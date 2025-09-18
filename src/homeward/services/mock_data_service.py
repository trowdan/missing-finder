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

    def search_cases(self, query: str, field: str = "all", page: int = 1, page_size: int = 20) -> tuple[list[MissingPersonCase], int]:
        """Search missing person cases with LIKE filtering"""
        if not query or not query.strip():
            return self.get_cases(page=page, page_size=page_size)

        query = query.lower().strip()
        results = []

        for case in self._cases:
            match = False

            if field == "all" or field == "id":
                if query in case.id.lower():
                    match = True

            if field == "all" or field == "full name":
                full_name = f"{case.name} {case.surname}".lower()
                if query in case.name.lower() or query in case.surname.lower() or query in full_name:
                    match = True

            if field == "all":
                # When searching "all", include additional searchable fields
                if case.description and query in case.description.lower():
                    match = True
                if case.circumstances and query in case.circumstances.lower():
                    match = True
                if (case.last_seen_location.address and query in case.last_seen_location.address.lower()) or \
                   (case.last_seen_location.city and query in case.last_seen_location.city.lower()):
                    match = True
                if case.case_number and query in case.case_number.lower():
                    match = True

            if match:
                results.append(case)

        total_count = len(results)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = results[start_idx:end_idx]

        return paginated_results, total_count

    def search_sightings(self, query: str, field: str = "all", page: int = 1, page_size: int = 20) -> tuple[list[Sighting], int]:
        """Search sighting reports with LIKE filtering"""
        if not query or not query.strip():
            return self.get_sightings(page=page, page_size=page_size)

        query = query.lower().strip()
        results = []

        for sighting in self._sightings:
            match = False

            if field == "all" or field == "id":
                if query in sighting.id.lower():
                    match = True

            if field == "all":
                # When searching "all", include additional searchable fields
                if sighting.description and query in sighting.description.lower():
                    match = True
                if sighting.circumstances and query in sighting.circumstances.lower():
                    match = True
                if (sighting.sighted_location.address and query in sighting.sighted_location.address.lower()) or \
                   (sighting.sighted_location.city and query in sighting.sighted_location.city.lower()):
                    match = True
                if sighting.witness_name and query in sighting.witness_name.lower():
                    match = True
                if sighting.sighting_number and query in sighting.sighting_number.lower():
                    match = True

            if match:
                results.append(sighting)

        total_count = len(results)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = results[start_idx:end_idx]

        return paginated_results, total_count

    def update_missing_persons_embeddings(self) -> dict:
        """Mock implementation - embeddings are not calculated in mock service"""
        return {
            "success": True,
            "rows_modified": 0,
            "message": "Mock service: embeddings update simulated (no actual embeddings calculated)"
        }

    def update_sightings_embeddings(self) -> dict:
        """Mock implementation - embeddings are not calculated in mock service"""
        return {
            "success": True,
            "rows_modified": 0,
            "message": "Mock service: embeddings update simulated (no actual embeddings calculated)"
        }

    def find_similar_sightings_for_missing_person(self, missing_person_id: str, search_radius_meters: float = 10000.0, delta_days: int = 30, top_k: int = 5) -> list[dict]:
        """Mock implementation - returns sample similarity results for testing"""
        # Return mock similarity results for demonstration
        return [
            {
                "missing_person_id": missing_person_id,
                "case_number": "MP-2024-001",
                "similarity_distance": 0.15,
                "sighting_id": "S-2024-001",
                "sighting_number": "SGHT-001",
                "sighted_date": "2024-01-15",
                "sighted_time": "14:30:00",
                "sighted_city": "Mock City",
                "witness_name": "John Doe",
                "confidence_level": "High",
                "ml_summary": "Mock sighting of person matching description near shopping center",
                "distance_km": 2.1
            },
            {
                "missing_person_id": missing_person_id,
                "case_number": "MP-2024-001",
                "similarity_distance": 0.25,
                "sighting_id": "S-2024-002",
                "sighting_number": "SGHT-002",
                "sighted_date": "2024-01-16",
                "sighted_time": "09:15:00",
                "sighted_city": "Mock City",
                "witness_name": "Jane Smith",
                "confidence_level": "Medium",
                "ml_summary": "Possible match reported at transit station, partial view",
                "distance_km": 4.7
            }
        ]

    def find_similar_missing_persons_for_sighting(self, sighting_id: str, search_radius_meters: float = 10000.0, delta_days: int = 30, top_k: int = 5) -> list[dict]:
        """Mock implementation - returns sample similar missing person cases for testing"""
        # Return mock similarity results for demonstration
        return [
            {
                "sighting_id": sighting_id,
                "sighting_number": "SGHT-001",
                "similarity_distance": 0.18,
                "id": "MP-2024-001",
                "case_number": "MP001-2024",
                "name": "John",
                "surname": "Anderson",
                "age": 28,
                "gender": "Male",
                "priority": "High",
                "last_seen_date": "2024-01-10",
                "last_seen_city": "Mock City",
                "ml_summary": "Missing person case with similar physical description and circumstances in the area",
                "distance_km": 1.8
            },
            {
                "sighting_id": sighting_id,
                "sighting_number": "SGHT-001",
                "similarity_distance": 0.32,
                "id": "MP-2024-002",
                "case_number": "MP002-2024",
                "name": "Michael",
                "surname": "Brown",
                "age": 25,
                "gender": "Male",
                "priority": "Medium",
                "last_seen_date": "2024-01-08",
                "last_seen_city": "Mock City North",
                "ml_summary": "Young adult male with similar build and clothing description from nearby area",
                "distance_km": 3.2
            },
            {
                "sighting_id": sighting_id,
                "sighting_number": "SGHT-001",
                "similarity_distance": 0.45,
                "id": "MP-2024-003",
                "case_number": "MP003-2024",
                "name": "David",
                "surname": "Wilson",
                "age": 30,
                "gender": "Male",
                "priority": "Low",
                "last_seen_date": "2024-01-05",
                "last_seen_city": "Mock City South",
                "ml_summary": "Missing person with comparable age and general appearance characteristics",
                "distance_km": 5.7
            }
        ]
