from abc import ABC, abstractmethod

from homeward.models.case import KPIData, MissingPersonCase, Sighting


class DataService(ABC):
    """Abstract base class for data services"""

    @abstractmethod
    def get_cases(self, status_filter: str = None) -> list[MissingPersonCase]:
        """Get missing person cases, optionally filtered by status"""
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
    def get_sightings(self, status_filter: str = None) -> list[Sighting]:
        """Get sighting reports, optionally filtered by status"""
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
