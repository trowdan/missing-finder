#!/bin/bash

# =============================================================================
# Homeward Project Setup Script
# =============================================================================
# This script initializes the Google Cloud environment for the Homeward
# missing persons finder application. It creates necessary cloud resources,
# configures environment variables, and prepares the system for operation.
#
# Usage: ./setup.sh --input /path/to/video-resources-config-file.json --project-id PROJECT_ID --region REGION
# =============================================================================

set -e  # Exit on any error

# =============================================================================
# CONFIGURATION AND CONSTANTS
# =============================================================================

# Default values
INPUT_JSON=""
PROJECT_ID=""
REGION=""

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
    echo "Usage: $0 --input /path/to/video-resources-config-file.json --project-id PROJECT_ID --region REGION"
    echo ""
    echo "Parameters:"
    echo "  --input PATH        Path to a JSON file containing details about the recordings to download"
    echo "  --project-id ID     Google Cloud Project ID"
    echo "  --region REGION     Google Cloud region (e.g., us-central1)"
    echo ""
    echo "Example:"
    echo "  $0 --input ./videos.json --project-id my-project-123 --region us-central1"
}

# Generate random 8-character string for bucket suffix (macOS compatible)
generate_random_suffix() {
    # Use openssl for cross-platform compatibility
    if command -v openssl &> /dev/null; then
        openssl rand -hex 4 | tr 'A-F' 'a-f'
    else
        # Fallback using date and random for macOS compatibility
        date +%s | sha256sum 2>/dev/null | cut -c1-8 || date +%s | shasum -a 256 | cut -c1-8
    fi
}

# Validate required parameters
validate_parameters() {
    print_step "Validating Input Parameters"
    
    # Check if all required parameters are provided
    if [[ -z "$INPUT_JSON" ]]; then
        print_error "Missing required parameter: --input"
        show_usage
        exit 1
    fi
    
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
    
    # Validate JSON file exists and is readable
    if [[ ! -f "$INPUT_JSON" ]]; then
        print_error "JSON file not found: $INPUT_JSON"
        exit 1
    fi
    
    if [[ ! -r "$INPUT_JSON" ]]; then
        print_error "JSON file is not readable: $INPUT_JSON"
        exit 1
    fi
    
    # Validate JSON file format
    if ! python3 -m json.tool "$INPUT_JSON" > /dev/null 2>&1; then
        print_error "Invalid JSON format in file: $INPUT_JSON"
        exit 1
    fi
    
    print_success "All parameters validated successfully"
    print_info "Input JSON: $INPUT_JSON"
    print_info "Project ID: $PROJECT_ID"
    print_info "Region: $REGION"
}

# Check if required tools are installed
check_prerequisites() {
    print_step "Checking Prerequisites"
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install Google Cloud SDK first."
        print_info "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # Check if gsutil is available (part of gcloud)
    if ! command -v gsutil &> /dev/null; then
        print_error "gsutil is not installed. Please install Google Cloud SDK first."
        exit 1
    fi
    
    # Check if python3 is available (for JSON validation)
    if ! command -v python3 &> /dev/null; then
        print_error "python3 is required but not installed."
        exit 1
    fi
    
    # Check if curl is available (for downloading videos)
    if ! command -v curl &> /dev/null; then
        print_error "curl is required but not installed."
        exit 1
    fi
    
    # Check if jq is available (for JSON parsing)
    if ! command -v jq &> /dev/null; then
        print_error "jq is required for JSON parsing but not installed."
        print_info "Install with: brew install jq (macOS) or apt-get install jq (Ubuntu)"
        exit 1
    fi
    
    # Check if bq is available (for BigQuery operations)
    if ! command -v bq &> /dev/null; then
        print_error "bq CLI is required but not installed."
        print_info "Install with: gcloud components install bq"
        exit 1
    fi
    
    print_success "All prerequisites are available"
}

# Authenticate with Google Cloud using service account
authenticate_gcloud() {
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
        print_error "Cannot access project $PROJECT_ID. Check project ID and service account permissions."
        exit 1
    fi
}

