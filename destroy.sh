#!/bin/bash

# =============================================================================
# Homeward Project Destroy Script
# =============================================================================
# This script removes all Google Cloud resources created by the setup script.
# It destroys resources in reverse order to ensure proper cleanup.
#
# Usage: ./destroy.sh --project-id PROJECT_ID --region REGION [--force]
# =============================================================================

set -e  # Exit on any error

# =============================================================================
# CONFIGURATION AND CONSTANTS
# =============================================================================

# Default values
PROJECT_ID=""
REGION=""
FORCE_DELETE=false

# Colors for output formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Print colored output messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Display usage information
show_usage() {
    echo "Usage: $0 --project-id PROJECT_ID --region REGION [--force]"
    echo ""
    echo "Parameters:"
    echo "  --project-id ID     Google Cloud Project ID"
    echo "  --region REGION     Google Cloud region (e.g., us-central1)"
    echo "  --force             Skip confirmation prompts"
    echo ""
    echo "Example:"
    echo "  $0 --project-id my-project-123 --region us-central1"
    echo "  $0 --project-id my-project-123 --region us-central1 --force"
}

# Validate required parameters
validate_parameters() {
    print_step "Validating Input Parameters"
    
    # Check if all required parameters are provided
    if [[ -z "$PROJECT_ID" ]]; then
        print_error "Missing required parameter: --project-id"
        show_usage
        exit 1
    fi
    
    if [[ -z "$REGION" ]]; then
        print_error "Missing required parameter: --region"
        show_usage
        exit 1
    fi
    
    print_success "All parameters validated successfully"
    print_info "Project ID: $PROJECT_ID"
    print_info "Region: $REGION"
    print_info "Force delete: $FORCE_DELETE"
}

# Check if required tools are installed
check_prerequisites() {
    print_step "Checking Prerequisites"
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install Google Cloud SDK first."
        exit 1
    fi
    
    # Check if gsutil is available
    if ! command -v gsutil &> /dev/null; then
        print_error "gsutil is not installed. Please install Google Cloud SDK first."
        exit 1
    fi
    
    # Check if bq is available
    if ! command -v bq &> /dev/null; then
        print_error "bq CLI is required but not installed."
        exit 1
    fi
    
    print_success "All prerequisites are available"
}

# Load environment variables from .env file
load_environment() {
    print_step "Loading Environment Variables"
    
    if [[ -f ".env" ]]; then
        print_info "Loading variables from .env file..."
        source .env
        
        if [[ -n "$HOMEWARD_VIDEO_BUCKET" ]]; then
            print_info "Found bucket: $HOMEWARD_VIDEO_BUCKET"
        fi
        
        if [[ -n "$HOMEWARD_BQ_CONNECTION" ]]; then
            print_info "Found BigQuery connection: $HOMEWARD_BQ_CONNECTION"
        fi
        
    else
        print_warning ".env file not found. Will attempt to discover resources."
    fi
}

# Authenticate with Google Cloud
authenticate_gcloud() {
    print_step "Authenticating with Google Cloud"
    
    # Set the project
    print_info "Setting active project to: $PROJECT_ID"
    if gcloud config set project "$PROJECT_ID"; then
        print_success "Project set successfully"
    else
        print_error "Failed to set project"
        exit 1
    fi
    
    # Verify authentication and project access
    print_info "Verifying project access..."
    if gcloud projects describe "$PROJECT_ID" > /dev/null 2>&1; then
        print_success "Project access verified"
    else
        print_error "Cannot access project $PROJECT_ID. Check project ID and authentication."
        exit 1
    fi
}

