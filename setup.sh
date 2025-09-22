#!/bin/bash

# =============================================================================
# Homeward Project Setup Script
# =============================================================================
# This script initializes the Google Cloud environment for the Homeward
# missing persons finder application. It creates necessary cloud resources,
# configures environment variables, and prepares the system for operation.
#
# Usage: ./setup.sh --demo-folder /path/to/demo-folder --project-id PROJECT_ID --region REGION
# =============================================================================

set -e  # Exit on any error

# =============================================================================
# CONFIGURATION AND CONSTANTS
# =============================================================================

# Default values
DEMO_FOLDER=""
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
    echo "Usage: $0 --demo-folder /path/to/demo-folder --project-id PROJECT_ID --region REGION"
    echo ""
    echo "Parameters:"
    echo "  --demo-folder PATH  Path to the root demo folder containing videos, reports, and sql subfolders"
    echo "  --project-id ID     Google Cloud Project ID"
    echo "  --region REGION     Google Cloud region (e.g., us-central1)"
    echo ""
    echo "Example:"
    echo "  $0 --demo-folder ./demo --project-id my-project-123 --region us-central1"
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
    
    # Demo folder is optional - if not provided, only core infrastructure is set up
    if [[ -z "$DEMO_FOLDER" ]]; then
        print_info "No demo folder specified - will set up core infrastructure only"
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
    
    # Validate demo folder exists and is readable (only if specified)
    if [[ -n "$DEMO_FOLDER" ]]; then
        if [[ ! -d "$DEMO_FOLDER" ]]; then
            print_error "Demo folder not found: $DEMO_FOLDER"
            exit 1
        fi
        
        if [[ ! -r "$DEMO_FOLDER" ]]; then
            print_error "Demo folder is not readable: $DEMO_FOLDER"
            exit 1
        fi
    fi
    
    print_success "All parameters validated successfully"
    if [[ -n "$DEMO_FOLDER" ]]; then
        print_info "Demo folder: $DEMO_FOLDER"
    else
        print_info "Demo folder: Not specified (core setup only)"
    fi
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
    
    # jq is no longer required - using bash for CSV parsing
    
    # Check if bq is available (for BigQuery operations)
    if ! command -v bq &> /dev/null; then
        print_error "bq CLI is required but not installed."
        print_info "Install with: gcloud components install bq"
        exit 1
    fi
    
    print_success "All prerequisites are available"
}

# Load existing environment variables if available
load_existing_environment() {
    print_step "Loading Existing Environment"
    
    if [[ -f ".env" ]]; then
        print_info "Loading existing environment from .env file..."
        source .env
        
        if [[ -n "$HOMEWARD_VIDEO_BUCKET" ]]; then
            print_info "Found existing bucket: $HOMEWARD_VIDEO_BUCKET"
        fi
        
        if [[ -n "$HOMEWARD_BQ_CONNECTION" ]]; then
            print_info "Found existing BigQuery connection: $HOMEWARD_BQ_CONNECTION"
        fi
        
        if [[ -n "$HOMEWARD_BQ_DATASET" ]]; then
            print_info "Found existing BigQuery dataset: $HOMEWARD_BQ_DATASET"
        fi
        
        if [[ -n "$HOMEWARD_BQ_TABLE" ]]; then
            print_info "Found existing BigQuery table: $HOMEWARD_BQ_TABLE"
        fi
        
        print_success "Existing environment loaded"
    else
        print_info "No existing .env file found - fresh installation"
    fi
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
    
    # Check if bucket already exists from environment
    if [[ -n "$HOMEWARD_VIDEO_BUCKET" ]]; then
        print_info "Checking existing bucket: $HOMEWARD_VIDEO_BUCKET"
        if gsutil ls -b "gs://$HOMEWARD_VIDEO_BUCKET" > /dev/null 2>&1; then
            print_success "Using existing bucket: gs://$HOMEWARD_VIDEO_BUCKET"
            BUCKET_NAME="$HOMEWARD_VIDEO_BUCKET"
            export HOMEWARD_VIDEO_BUCKET="$BUCKET_NAME"
            return 0
        else
            print_warning "Configured bucket no longer exists, creating new one..."
        fi
    fi
    
    # Generate random suffix for bucket name
    RANDOM_SUFFIX=$(generate_random_suffix)
    BUCKET_NAME="homeward_videos_${RANDOM_SUFFIX}"
    
    print_info "Generated bucket name: $BUCKET_NAME"
    
    # Check if bucket name is available
    print_info "Checking bucket name availability..."
    while gsutil ls -b "gs://$BUCKET_NAME" > /dev/null 2>&1; do
        print_warning "Bucket name already exists, generating new suffix..."
        RANDOM_SUFFIX=$(generate_random_suffix)
        BUCKET_NAME="homeward_videos_${RANDOM_SUFFIX}"
        print_info "New bucket name: $BUCKET_NAME"
    done
    
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
    if ! grep -q "^HOMEWARD_VIDEO_BUCKET=" .env 2>/dev/null; then
        echo "HOMEWARD_VIDEO_BUCKET=$BUCKET_NAME" >> .env
    fi
    print_info "Bucket name saved to environment: HOMEWARD_VIDEO_BUCKET"
}