# Create Google Cloud Storage bucket for video ingestion
create_storage_bucket() {
    print_step "Creating Google Cloud Storage Bucket"
    
    # Generate random suffix for bucket name
    RANDOM_SUFFIX=$(generate_random_suffix)
    BUCKET_NAME="homeward_videos_${RANDOM_SUFFIX}"
    
    print_info "Generated bucket name: $BUCKET_NAME"
    
    # Check if bucket name is available
    print_info "Checking bucket name availability..."
    if gsutil ls -b "gs://$BUCKET_NAME" > /dev/null 2>&1; then
        print_warning "Bucket name already exists, generating new suffix..."
        RANDOM_SUFFIX=$(generate_random_suffix)
        BUCKET_NAME="homeward_videos_${RANDOM_SUFFIX}"
        print_info "New bucket name: $BUCKET_NAME"
    fi
    
    # Create the bucket
    print_info "Creating private storage bucket in region: $REGION"
    if gsutil mb -p "$PROJECT_ID" -c STANDARD -l "$REGION" "gs://$BUCKET_NAME"; then
        print_success "Storage bucket created successfully: gs://$BUCKET_NAME"
    else
        print_error "Failed to create storage bucket"
        exit 1
    fi
    
    # Set bucket to private (remove public access)
    print_info "Configuring bucket permissions (private access only)..."
    if gsutil iam ch -d allUsers:objectViewer "gs://$BUCKET_NAME" 2>/dev/null || true; then
        print_info "Removed public access (if it existed)"
    fi
    
    if gsutil iam ch -d allAuthenticatedUsers:objectViewer "gs://$BUCKET_NAME" 2>/dev/null || true; then
        print_info "Removed authenticated users access (if it existed)"
    fi
    
    # Verify bucket is private
    if gsutil iam get "gs://$BUCKET_NAME" | grep -q "allUsers\|allAuthenticatedUsers"; then
        print_warning "Bucket may still have public access. Please review permissions manually."
    else
        print_success "Bucket is configured as private"
    fi
    
    # Store bucket name for later use
    export HOMEWARD_VIDEO_BUCKET="$BUCKET_NAME"
    echo "HOMEWARD_VIDEO_BUCKET=$BUCKET_NAME" >> .env
    print_info "Bucket name saved to environment: HOMEWARD_VIDEO_BUCKET"
}

# Create BigQuery connection for object tables
create_bigquery_connection() {
    print_step "Creating BigQuery Connection"
    
    # Use fixed connection name
    CONNECTION_ID="homeward_gcp_connection"
    
    print_info "Creating BigQuery connection: $CONNECTION_ID"
    
    # Create the BigQuery connection
    if bq mk --connection --location="$REGION" --project_id="$PROJECT_ID" \
        --connection_type=CLOUD_RESOURCE "$CONNECTION_ID"; then
        print_success "BigQuery connection created successfully: $CONNECTION_ID"
    else
        # Check if connection already exists
        if bq show --connection --location="$REGION" --project_id="$PROJECT_ID" "$CONNECTION_ID" > /dev/null 2>&1; then
            print_warning "BigQuery connection already exists: $CONNECTION_ID"
        else
            print_error "Failed to create BigQuery connection"
            exit 1
        fi
    fi
    
    # Get the service account associated with the connection
    print_info "Retrieving service account for BigQuery connection..."
    CONNECTION_FULL_ID="${PROJECT_ID}.${REGION}.${CONNECTION_ID}"
    
    # Get connection details with error handling
    print_info "Getting connection details for: $CONNECTION_FULL_ID"
    CONNECTION_DETAILS=$(bq show --format json --connection "$CONNECTION_FULL_ID" 2>&1)
    
    if [[ $? -ne 0 ]]; then
        print_error "Failed to retrieve connection details:"
        print_error "$CONNECTION_DETAILS"
        exit 1
    fi
    
    # Check if the output is valid JSON
    if ! echo "$CONNECTION_DETAILS" | jq . > /dev/null 2>&1; then
        print_error "Invalid JSON response from bq show command:"
        print_error "$CONNECTION_DETAILS"
        exit 1
    fi
    
    # Extract service account ID
    SERVICE_ACCOUNT=$(echo "$CONNECTION_DETAILS" | jq -r '.cloudResource.serviceAccountId')
    
    if [[ "$SERVICE_ACCOUNT" == "null" || -z "$SERVICE_ACCOUNT" ]]; then
        print_error "Failed to retrieve service account for BigQuery connection"
        print_error "Connection details: $CONNECTION_DETAILS"
        exit 1
    fi
    
    print_success "Retrieved service account: $SERVICE_ACCOUNT"
    
    # Grant the service account access to the storage bucket
    print_info "Granting storage.objectViewer role to service account..."
    if gcloud storage buckets add-iam-policy-binding "gs://$HOMEWARD_VIDEO_BUCKET" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/storage.objectViewer"; then
        print_success "IAM policy binding added successfully"
    else
        print_error "Failed to add IAM policy binding"
        exit 1
    fi
    
    # Store connection ID for later use
    export HOMEWARD_BQ_CONNECTION="$CONNECTION_ID"
    echo "HOMEWARD_BQ_CONNECTION=$CONNECTION_ID" >> .env
    print_info "Connection ID saved to environment: HOMEWARD_BQ_CONNECTION"
}