# Confirm destruction with user
confirm_destruction() {
    if [[ "$FORCE_DELETE" == true ]]; then
        print_warning "Force delete enabled - skipping confirmation"
        return 0
    fi
    
    print_step "Destruction Confirmation"
    print_warning "This will permanently delete the following resources:"
    
    if [[ -n "$HOMEWARD_VIDEO_BUCKET" ]]; then
        echo "  - Storage bucket: gs://$HOMEWARD_VIDEO_BUCKET (including all videos)"
    fi
    
    if [[ -n "$HOMEWARD_BQ_CONNECTION" ]]; then
        echo "  - BigQuery connection: $HOMEWARD_BQ_CONNECTION"
    else
        echo "  - BigQuery connection: homeward_gcp_connection"
    fi
    
    if [[ -n "$HOMEWARD_BQ_TABLE" ]]; then
        echo "  - BigQuery object table: $HOMEWARD_BQ_TABLE"
    else
        echo "  - BigQuery object table: video_objects"
    fi
    
    
    if [[ -n "$HOMEWARD_BQ_DATASET" ]]; then
        echo "  - BigQuery dataset: $HOMEWARD_BQ_DATASET"
    else
        echo "  - BigQuery dataset: homeward"
    fi
    
    echo "  - All uploaded videos and metadata"
    echo ""
    
    read -p "Are you sure you want to proceed? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "Destruction cancelled by user"
        exit 0
    fi
    
    print_warning "Last chance! Type 'DELETE' to confirm destruction:"
    read -p "> " -r
    if [[ "$REPLY" != "DELETE" ]]; then
        print_info "Destruction cancelled by user"
        exit 0
    fi
    
    print_success "Destruction confirmed"
}


# Delete storage bucket and all contents
delete_storage_bucket() {
    print_step "Deleting Storage Bucket"
    
    if [[ -z "$HOMEWARD_VIDEO_BUCKET" ]]; then
        print_warning "No bucket specified for deletion"
        return 0
    fi
    
    # Check if bucket exists
    if ! gsutil ls -b "gs://$HOMEWARD_VIDEO_BUCKET" > /dev/null 2>&1; then
        print_warning "Bucket does not exist: gs://$HOMEWARD_VIDEO_BUCKET"
        return 0
    fi
    
    # Count objects in bucket
    local object_count
    object_count=$(gsutil ls "gs://$HOMEWARD_VIDEO_BUCKET/**" 2>/dev/null | wc -l || echo "0")
    
    if [[ $object_count -gt 0 ]]; then
        print_info "Deleting $object_count objects from bucket..."
        if gsutil -m rm -r "gs://$HOMEWARD_VIDEO_BUCKET/**"; then
            print_success "All objects deleted from bucket"
        else
            print_error "Failed to delete objects from bucket"
            exit 1
        fi
    else
        print_info "Bucket is already empty"
    fi
    
    # Delete the bucket itself
    print_info "Deleting bucket: gs://$HOMEWARD_VIDEO_BUCKET"
    if gsutil rb "gs://$HOMEWARD_VIDEO_BUCKET"; then
        print_success "Storage bucket deleted successfully"
    else
        print_error "Failed to delete storage bucket"
        exit 1
    fi
}

# Delete BigQuery object table
delete_bigquery_object_table() {
    print_step "Deleting BigQuery Object Table"
    
    local table_name="${HOMEWARD_BQ_TABLE:-video_objects}"
    local dataset_id="${HOMEWARD_BQ_DATASET:-homeward}"
    
    # Check if table exists
    if ! bq show --project_id="$PROJECT_ID" "$dataset_id.$table_name" > /dev/null 2>&1; then
        print_warning "BigQuery object table does not exist: $dataset_id.$table_name"
        return 0
    fi
    
    print_info "Deleting BigQuery object table: $dataset_id.$table_name"
    if bq rm --project_id="$PROJECT_ID" "$dataset_id.$table_name"; then
        print_success "BigQuery object table deleted successfully"
    else
        print_error "Failed to delete BigQuery object table"
        exit 1
    fi
}


# Delete BigQuery dataset
delete_bigquery_dataset() {
    print_step "Deleting BigQuery Dataset"
    
    local dataset_id="${HOMEWARD_BQ_DATASET:-homeward}"
    
    # Check if dataset exists
    if ! bq show --dataset --project_id="$PROJECT_ID" "$dataset_id" > /dev/null 2>&1; then
        print_warning "BigQuery dataset does not exist: $dataset_id"
        return 0
    fi
    
    print_info "Deleting BigQuery dataset: $dataset_id"
    if bq rm -r -f --project_id="$PROJECT_ID" "$dataset_id"; then
        print_success "BigQuery dataset deleted successfully"
    else
        print_error "Failed to delete BigQuery dataset"
        exit 1
    fi
}

