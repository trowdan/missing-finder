import binascii
import collections
import datetime
import hashlib
import logging
import os
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import six
from google.cloud import storage
from google.oauth2 import service_account
from nicegui import ui

from homeward.config import AppConfig

logger = logging.getLogger(__name__)


class GCSService:
    """Service for downloading files from Google Cloud Storage"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.client = storage.Client(project=config.bigquery_project_id)
        self.processed_bucket = config.gcs_bucket_processed

        # Try to get service account credentials for signing
        self.service_account_credentials = self._get_service_account_credentials()

    def _get_service_account_credentials(self) -> Optional[service_account.Credentials]:
        """Try to get service account credentials with private key for signing"""
        try:
            # First try the configured path
            service_account_file = self.config.service_account_key_path
            if service_account_file and os.path.exists(service_account_file):
                logger.info(f"Using service account key from config: {service_account_file}")
                return service_account.Credentials.from_service_account_file(service_account_file)

            # Fallback to environment variable
            service_account_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if service_account_file and os.path.exists(service_account_file):
                logger.info(f"Using service account key from environment: {service_account_file}")
                return service_account.Credentials.from_service_account_file(service_account_file)

            logger.warning("No service account key file found. Signed URLs will not be available.")
            return None
        except Exception as e:
            logger.warning(f"Could not load service account credentials: {e}")
            return None

    def download_video_file(self, video_url: str) -> None:
        """Download a video file from GCS using presigned URL"""
        try:
            # Parse the GCS URL to extract bucket and blob name
            # Expected format: gs://bucket-name/path/to/file.mp4
            if not video_url.startswith('gs://'):
                ui.notify("❌ Invalid GCS URL format", type="negative")
                return

            # Remove gs:// prefix and split bucket/path
            url_parts = video_url[5:].split('/', 1)
            if len(url_parts) != 2:
                ui.notify("❌ Invalid GCS URL format", type="negative")
                return

            bucket_name, blob_name = url_parts

            # Get the bucket and blob
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Check if blob exists
            if not blob.exists():
                ui.notify(f"❌ File not found: {blob_name}", type="negative")
                return

            # Get the filename from the blob path
            filename = Path(blob_name).name

            # Try to generate presigned URL
            if self.service_account_credentials:
                try:
                    signed_url = self.generate_signed_url(
                        bucket_name=bucket_name,
                        object_name=blob_name,
                        expiration=3600  # 1 hour
                    )
                    ui.download(signed_url, filename)
                    ui.notify(f"✅ Downloading {filename}", type="positive")
                    return
                except Exception as e:
                    logger.warning(f"Failed to generate presigned URL: {e}")

            # Fallback: Try standard blob signing (might fail without private key)
            try:
                signed_url = blob.generate_signed_url(
                    version="v4",
                    expiration=datetime.timedelta(hours=1),
                    method="GET"
                )
                ui.download(signed_url, filename)
                ui.notify(f"✅ Downloading {filename}", type="positive")
            except Exception as e:
                logger.error(f"Standard signing also failed: {e}")
                ui.notify("❌ Download failed: Unable to generate signed URL. Service account with private key required.", type="negative")

        except Exception as e:
            logger.error(f"Failed to download video file {video_url}: {e}")
            ui.notify(f"❌ Download failed: {str(e)}", type="negative")

    def generate_signed_url(
        self,
        bucket_name: str,
        object_name: str,
        subresource=None,
        expiration=604800,
        http_method="GET",
        query_parameters=None,
        headers=None,
    ) -> str:
        """Generate a presigned URL for downloading a GCS object"""
        if not self.service_account_credentials:
            raise ValueError("Service account credentials required for signing")

        if expiration > 604800:
            raise ValueError("Expiration Time can't be longer than 604800 seconds (7 days).")

        escaped_object_name = quote(six.ensure_binary(object_name), safe=b"/~")
        canonical_uri = f"/{escaped_object_name}"

        datetime_now = datetime.datetime.now(tz=datetime.timezone.utc)
        request_timestamp = datetime_now.strftime("%Y%m%dT%H%M%SZ")
        datestamp = datetime_now.strftime("%Y%m%d")

        client_email = self.service_account_credentials.service_account_email
        credential_scope = f"{datestamp}/auto/storage/goog4_request"
        credential = f"{client_email}/{credential_scope}"

        if headers is None:
            headers = dict()
        host = f"{bucket_name}.storage.googleapis.com"
        headers["host"] = host

        canonical_headers = ""
        ordered_headers = collections.OrderedDict(sorted(headers.items()))
        for k, v in ordered_headers.items():
            lower_k = str(k).lower()
            strip_v = str(v).lower()
            canonical_headers += f"{lower_k}:{strip_v}\n"

        signed_headers = ""
        for k, _ in ordered_headers.items():
            lower_k = str(k).lower()
            signed_headers += f"{lower_k};"
        signed_headers = signed_headers[:-1]  # remove trailing ';'

        if query_parameters is None:
            query_parameters = dict()
        query_parameters["X-Goog-Algorithm"] = "GOOG4-RSA-SHA256"
        query_parameters["X-Goog-Credential"] = credential
        query_parameters["X-Goog-Date"] = request_timestamp
        query_parameters["X-Goog-Expires"] = expiration
        query_parameters["X-Goog-SignedHeaders"] = signed_headers
        if subresource:
            query_parameters[subresource] = ""

        canonical_query_string = ""
        ordered_query_parameters = collections.OrderedDict(sorted(query_parameters.items()))
        for k, v in ordered_query_parameters.items():
            encoded_k = quote(str(k), safe="")
            encoded_v = quote(str(v), safe="")
            canonical_query_string += f"{encoded_k}={encoded_v}&"
        canonical_query_string = canonical_query_string[:-1]  # remove trailing '&'

        canonical_request = "\n".join(
            [
                http_method,
                canonical_uri,
                canonical_query_string,
                canonical_headers,
                signed_headers,
                "UNSIGNED-PAYLOAD",
            ]
        )

        canonical_request_hash = hashlib.sha256(canonical_request.encode()).hexdigest()

        string_to_sign = "\n".join(
            [
                "GOOG4-RSA-SHA256",
                request_timestamp,
                credential_scope,
                canonical_request_hash,
            ]
        )

        # signer.sign() signs using RSA-SHA256 with PKCS1v15 padding
        signature = binascii.hexlify(
            self.service_account_credentials.signer.sign(string_to_sign)
        ).decode()

        scheme_and_host = "{}://{}".format("https", host)
        signed_url = "{}{}?{}&x-goog-signature={}".format(
            scheme_and_host, canonical_uri, canonical_query_string, signature
        )

        return signed_url

    def get_file_info(self, video_url: str) -> Optional[dict]:
        """Get information about a file in GCS"""
        try:
            if not video_url.startswith('gs://'):
                return None

            url_parts = video_url[5:].split('/', 1)
            if len(url_parts) != 2:
                return None

            bucket_name, blob_name = url_parts
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            if not blob.exists():
                return None

            blob.reload()  # Refresh metadata

            return {
                'name': Path(blob_name).name,
                'size': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created,
                'updated': blob.updated
            }

        except Exception as e:
            logger.error(f"Failed to get file info for {video_url}: {e}")
            return None