# Create BigQuery connection for object tables
create_bigquery_connection() {
    print_step "Creating BigQuery Connection"
    
    # Check if connection already exists from environment
    if [[ -n "$HOMEWARD_BQ_CONNECTION" ]]; then
        CONNECTION_ID="$HOMEWARD_BQ_CONNECTION"
        print_info "Checking existing BigQuery connection: $CONNECTION_ID"
        if bq show --connection --location="$REGION" --project_id="$PROJECT_ID" "$CONNECTION_ID" > /dev/null 2>&1; then
            print_success "Using existing BigQuery connection: $CONNECTION_ID"
        else
            print_warning "Configured connection no longer exists, creating new one..."
            CONNECTION_ID="homeward_gcp_connection"
        fi
    else
        # Use fixed connection name
        CONNECTION_ID="homeward_gcp_connection"
    fi
    
    print_info "Creating BigQuery connection: $CONNECTION_ID"
    
    # Create the BigQuery connection
    if bq mk --connection --location="$REGION" --project_id="$PROJECT_ID" \
        --connection_type=CLOUD_RESOURCE "$CONNECTION_ID"; then
        print_success "BigQuery connection created successfully: $CONNECTION_ID"
    else
        # Check if connection already exists
        if bq show --connection --location="$REGION" --project_id="$PROJECT_ID" "$CONNECTION_ID" > /dev/null 2>&1; then
            print_success "Using existing BigQuery connection: $CONNECTION_ID"
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
        print_success "Storage IAM policy binding added successfully"
    else
        print_error "Failed to add storage IAM policy binding"
        exit 1
    fi
    
    # Grant the service account Vertex AI User role for remote model access
    print_info "Granting aiplatform.user role to service account..."
    if gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/aiplatform.user"; then
        print_success "Vertex AI IAM policy binding added successfully"
        print_info "Waiting for IAM policy propagation (30 seconds)..."
        sleep 30
        print_success "IAM policy propagation completed"
    else
        print_error "Failed to add Vertex AI IAM policy binding"
        exit 1
    fi
    
    # Store connection ID for later use
    export HOMEWARD_BQ_CONNECTION="$CONNECTION_ID"
    if ! grep -q "^HOMEWARD_BQ_CONNECTION=" .env 2>/dev/null; then
        echo "HOMEWARD_BQ_CONNECTION=$CONNECTION_ID" >> .env
    fi
    print_info "Connection ID saved to environment: HOMEWARD_BQ_CONNECTION"
}