# Create BigQuery dataset
create_bigquery_dataset() {
    print_step "Creating BigQuery Dataset"
    
    DATASET_ID="homeward"
    
    print_info "Creating BigQuery dataset: $DATASET_ID"
    
    # Create the dataset
    if bq mk --dataset --location="$REGION" --project_id="$PROJECT_ID" "$DATASET_ID"; then
        print_success "BigQuery dataset created successfully: $DATASET_ID"
    else
        # Check if dataset already exists
        if bq show --dataset --project_id="$PROJECT_ID" "$DATASET_ID" > /dev/null 2>&1; then
            print_warning "BigQuery dataset already exists: $DATASET_ID"
        else
            print_error "Failed to create BigQuery dataset"
            exit 1
        fi
    fi
    
    # Store dataset ID for later use
    export HOMEWARD_BQ_DATASET="$DATASET_ID"
    echo "HOMEWARD_BQ_DATASET=$DATASET_ID" >> .env
    print_info "Dataset ID saved to environment: HOMEWARD_BQ_DATASET"
}

# Create BigQuery object table
create_bigquery_object_table() {
    print_step "Creating BigQuery Object Table"
    
    TABLE_NAME="video_objects"
    CONNECTION_ID="${HOMEWARD_BQ_CONNECTION}"
    DATASET_ID="${HOMEWARD_BQ_DATASET}"
    BUCKET_PATH="gs://${HOMEWARD_VIDEO_BUCKET}"
    
    print_info "Creating BigQuery object table: $TABLE_NAME"
    print_info "Using bucket path: $BUCKET_PATH/*.mp4"
    print_info "Using connection: $REGION.$CONNECTION_ID"
    
    # Create the object table
    if bq mk --table \
        --external_table_definition="$BUCKET_PATH/*.mp4@$REGION.$CONNECTION_ID" \
        --object_metadata=SIMPLE \
        --max_staleness="0-0 1 0:0:0" \
        --metadata_cache_mode=AUTOMATIC \
        "$PROJECT_ID:$DATASET_ID.$TABLE_NAME"; then
        print_success "BigQuery object table created successfully: $TABLE_NAME"
    else
        print_error "Failed to create BigQuery object table"
        exit 1
    fi
    
    # Store table name for later use
    export HOMEWARD_BQ_TABLE="$TABLE_NAME"
    echo "HOMEWARD_BQ_TABLE=$TABLE_NAME" >> .env
    print_info "Table name saved to environment: HOMEWARD_BQ_TABLE"
}