# Delete BigQuery connection
delete_bigquery_connection() {
    print_step "Deleting BigQuery Connection"
    
    local connection_id="${HOMEWARD_BQ_CONNECTION:-homeward_gcp_connection}"
    local connection_full_id="${PROJECT_ID}.${REGION}.${connection_id}"
    
    # Check if connection exists
    if ! bq show --connection --location="$REGION" --project_id="$PROJECT_ID" "$connection_id" > /dev/null 2>&1; then
        print_warning "BigQuery connection does not exist: $connection_id"
        return 0
    fi
    
    # Get connection details to retrieve the service account
    print_info "Retrieving service account for cleanup..."
    CONNECTION_DETAILS=$(bq show --format json --connection "$connection_full_id" 2>/dev/null)
    
    if [[ $? -eq 0 ]] && echo "$CONNECTION_DETAILS" | jq . > /dev/null 2>&1; then
        SERVICE_ACCOUNT=$(echo "$CONNECTION_DETAILS" | jq -r '.cloudResource.serviceAccountId')
        
        if [[ "$SERVICE_ACCOUNT" != "null" && -n "$SERVICE_ACCOUNT" ]]; then
            print_info "Removing Vertex AI IAM policy binding for service account..."
            gcloud projects remove-iam-policy-binding "$PROJECT_ID" \
                --member="serviceAccount:$SERVICE_ACCOUNT" \
                --role="roles/aiplatform.user" 2>/dev/null || true
            print_info "IAM policy binding cleanup attempted"
        fi
    fi
    
    print_info "Deleting BigQuery connection: $connection_id"
    if bq rm --connection --location="$REGION" --project_id="$PROJECT_ID" "$connection_id"; then
        print_success "BigQuery connection deleted successfully"
    else
        print_error "Failed to delete BigQuery connection"
        exit 1
    fi
}

# Clean up environment file
cleanup_environment() {
    print_step "Cleaning Up Environment"
    
    if [[ -f ".env" ]]; then
        print_info "Removing environment variables from .env file..."
        
        # Remove Homeward-specific variables
        if command -v sed &> /dev/null; then
            # macOS compatible sed
            sed -i '' '/^HOMEWARD_VIDEO_BUCKET=/d' .env 2>/dev/null || true
            sed -i '' '/^HOMEWARD_BQ_CONNECTION=/d' .env 2>/dev/null || true
            sed -i '' '/^HOMEWARD_BQ_DATASET=/d' .env 2>/dev/null || true
            sed -i '' '/^HOMEWARD_BQ_TABLE=/d' .env 2>/dev/null || true
        else
            # GNU sed
            sed -i '/^HOMEWARD_VIDEO_BUCKET=/d' .env 2>/dev/null || true
            sed -i '/^HOMEWARD_BQ_CONNECTION=/d' .env 2>/dev/null || true
            sed -i '/^HOMEWARD_BQ_DATASET=/d' .env 2>/dev/null || true
            sed -i '/^HOMEWARD_BQ_TABLE=/d' .env 2>/dev/null || true
        fi
        
        # Remove .env file if it's empty
        if [[ ! -s ".env" ]]; then
            rm -f .env
            print_info "Empty .env file removed"
        fi
        
        print_success "Environment cleanup completed"
    else
        print_info "No .env file to clean up"
    fi
}

# =============================================================================
# MAIN SCRIPT EXECUTION
# =============================================================================

main() {
    print_info "Starting Homeward Project Destruction"
    print_info "Script version: 1.0.0"
    echo ""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --project-id)
                PROJECT_ID="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
                ;;
            --force)
                FORCE_DELETE=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown parameter: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Execute destruction steps in reverse order
    validate_parameters
    check_prerequisites
    load_environment
    authenticate_gcloud
    confirm_destruction
    
    # Destroy resources in reverse order of creation
    delete_bigquery_object_table
    delete_bigquery_dataset
    delete_bigquery_connection
    delete_storage_bucket
    cleanup_environment
    
    print_step "Destruction Complete"
    print_success "All Homeward project resources have been destroyed!"
    print_info "Project ID: $PROJECT_ID"
    print_info "Region: $REGION"
    echo ""
    print_warning "Note: This script does not modify gcloud authentication or project settings."
    print_info "Your gcloud CLI configuration remains unchanged."
}

# Execute main function with all arguments
main "$@"