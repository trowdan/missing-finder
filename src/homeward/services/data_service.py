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

    @abstractmethod
    def get_case_sightings(self, case_id: str) -> list[dict]:
        """Get all sightings linked to a specific case from the case_sightings table. Returns list of sighting link data."""
        pass

    @abstractmethod
    def link_sighting_to_case(self, sighting_id: str, case_id: str, match_confidence: float = 0.5, match_type: str = "Manual", match_reason: str = None) -> bool:
        """Link a sighting to a missing person case. Returns success status."""
        pass

    @abstractmethod
    def get_linked_case_for_sighting(self, sighting_id: str) -> dict:
        """Get the linked case information for a sighting. Returns case data dict or None if not linked."""
        pass

    @abstractmethod
    def search_cases_by_location(self, latitude: float, longitude: float, radius_km: float, page: int = 1, page_size: int = 20) -> tuple[list[MissingPersonCase], int]:
        """Search missing person cases by geographic location using BigQuery geo functions. Returns (cases, total_count)"""
        pass

    @abstractmethod
    def search_sightings_by_location(self, latitude: float, longitude: float, radius_km: float, page: int = 1, page_size: int = 20) -> tuple[list[Sighting], int]:
        """Search sighting reports by geographic location using BigQuery geo functions. Returns (sightings, total_count)"""
        pass

    @abstractmethod
    def get_video_evidence_for_case(self, case_id: str) -> list[dict]:
        """Get all video evidence linked to a specific case from the video_analytics_results table. Returns list of video evidence data."""
        pass
