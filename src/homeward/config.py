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
    gcs_bucket_ingestion: Optional[str] = None
    gcs_bucket_processed: Optional[str] = None


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
        gcs_bucket_ingestion=os.getenv("HOMEWARD_GCS_BUCKET_INGESTION"),
        gcs_bucket_processed=os.getenv("HOMEWARD_GCS_BUCKET_PROCESSED"),
    )
