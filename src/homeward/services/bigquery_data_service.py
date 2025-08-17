from typing import Optional

from homeward.config import AppConfig
from homeward.models.case import KPIData, MissingPersonCase, Sighting
from homeward.services.data_service import DataService


class BigQueryDataService(DataService):
    """BigQuery implementation of DataService for production use"""

    def __init__(self, config: AppConfig):
        self.config = config
        # TODO: Initialize BigQuery client
        # self.client = bigquery.Client(project=config.bigquery_project_id)

    def get_cases(self, status_filter: Optional[str] = None) -> list[MissingPersonCase]:
        """Get missing person cases from BigQuery"""
        # TODO: Implement BigQuery query
        raise NotImplementedError("BigQuery implementation not yet available")

    def get_kpi_data(self) -> KPIData:
        """Get KPI dashboard data from BigQuery"""
        # TODO: Implement BigQuery aggregation queries
        raise NotImplementedError("BigQuery implementation not yet available")

    def get_case_by_id(self, case_id: str) -> Optional[MissingPersonCase]:
        """Get a specific case by ID from BigQuery"""
        # TODO: Implement BigQuery query by ID
        raise NotImplementedError("BigQuery implementation not yet available")

    def create_case(self, case: MissingPersonCase) -> str:
        """Create a new case in BigQuery"""
        # TODO: Implement BigQuery insert
        raise NotImplementedError("BigQuery implementation not yet available")

    def get_sightings(self, status_filter: Optional[str] = None) -> list[Sighting]:
        """Get sighting reports from BigQuery"""
        # TODO: Implement BigQuery query
        raise NotImplementedError("BigQuery implementation not yet available")

    def get_sighting_by_id(self, sighting_id: str) -> Sighting:
        """Get a specific sighting by ID from BigQuery"""
        # TODO: Implement BigQuery query by ID
        raise NotImplementedError("BigQuery implementation not yet available")

    def create_sighting(self, sighting: Sighting) -> str:
        """Create a new sighting in BigQuery"""
        # TODO: Implement BigQuery insert
        raise NotImplementedError("BigQuery implementation not yet available")
