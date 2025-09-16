from abc import ABC, abstractmethod
from typing import Optional

from homeward.models.case import KPIData, MissingPersonCase, Sighting


class DataService(ABC):
    """Abstract base class for data services"""

    @abstractmethod
    def get_cases(self, status_filter: Optional[str] = None, page: int = 1, page_size: int = 20) -> tuple[list[MissingPersonCase], int]:
        """Get missing person cases with pagination. Returns (cases, total_count)"""
        pass

    @abstractmethod
    def get_kpi_data(self) -> KPIData:
        """Get KPI dashboard data"""
        pass

    @abstractmethod
    def get_case_by_id(self, case_id: str) -> MissingPersonCase:
        """Get a specific case by ID"""
        pass

    @abstractmethod
    def create_case(self, case: MissingPersonCase) -> str:
        """Create a new case and return the ID"""
        pass

    @abstractmethod
    def update_case(self, case: MissingPersonCase) -> bool:
        """Update an existing case and return success status"""
        pass

    @abstractmethod
    def get_sightings(self, status_filter: Optional[str] = None, page: int = 1, page_size: int = 20) -> tuple[list[Sighting], int]:
        """Get sighting reports with pagination. Returns (sightings, total_count)"""
        pass

    @abstractmethod
    def get_sighting_by_id(self, sighting_id: str) -> Sighting:
        """Get a specific sighting by ID"""
        pass

    @abstractmethod
    def create_sighting(self, sighting: Sighting) -> str:
        """Create a new sighting and return the ID"""
        pass

    @abstractmethod
    def update_sighting(self, sighting: Sighting) -> bool:
        """Update an existing sighting and return success status"""
        pass