# Enable required Google Cloud APIs
enable_required_apis() {
    print_step "Enabling Required APIs"
    
    # APIs required for Homeward project
    local required_apis=(
        "aiplatform.googleapis.com"    # Vertex AI API (required for remote models)
        "bigquery.googleapis.com"      # BigQuery API
        "storage.googleapis.com"       # Cloud Storage API
        "geocoding-backend.googleapis.com"  # Geocoding API (for address to coordinates conversion)
    )
    
    for api in "${required_apis[@]}"; do
        print_info "Enabling API: $api"
        if gcloud services enable "$api" --project="$PROJECT_ID"; then
            print_success "API enabled successfully: $api"
        else
            print_error "Failed to enable API: $api"
            exit 1
        fi
    done
    
    print_info "Waiting for API propagation (30 seconds)..."
    sleep 30
    print_success "All required APIs have been enabled"
}

# Create BigQuery dataset
create_bigquery_dataset() {
    print_step "Creating BigQuery Dataset"
    
    # Check if dataset already exists from environment
    if [[ -n "$HOMEWARD_BQ_DATASET" ]]; then
        DATASET_ID="$HOMEWARD_BQ_DATASET"
        print_info "Checking existing BigQuery dataset: $DATASET_ID"
        if bq show --dataset --project_id="$PROJECT_ID" "$DATASET_ID" > /dev/null 2>&1; then
            print_success "Using existing BigQuery dataset: $DATASET_ID"
            export HOMEWARD_BQ_DATASET="$DATASET_ID"
            return 0
        else
            print_warning "Configured dataset no longer exists, creating new one..."
        fi
    fi
    
    DATASET_ID="homeward"
    
    print_info "Creating BigQuery dataset: $DATASET_ID"
    
    # Create the dataset
    if bq mk --dataset --location="$REGION" --project_id="$PROJECT_ID" "$DATASET_ID"; then
        print_success "BigQuery dataset created successfully: $DATASET_ID"
    else
        # Check if dataset already exists
        if bq show --dataset --project_id="$PROJECT_ID" "$DATASET_ID" > /dev/null 2>&1; then
            print_success "Using existing BigQuery dataset: $DATASET_ID"
        else
            print_error "Failed to create BigQuery dataset"
            exit 1
        fi
    fi
    
    # Store dataset ID for later use
    export HOMEWARD_BQ_DATASET="$DATASET_ID"
    if ! grep -q "^HOMEWARD_BQ_DATASET=" .env 2>/dev/null; then
        echo "HOMEWARD_BQ_DATASET=$DATASET_ID" >> .env
    fi
    print_info "Dataset ID saved to environment: HOMEWARD_BQ_DATASET"
}

# Create service account for video downloads
create_video_downloader_service_account() {
    print_step "Creating Video Downloader Service Account"

    local service_account_name="video-downloader-sa"
    local service_account_display_name="Video Downloader Service Account"
    local service_account_description="Service account for downloading video files from GCS"

    # Check if service account already exists
    if gcloud iam service-accounts describe "${service_account_name}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --project="$PROJECT_ID" > /dev/null 2>&1; then
        print_success "Using existing service account: ${service_account_name}@${PROJECT_ID}.iam.gserviceaccount.com"
    else
        # Create the service account
        print_info "Creating service account: $service_account_display_name"
        if gcloud iam service-accounts create "$service_account_name" \
            --project="$PROJECT_ID" \
            --display-name="$service_account_display_name" \
            --description="$service_account_description"; then
            print_success "Service account created successfully: ${service_account_name}@${PROJECT_ID}.iam.gserviceaccount.com"
            print_info "Waiting for service account propagation (30 seconds)..."
            sleep 30
        else
            print_error "Failed to create service account"
            exit 1
        fi
    fi

    # Grant storage.objectViewer role to the service account
    print_info "Granting storage.objectViewer role to service account..."
    if gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${service_account_name}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/storage.objectViewer"; then
        print_success "Storage object viewer role granted successfully"
    else
        print_error "Failed to grant storage object viewer role"
        exit 1
    fi

    # Create downloads directory if it doesn't exist
    if [[ ! -d "downloads" ]]; then
        print_info "Creating downloads directory..."
        mkdir -p downloads
        print_success "Downloads directory created"
    fi

    # Generate and download private key
    local key_file="downloads/key.json"
    print_info "Generating private key for service account..."

    # Remove existing key file if it exists
    if [[ -f "$key_file" ]]; then
        print_warning "Existing key file found, backing up to ${key_file}.bak"
        mv "$key_file" "${key_file}.bak"
    fi

    if gcloud iam service-accounts keys create "$key_file" \
        --iam-account="${service_account_name}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --project="$PROJECT_ID"; then
        print_success "Private key generated and saved to: $key_file"

        # Set restrictive permissions on the key file
        chmod 600 "$key_file"
        print_info "Key file permissions set to 600 (owner read/write only)"

        # Store the key path in environment
        export HOMEWARD_SERVICE_ACCOUNT_KEY_PATH="$key_file"
        if ! grep -q "^HOMEWARD_SERVICE_ACCOUNT_KEY_PATH=" .env 2>/dev/null; then
            echo "HOMEWARD_SERVICE_ACCOUNT_KEY_PATH=$key_file" >> .env
        fi
        print_info "Service account key path saved to environment"

    else
        print_error "Failed to generate private key"
        exit 1
    fi

    print_success "Video downloader service account setup completed"
}

