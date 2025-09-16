from typing import Optional

from homeward.models.case import (
    CaseStatus,
    KPIData,
    MissingPersonCase,
    Sighting,
    SightingStatus,
)
from homeward.services.data_service import DataService
from homeward.services.mock_data import (
    get_mock_cases,
    get_mock_kpi_data,
    get_mock_sightings,
)


class MockDataService(DataService):
    """Mock implementation of DataService for development and testing"""

    def __init__(self):
        self._cases = get_mock_cases()
        self._sightings = get_mock_sightings()
        self._kpi_data = get_mock_kpi_data()

    def get_cases(self, status_filter: Optional[str] = None, page: int = 1, page_size: int = 20) -> tuple[list[MissingPersonCase], int]:
        """Get missing person cases with pagination. Returns (cases, total_count)"""
        if status_filter is None:
            filtered_cases = self._cases
        else:
            try:
                status_enum = CaseStatus(status_filter)
                filtered_cases = [case for case in self._cases if case.status == status_enum]
            except ValueError:
                filtered_cases = self._cases

        total_count = len(filtered_cases)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_cases = filtered_cases[start_idx:end_idx]

        return paginated_cases, total_count

    def get_kpi_data(self) -> KPIData:
        """Get KPI dashboard data"""
        return self._kpi_data

    def get_case_by_id(self, case_id: str) -> Optional[MissingPersonCase]:
        """Get a specific case by ID"""
        for case in self._cases:
            if case.id == case_id:
                return case
        return None

    def create_case(self, case: MissingPersonCase) -> str:
        """Create a new case and return the ID"""
        self._cases.append(case)
        return case.id

    def get_sightings(self, status_filter: Optional[str] = None, page: int = 1, page_size: int = 20) -> tuple[list[Sighting], int]:
        """Get sighting reports with pagination. Returns (sightings, total_count)"""
        if status_filter is None:
            filtered_sightings = self._sightings
        else:
            try:
                status_enum = SightingStatus(status_filter)
                filtered_sightings = [
                    sighting
                    for sighting in self._sightings
                    if sighting.status == status_enum
                ]
            except ValueError:
                filtered_sightings = self._sightings

        total_count = len(filtered_sightings)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_sightings = filtered_sightings[start_idx:end_idx]

        return paginated_sightings, total_count

    def get_sighting_by_id(self, sighting_id: str) -> Optional[Sighting]:
        """Get a specific sighting by ID"""
        for sighting in self._sightings:
            if sighting.id == sighting_id:
                return sighting
        return None

    def create_sighting(self, sighting: Sighting) -> str:
        """Create a new sighting and return the ID"""
        self._sightings.append(sighting)
        return sighting.id

    def update_case(self, case: MissingPersonCase) -> bool:
        """Update an existing case and return success status"""
        for i, existing_case in enumerate(self._cases):
            if existing_case.id == case.id:
                self._cases[i] = case
                return True
        return False

    def update_sighting(self, sighting: Sighting) -> bool:
        """Update an existing sighting and return success status"""
        for i, existing_sighting in enumerate(self._sightings):
            if existing_sighting.id == sighting.id:
                self._sightings[i] = sighting
                return True
        return False