# Parse JSON configuration and extract video metadata
parse_video_config() {
    print_step "Parsing Video Configuration"
    
    # Validate JSON structure
    if ! jq -e '.videos' "$INPUT_JSON" > /dev/null 2>&1; then
        print_error "Invalid JSON structure: missing 'videos' array"
        exit 1
    fi
    
    # Count videos in configuration
    VIDEO_COUNT=$(jq '.videos | length' "$INPUT_JSON")
    print_info "Found $VIDEO_COUNT videos to process"
    
    # Validate required fields for each video
    local missing_fields=()
    for i in $(seq 0 $((VIDEO_COUNT-1))); do
        local video_id=$(jq -r ".videos[$i].id" "$INPUT_JSON")
        
        # Check required fields
        for field in "download_url" "camera_id" "timestamp" "latitude" "longitude" "camera_type" "resolution" "mime_type"; do
            if [[ $(jq -r ".videos[$i].$field" "$INPUT_JSON") == "null" ]]; then
                missing_fields+=("Video $video_id: missing $field")
            fi
        done
    done
    
    if [[ ${#missing_fields[@]} -gt 0 ]]; then
        print_error "Configuration validation failed:"
        for field in "${missing_fields[@]}"; do
            print_error "  - $field"
        done
        exit 1
    fi
    
    print_success "Video configuration validated successfully"
}

# Download and upload videos to GCS
process_videos() {
    print_step "Processing and Uploading Videos"
    
    # Create temporary directory for downloads
    TEMP_DIR=$(mktemp -d)
    print_info "Using temporary directory: $TEMP_DIR"
    
    # Ensure cleanup on exit
    trap "rm -rf $TEMP_DIR" EXIT
    
    local success_count=0
    local failure_count=0
    
    for i in $(seq 0 $((VIDEO_COUNT-1))); do
        # Extract video metadata
        local video_id=$(jq -r ".videos[$i].id" "$INPUT_JSON")
        local download_url=$(jq -r ".videos[$i].download_url" "$INPUT_JSON")
        local camera_id=$(jq -r ".videos[$i].camera_id" "$INPUT_JSON")
        local timestamp=$(jq -r ".videos[$i].timestamp" "$INPUT_JSON")
        local latitude=$(jq -r ".videos[$i].latitude" "$INPUT_JSON")
        local longitude=$(jq -r ".videos[$i].longitude" "$INPUT_JSON")
        local camera_type=$(jq -r ".videos[$i].camera_type" "$INPUT_JSON")
        local resolution=$(jq -r ".videos[$i].resolution" "$INPUT_JSON")
        local mime_type=$(jq -r ".videos[$i].mime_type" "$INPUT_JSON")
        
        # Generate filename according to Homeward naming convention
        local filename="${camera_id}_${timestamp}_${latitude}_${longitude}_${camera_type}_${resolution}.mp4"
        local temp_file="$TEMP_DIR/$filename"
        
        print_info "Processing video $((i+1))/$VIDEO_COUNT: $video_id"
        print_info "  Filename: $filename"
        
        # Download video file
        print_info "  Downloading from: $download_url"
        if curl -L -f -o "$temp_file" "$download_url" --connect-timeout 30 --max-time 300; then
            print_success "  Download completed: $(du -h "$temp_file" | cut -f1)"
        else
            print_error "  Failed to download video: $video_id"
            ((failure_count++))
            continue
        fi
        
        
        # Upload video to GCS with proper content type and custom metadata
        print_info "  Uploading video to GCS with metadata..."
        if gsutil -h "Content-Type:$mime_type" \
                  -h "x-goog-meta-video-id:$video_id" \
                  -h "x-goog-meta-camera-id:$camera_id" \
                  -h "x-goog-meta-timestamp:$timestamp" \
                  -h "x-goog-meta-latitude:$latitude" \
                  -h "x-goog-meta-longitude:$longitude" \
                  -h "x-goog-meta-camera-type:$camera_type" \
                  -h "x-goog-meta-resolution:$resolution" \
                  -h "x-goog-meta-upload-date:$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
                  -h "x-goog-meta-processed-by:homeward-setup-script" \
                  -h "x-goog-meta-source-dataset:$(jq -r '.metadata.dataset' "$INPUT_JSON")" \
                  cp "$temp_file" "gs://$HOMEWARD_VIDEO_BUCKET/$filename"; then
            print_success "  Video uploaded successfully with metadata"
        else
            print_error "  Failed to upload video: $filename"
            ((failure_count++))
            continue
        fi
        
        
        # Clean up temporary files
        rm -f "$temp_file"
        
        ((success_count++))
        print_success "  Video $video_id processed successfully ($success_count/$VIDEO_COUNT completed)"
        echo ""
    done
    
    print_step "Video Processing Summary"
    print_success "Successfully processed: $success_count videos"
    if [[ $failure_count -gt 0 ]]; then
        print_warning "Failed to process: $failure_count videos"
    fi
    
    if [[ $success_count -eq 0 ]]; then
        print_error "No videos were successfully processed"
        exit 1
    fi
}


# =============================================================================
# MAIN SCRIPT EXECUTION
# =============================================================================

main() {
    print_info "Starting Homeward Project Setup"
    print_info "Script version: 1.0.0"
    echo ""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --input)
                INPUT_JSON="$2"
                shift 2
                ;;
            --project-id)
                PROJECT_ID="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
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
    
    # Execute setup steps
    validate_parameters
    check_prerequisites
    authenticate_gcloud
    create_storage_bucket
    create_bigquery_connection
    create_bigquery_dataset
    parse_video_config
    process_videos
    create_bigquery_object_table
    
    print_step "Setup Complete"
    print_success "Homeward project setup completed successfully!"
    print_info "Video ingestion bucket: gs://$HOMEWARD_VIDEO_BUCKET"
    print_info "BigQuery connection: $HOMEWARD_BQ_CONNECTION"
    print_info "BigQuery dataset: $HOMEWARD_BQ_DATASET"
    print_info "BigQuery object table: $HOMEWARD_BQ_TABLE"
    print_info "Project ID: $PROJECT_ID"
    print_info "Region: $REGION"
    print_info "Videos processed: $VIDEO_COUNT"
    echo ""
    print_info "Next steps:"
    print_info "1. Verify uploaded videos in GCS: gs://$HOMEWARD_VIDEO_BUCKET"
    print_info "2. Set up BigQuery tables and external data sources"
    print_info "3. Configure Eventarc triggers for video processing"
    print_info "4. Initialize AI/ML pipelines for person detection"
}

# Execute main function with all arguments
main "$@"