# Create and configure geocoding API key
create_geocoding_api_key() {
    print_step "Creating Geocoding API Key"

    # Check if API key already exists from environment
    if [[ -n "$HOMEWARD_GEOCODING_API_KEY" ]]; then
        print_info "Geocoding API key already configured"
        return 0
    fi

    local api_key_name="homeward-geocoding-key"
    local api_key_display_name="Homeward Geocoding API Key"

    print_info "Creating geocoding API key: $api_key_display_name"

    # Create the API key
    local create_output
    if create_output=$(gcloud services api-keys create \
        --project="$PROJECT_ID" \
        --display-name="$api_key_display_name" \
        --format="json" 2>&1); then

        # Extract the key name and key value directly from the creation response
        local key_name=$(echo "$create_output" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
        local api_key_value=$(echo "$create_output" | grep -o '"keyString":"[^"]*"' | cut -d'"' -f4)

        if [[ -z "$key_name" || -z "$api_key_value" ]]; then
            print_error "Failed to parse API key creation response"
            print_error "Raw output: $create_output"
            exit 1
        fi

        print_success "API key created: $key_name"
        print_success "API key value extracted from creation response"

        # Extract just the key ID from the full resource name for restrictions
        local key_id=$(basename "$key_name")

        # Apply API restrictions to limit the key to geocoding service only
        print_info "Applying API restrictions to limit key to geocoding service..."
        if gcloud services api-keys update "$key_id" \
            --project="$PROJECT_ID" \
            --api-target=service=geocoding-backend.googleapis.com > /dev/null 2>&1; then
            print_success "API key restricted to geocoding service"
        else
            print_warning "Failed to apply API restrictions - key will work but is less secure"
        fi

        # Store the API key
        export HOMEWARD_GEOCODING_API_KEY="$api_key_value"
        if ! grep -q "^HOMEWARD_GEOCODING_API_KEY=" .env 2>/dev/null; then
            echo "HOMEWARD_GEOCODING_API_KEY=$api_key_value" >> .env
        fi
        print_success "Geocoding API key saved to environment"

    else
        # Check if key already exists with this display name
        print_info "Checking for existing geocoding API key..."
        local existing_keys
        if existing_keys=$(gcloud services api-keys list \
            --project="$PROJECT_ID" \
            --filter="displayName:$api_key_display_name" \
            --format="value(name)" 2>/dev/null); then

            if [[ -n "$existing_keys" ]]; then
                local existing_key=$(echo "$existing_keys" | head -n1)
                print_success "Using existing geocoding API key: $existing_key"

                # Get the existing API key value
                local existing_api_key_value
                if existing_api_key_value=$(gcloud services api-keys get-key-string "$existing_key" --format="value(keyString)" 2>&1); then
                    export HOMEWARD_GEOCODING_API_KEY="$existing_api_key_value"
                    if ! grep -q "^HOMEWARD_GEOCODING_API_KEY=" .env 2>/dev/null; then
                        echo "HOMEWARD_GEOCODING_API_KEY=$existing_api_key_value" >> .env
                    fi
                    print_success "Existing geocoding API key configured"
                else
                    print_error "Failed to retrieve existing API key value"
                    exit 1
                fi
            else
                print_error "Failed to create geocoding API key: $create_output"
                exit 1
            fi
        else
            print_error "Failed to create or find geocoding API key"
            exit 1
        fi
    fi
}


# Create BigQuery object table
create_bigquery_object_table() {
    print_step "Creating BigQuery Object Table"
    
    # Check if table already exists from environment
    if [[ -n "$HOMEWARD_BQ_TABLE" ]]; then
        TABLE_NAME="$HOMEWARD_BQ_TABLE"
        DATASET_ID="${HOMEWARD_BQ_DATASET}"
        
        print_info "Checking existing BigQuery object table: $DATASET_ID.$TABLE_NAME"
        if bq show --table --project_id="$PROJECT_ID" "$DATASET_ID.$TABLE_NAME" > /dev/null 2>&1; then
            print_success "Using existing BigQuery object table: $TABLE_NAME"
            return 0
        else
            print_warning "Configured table no longer exists, creating new one..."
        fi
    fi
    
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
    if ! grep -q "^HOMEWARD_BQ_TABLE=" .env 2>/dev/null; then
        echo "HOMEWARD_BQ_TABLE=$TABLE_NAME" >> .env
    fi
    print_info "Table name saved to environment: HOMEWARD_BQ_TABLE"
}

# Execute SQL scripts from a specified folder
execute_sql_scripts_from_folder() {
    local folder_path="$1"
    local folder_description="$2"
    
    print_step "Executing SQL Scripts from $folder_description"
    
    # Check if folder exists
    if [[ ! -d "$folder_path" ]]; then
        print_warning "Folder not found: $folder_path"
        print_info "Skipping $folder_description SQL script execution"
        return 0
    fi
    
    # Find SQL files and sort them alphabetically
    local sql_files=()
    while IFS= read -r -d '' file; do
        sql_files+=("$file")
    done < <(find "$folder_path" -name "*.sql" -type f -print0 | sort -z)
    
    if [[ ${#sql_files[@]} -eq 0 ]]; then
        print_warning "No SQL files found in: $folder_path"
        print_info "Skipping $folder_description SQL script execution"
        return 0
    fi
    
    print_info "Found ${#sql_files[@]} SQL files to execute in $folder_description"
    
    local success_count=0
    local failure_count=0
    
    # Execute each SQL file in alphabetical order
    for sql_file in "${sql_files[@]}"; do
        local filename=$(basename "$sql_file")
        print_info "Executing SQL script: $filename"
        
        # Read SQL file content
        local sql_content
        if ! sql_content=$(cat "$sql_file"); then
            print_error "Failed to read SQL file: $sql_file"
            ((failure_count++))
            continue
        fi
        
        # Execute SQL using bq query
        if bq query --use_legacy_sql=false --project_id="$PROJECT_ID" "$sql_content"; then
            print_success "Successfully executed: $filename"
            ((success_count++))
        else
            print_error "Failed to execute SQL script: $filename"
            ((failure_count++))
        fi
        
        echo ""
    done
    
    print_step "$folder_description SQL Execution Summary"
    print_success "Successfully executed: $success_count scripts"
    if [[ $failure_count -gt 0 ]]; then
        print_warning "Failed to execute: $failure_count scripts"
    fi
    
    if [[ $success_count -eq 0 && ${#sql_files[@]} -gt 0 ]]; then
        print_error "No SQL scripts were successfully executed in $folder_description"
        exit 1
    fi
}

# Parse CSV configuration and extract video metadata (only if demo folder is specified)
parse_video_config() {
    # Skip if no demo folder specified
    if [[ -z "$DEMO_FOLDER" ]]; then
        print_info "No demo folder specified - skipping video configuration parsing"
        return 0
    fi

    print_step "Parsing Video Configuration"

    # Set path to video sources CSV file
    local video_config_file="$DEMO_FOLDER/videos/metadata/video_sources.csv"

    # Check if CSV file exists
    if [[ ! -f "$video_config_file" ]]; then
        print_warning "Video sources configuration not found: $video_config_file"
        print_info "Will process only media files from videos/media/ folder if available"
        VIDEO_COUNT=0
        return 0
    fi

    # Count videos in configuration
    VIDEO_COUNT=$(wc -l < "$video_config_file" | tr -d ' ')
    print_info "Found $VIDEO_COUNT videos to process from CSV configuration"

    if [[ $VIDEO_COUNT -eq 0 ]]; then
        print_warning "No video entries found in configuration file"
        print_info "Will process only media files from videos/media/ folder if available"
        return 0
    fi

    # Store the video config file path for later use
    export VIDEO_CONFIG_FILE="$video_config_file"

    print_success "Video configuration validated successfully"
}

# Parse filename to extract metadata according to Homeward naming convention
parse_filename_metadata() {
    local filename="$1"
    local basename_file=$(basename "$filename" | sed 's/\.[^.]*$//')  # Remove extension

    # Expected format: CameraID_YYYYMMDDHHMMSS_LATITUDE_LONGITUDE_CAMERATYPE_RESOLUTION
    # Split by underscore
    IFS='_' read -ra PARTS <<< "$basename_file"

    if [[ ${#PARTS[@]} -lt 6 ]]; then
        return 1  # Not enough parts
    fi

    # Extract metadata
    PARSED_CAMERA_ID="${PARTS[0]}"
    PARSED_TIMESTAMP="${PARTS[1]}"
    PARSED_LATITUDE="${PARTS[2]}"
    PARSED_LONGITUDE="${PARTS[3]}"
    PARSED_CAMERA_TYPE="${PARTS[4]}"
    PARSED_RESOLUTION="${PARTS[5]}"

    # Validate timestamp format (YYYYMMDDHHMMSS)
    if [[ ! "$PARSED_TIMESTAMP" =~ ^[0-9]{14}$ ]]; then
        return 1
    fi

    # Validate coordinates (basic check for numeric values)
    if [[ ! "$PARSED_LATITUDE" =~ ^-?[0-9]+\.?[0-9]*$ ]] || [[ ! "$PARSED_LONGITUDE" =~ ^-?[0-9]+\.?[0-9]*$ ]]; then
        return 1
    fi

    return 0
}

# Process media files from demo folder's videos/media/ directory
process_media_files() {
    # Skip if no demo folder specified
    if [[ -z "$DEMO_FOLDER" ]]; then
        print_info "No demo folder specified - skipping media file processing"
        return 0
    fi

    local media_folder="$DEMO_FOLDER/videos/media"

    # Check if media folder exists
    if [[ ! -d "$media_folder" ]]; then
        print_info "Media folder not found: $media_folder - skipping media file processing"
        return 0
    fi

    print_step "Processing Media Files from Demo Folder"
    print_info "Scanning media folder: $media_folder"

    # Find media files (mp4, avi, mov, mkv)
    local media_files=()
    while IFS= read -r -d '' file; do
        media_files+=("$file")
    done < <(find "$media_folder" -type f \( -iname "*.mp4" -o -iname "*.avi" -o -iname "*.mov" -o -iname "*.mkv" \) -print0)

    if [[ ${#media_files[@]} -eq 0 ]]; then
        print_warning "No media files found in: $media_folder"
        return 0
    fi

    print_info "Found ${#media_files[@]} media files to process"

    local success_count=0
    local failure_count=0
    local file_number=0

    for media_file in "${media_files[@]}"; do
        ((file_number++))
        local filename=$(basename "$media_file")

        print_info "Processing media file $file_number/${#media_files[@]}: $filename"

        # Try to parse filename for metadata
        if parse_filename_metadata "$filename"; then
            print_success "  Parsed metadata from filename:"
            print_info "    Camera ID: $PARSED_CAMERA_ID"
            print_info "    Timestamp: $PARSED_TIMESTAMP"
            print_info "    Latitude: $PARSED_LATITUDE"
            print_info "    Longitude: $PARSED_LONGITUDE"
            print_info "    Camera Type: $PARSED_CAMERA_TYPE"
            print_info "    Resolution: $PARSED_RESOLUTION"

            # Determine MIME type based on file extension
            local file_ext="${filename##*.}"
            local mime_type="video/mp4"
            case "${file_ext,,}" in
                avi) mime_type="video/x-msvideo" ;;
                mov) mime_type="video/quicktime" ;;
                mkv) mime_type="video/x-matroska" ;;
            esac

            # Generate video ID from filename
            local video_id="${PARSED_CAMERA_ID}_${PARSED_TIMESTAMP}"

            # Upload to GCS with parsed metadata
            print_info "  Uploading media file to GCS with parsed metadata..."
            if gsutil -h "Content-Type:$mime_type" \
                      -h "x-goog-meta-video-id:$video_id" \
                      -h "x-goog-meta-camera-id:$PARSED_CAMERA_ID" \
                      -h "x-goog-meta-timestamp:$PARSED_TIMESTAMP" \
                      -h "x-goog-meta-latitude:$PARSED_LATITUDE" \
                      -h "x-goog-meta-longitude:$PARSED_LONGITUDE" \
                      -h "x-goog-meta-camera-type:$PARSED_CAMERA_TYPE" \
                      -h "x-goog-meta-resolution:$PARSED_RESOLUTION" \
                      -h "x-goog-meta-upload-date:$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
                      -h "x-goog-meta-processed-by:homeward-setup-script" \
                      -h "x-goog-meta-source-dataset:Demo Media Files" \
                      cp "$media_file" "gs://$HOMEWARD_VIDEO_BUCKET/$filename"; then
                print_success "  Media file uploaded successfully with parsed metadata"
                ((success_count++))
            else
                print_error "  Failed to upload media file: $filename"
                ((failure_count++))
            fi
        else
            print_warning "  Could not parse metadata from filename: $filename"
            print_warning "  Expected format: CameraID_YYYYMMDDHHMMSS_LATITUDE_LONGITUDE_CAMERATYPE_RESOLUTION"
            print_info "  Uploading with basic metadata only..."

            # Generate basic metadata
            local video_id="unknown_$(date +%s)"
            local current_timestamp=$(date -u +%Y%m%d%H%M%S)

            # Upload with minimal metadata
            if gsutil -h "Content-Type:video/mp4" \
                      -h "x-goog-meta-video-id:$video_id" \
                      -h "x-goog-meta-camera-id:unknown" \
                      -h "x-goog-meta-timestamp:$current_timestamp" \
                      -h "x-goog-meta-latitude:0.0" \
                      -h "x-goog-meta-longitude:0.0" \
                      -h "x-goog-meta-camera-type:unknown" \
                      -h "x-goog-meta-resolution:unknown" \
                      -h "x-goog-meta-upload-date:$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
                      -h "x-goog-meta-processed-by:homeward-setup-script" \
                      -h "x-goog-meta-source-dataset:Demo Media Files" \
                      -h "x-goog-meta-parsing-status:failed" \
                      cp "$media_file" "gs://$HOMEWARD_VIDEO_BUCKET/$filename"; then
                print_success "  Media file uploaded with basic metadata"
                ((success_count++))
            else
                print_error "  Failed to upload media file: $filename"
                ((failure_count++))
            fi
        fi

        echo ""
    done

    print_step "Media File Processing Summary"
    print_success "Successfully processed: $success_count media files"
    if [[ $failure_count -gt 0 ]]; then
        print_warning "Failed to process: $failure_count media files"
    fi

    # Update global video count
    if [[ -n "$VIDEO_COUNT" ]]; then
        VIDEO_COUNT=$((VIDEO_COUNT + success_count))
    else
        VIDEO_COUNT=$success_count
    fi
}

# Download and upload videos to GCS (only if demo folder is specified)
process_videos() {
    # Skip if no demo folder specified or no video config
    if [[ -z "$DEMO_FOLDER" || -z "$VIDEO_CONFIG_FILE" ]]; then
        print_info "No demo folder or video configuration - skipping CSV-based video processing"
        return 0
    fi

    print_step "Processing and Uploading Videos from CSV Configuration"

    # Create temporary directory for downloads
    TEMP_DIR=$(mktemp -d)
    print_info "Using temporary directory: $TEMP_DIR"

    # Ensure cleanup on exit
    trap "rm -rf $TEMP_DIR" EXIT

    local success_count=0
    local failure_count=0

    local line_number=0
    while IFS='|' read -r video_id download_url camera_id timestamp latitude longitude camera_type resolution location duration_seconds mime_type; do
        ((line_number++))

        # Generate filename according to Homeward naming convention
        local filename="${camera_id}_${timestamp}_${latitude}_${longitude}_${camera_type}_${resolution}.mp4"
        local temp_file="$TEMP_DIR/$filename"

        print_info "Processing video $line_number/$VIDEO_COUNT: $video_id"
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
                  -h "x-goog-meta-source-dataset:VIRAT Video and Image Dataset Release 2.0" \
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
        print_success "  Video $video_id processed successfully ($line_number/$VIDEO_COUNT completed)"
        echo ""
    done < "$VIDEO_CONFIG_FILE"

    print_step "CSV-based Video Processing Summary"
    print_success "Successfully processed: $success_count videos"
    if [[ $failure_count -gt 0 ]]; then
        print_warning "Failed to process: $failure_count videos"
    fi

    if [[ $success_count -eq 0 ]]; then
        print_warning "No videos were successfully processed from CSV configuration"
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
            --demo-folder)
                DEMO_FOLDER="$2"
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
    load_existing_environment
    authenticate_gcloud
    enable_required_apis
    create_geocoding_api_key
    create_storage_bucket
    create_bigquery_connection
    create_bigquery_dataset
    create_video_downloader_service_account
    parse_video_config
    process_videos
    process_media_files
    create_bigquery_object_table
    
    # Execute SQL scripts in required order
    # 1. DDL SQL scripts (mandatory)
    execute_sql_scripts_from_folder "sql/DDL" "DDL SQL Scripts"
    
    # 2. Demo-specific SQL scripts (only if demo folder specified)
    if [[ -n "$DEMO_FOLDER" ]]; then
        execute_sql_scripts_from_folder "$DEMO_FOLDER/reports/missings" "Missing Persons Reports"
        execute_sql_scripts_from_folder "$DEMO_FOLDER/reports/sightings" "Sightings Reports"
    fi
    
    print_step "Setup Complete"
    print_success "Homeward project setup completed successfully!"
    print_info "Video ingestion bucket: gs://$HOMEWARD_VIDEO_BUCKET"
    print_info "BigQuery connection: $HOMEWARD_BQ_CONNECTION"
    print_info "BigQuery dataset: $HOMEWARD_BQ_DATASET"
    print_info "BigQuery object table: $HOMEWARD_BQ_TABLE"
    print_info "Geocoding API key: $(echo "$HOMEWARD_GEOCODING_API_KEY" | cut -c1-10)... (configured)"
    print_info "Video downloader service account: video-downloader-sa@${PROJECT_ID}.iam.gserviceaccount.com"
    print_info "Service account key: ${HOMEWARD_SERVICE_ACCOUNT_KEY_PATH:-downloads/key.json}"
    print_info "Project ID: $PROJECT_ID"
    print_info "Region: $REGION"
    if [[ -n "$VIDEO_COUNT" && $VIDEO_COUNT -gt 0 ]]; then
        print_info "Videos processed: $VIDEO_COUNT"
    else
        print_info "Videos processed: 0"
    fi
    echo ""
    print_warning "IMPORTANT: Keep the service account key file secure and do not commit it to version control!"
}

# Execute main function with all arguments
main "$@"