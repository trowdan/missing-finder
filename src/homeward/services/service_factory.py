from homeward.config import AppConfig, DataSource
from homeward.services.data_service import DataService
from homeward.services.mock_data_service import MockDataService
from homeward.services.bigquery_data_service import BigQueryDataService


def create_data_service(config: AppConfig) -> DataService:
    """Factory function to create the appropriate data service based on configuration"""
    
    if config.data_source == DataSource.MOCK:
        return MockDataService()
    elif config.data_source == DataSource.BIGQUERY:
        return BigQueryDataService(config)
    else:
        raise ValueError(f"Unknown data source: {config.data_source}")