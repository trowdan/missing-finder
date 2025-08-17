from homeward.config import AppConfig, DataSource
from homeward.services.data_service import DataService
from homeward.services.mock_data_service import MockDataService
from homeward.services.bigquery_data_service import BigQueryDataService
from homeward.services.video_analysis_service import VideoAnalysisService
from homeward.services.mock_video_analysis_service import MockVideoAnalysisService
from homeward.services.bigquery_video_analysis_service import BigQueryVideoAnalysisService


def create_data_service(config: AppConfig) -> DataService:
    """Factory function to create the appropriate data service based on configuration"""
    
    if config.data_source == DataSource.MOCK:
        return MockDataService()
    elif config.data_source == DataSource.BIGQUERY:
        return BigQueryDataService(config)
    else:
        raise ValueError(f"Unknown data source: {config.data_source}")


def create_video_analysis_service(config: AppConfig) -> VideoAnalysisService:
    """Factory function to create the appropriate video analysis service based on configuration"""
    
    if config.data_source == DataSource.MOCK:
        return MockVideoAnalysisService()
    elif config.data_source == DataSource.BIGQUERY:
        return BigQueryVideoAnalysisService(config.project_id, config.dataset_id)
    else:
        raise ValueError(f"Unknown data source: {config.data_source}")