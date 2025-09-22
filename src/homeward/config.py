import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DataSource(Enum):
    MOCK = "mock"
    BIGQUERY = "bigquery"


@dataclass
class AppConfig:
    data_source: DataSource
    version: str
    bigquery_project_id: Optional[str] = None
    bigquery_dataset: Optional[str] = None
    bigquery_region: Optional[str] = None
    bigquery_connection: Optional[str] = None
    bigquery_model: Optional[str] = None
    gcs_bucket_ingestion: Optional[str] = None
    gcs_bucket_processed: Optional[str] = None
    geocoding_api_key: Optional[str] = None
    service_account_key_path: Optional[str] = None


def load_config() -> AppConfig:
    """Load configuration from environment variables"""
    data_source_str = os.getenv("HOMEWARD_DATA_SOURCE", "mock").lower()

    try:
        data_source = DataSource(data_source_str)
    except ValueError:
        data_source = DataSource.MOCK

    return AppConfig(
        data_source=data_source,
        version=os.getenv("HOMEWARD_VERSION", "0.1.0"),
        bigquery_project_id=os.getenv("HOMEWARD_BIGQUERY_PROJECT_ID"),
        bigquery_dataset=os.getenv("HOMEWARD_BIGQUERY_DATASET", "homeward"),
        bigquery_region=os.getenv("HOMEWARD_BIGQUERY_REGION", "us-central1"),
        bigquery_connection=os.getenv("HOMEWARD_BQ_CONNECTION", "homeward_gcp_connection"),
        bigquery_model=os.getenv("HOMEWARD_BQ_MODEL", "gemini-2.5-flash"),
        gcs_bucket_ingestion=os.getenv("HOMEWARD_GCS_BUCKET_INGESTION"),
        gcs_bucket_processed=os.getenv("HOMEWARD_GCS_BUCKET_PROCESSED"),
        geocoding_api_key=os.getenv("HOMEWARD_GEOCODING_API_KEY"),
        service_account_key_path=os.getenv("HOMEWARD_SERVICE_ACCOUNT_KEY_PATH", "downloads/key.json"),
    )
