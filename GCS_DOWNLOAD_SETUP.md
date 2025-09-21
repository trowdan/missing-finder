# GCS Video Download Setup

This document explains how to set up video file downloads from Google Cloud Storage in the Homeward application.

## Overview

The application now supports downloading video files from Google Cloud Storage when clicking the "View" button in the Video Intelligence results table. The download functionality uses presigned URLs for secure access to private GCS buckets.

## Automated Setup (Recommended)

The easiest way to set up video downloads is to use the automated setup script:

```bash
./setup.sh --demo-folder ./demo --project-id YOUR_PROJECT_ID --region us-central1
```

This script will automatically:
1. Create a service account named `video-downloader-sa`
2. Grant the necessary `storage.objectViewer` role
3. Generate a private key and save it to `downloads/key.json`
4. Configure the environment variables
5. Set proper file permissions (600) for security

## Manual Configuration

If you prefer manual setup or need to use a different service account:

### Service Account Key

To enable video downloads, you need to configure a service account key file with the appropriate permissions:

1. **Default Path**: Place your service account key file at `downloads/key.json` (relative to the application root)

2. **Custom Path**: Set the environment variable `HOMEWARD_SERVICE_ACCOUNT_KEY_PATH` to your custom path:
   ```bash
   export HOMEWARD_SERVICE_ACCOUNT_KEY_PATH="/path/to/your/service-account-key.json"
   ```

3. **Environment Variable Fallback**: The system will also check the standard `GOOGLE_APPLICATION_CREDENTIALS` environment variable

### Service Account Permissions

Your service account needs the following permissions:
- `storage.objects.get` - to read objects from the bucket
- `storage.objects.list` - to list objects in the bucket

### Manual Service Account Creation

If setting up manually:

```bash
# Create service account
gcloud iam service-accounts create video-downloader-sa \
    --project=YOUR_PROJECT_ID \
    --display-name="Video Downloader Service Account" \
    --description="Service account for downloading video files from GCS"

# Grant storage.objectViewer role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:video-downloader-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"

# Create downloads directory
mkdir -p downloads

# Generate private key
gcloud iam service-accounts keys create downloads/key.json \
    --iam-account="video-downloader-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --project=YOUR_PROJECT_ID

# Set secure permissions
chmod 600 downloads/key.json
```

## How It Works

1. **Presigned URLs**: When you click the "View" button, the application generates a presigned URL using the service account credentials
2. **Secure Download**: The presigned URL allows temporary access to the private GCS file without exposing permanent credentials
3. **Browser Download**: The file is downloaded directly by your browser using the presigned URL

## Fallback Behavior

If service account credentials are not available or cannot generate presigned URLs:
- The system will attempt to use the standard Google Cloud Storage client library signing
- If that also fails, an error message will be displayed explaining that a service account with private key is required

## Troubleshooting

### "Service account with private key required" Error

This error occurs when:
- No service account key file is found at the configured path
- The service account key file is invalid or corrupted
- The service account doesn't have the necessary permissions

**Solutions:**
1. Ensure the service account key file exists at the configured path
2. Verify the key file is valid JSON and contains the private key
3. Check that the service account has the required GCS permissions

### "File not found" Error

This error occurs when:
- The video file has been moved or deleted from GCS
- The bucket name or file path in the video URL is incorrect

**Solutions:**
1. Verify the file exists in the GCS bucket
2. Check the video URL format (should be `gs://bucket-name/path/to/file.mp4`)

## Cleanup

To remove the service account and clean up all resources, use the destroy script:

```bash
./destroy.sh --project-id YOUR_PROJECT_ID --region us-central1
```

This will automatically:
- Delete the service account and remove IAM bindings
- Remove the private key file (`downloads/key.json`)
- Clean up environment variables
- Remove the downloads directory if empty

## Security Notes

- Service account keys should be kept secure and not committed to version control
- The `downloads/` directory and `*.json` key files are automatically ignored by Git
- Presigned URLs have a default expiration of 1 hour for security
- The download process doesn't store files on the server, maintaining privacy and reducing storage requirements
- Private key files are created with restrictive permissions (600 - owner read/write only)