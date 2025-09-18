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

    @abstractmethod
    def search_cases(self, query: str, field: str = "all", page: int = 1, page_size: int = 20) -> tuple[list[MissingPersonCase], int]:
        """Search missing person cases with LIKE filtering. Returns (cases, total_count)"""
        pass

    @abstractmethod
    def search_sightings(self, query: str, field: str = "all", page: int = 1, page_size: int = 20) -> tuple[list[Sighting], int]:
        """Search sighting reports with LIKE filtering. Returns (sightings, total_count)"""
        pass

    @abstractmethod
    def update_missing_persons_embeddings(self) -> dict:
        """Update embeddings for missing persons that don't have them yet. Returns status dict."""
        pass

    @abstractmethod
    def update_sightings_embeddings(self) -> dict:
        """Update embeddings for sightings that don't have them yet. Returns status dict."""
        pass

    @abstractmethod
    def find_similar_sightings_for_missing_person(self, missing_person_id: str, search_radius_meters: float = 10000.0, delta_days: int = 30, top_k: int = 5) -> list[dict]:
        """Find sightings similar to a missing person using vector search. Returns list of similarity results."""
        pass

    @abstractmethod
    def find_similar_missing_persons_for_sighting(self, sighting_id: str, search_radius_meters: float = 10000.0, delta_days: int = 30, top_k: int = 5) -> list[dict]:
        """Find missing persons similar to a sighting using vector search. Returns list of similarity results."""
        pass
