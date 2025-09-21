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

    def get_case_sightings(self, case_id: str) -> list[dict]:
        """Mock implementation - returns sample case sightings for testing"""
        # Return mock case sightings for demonstration
        return [
            {
                # Case sighting link data
                "link_id": "LINK-001",
                "missing_person_id": case_id,
                "sighting_id": "SGHT-001",
                "match_confidence": 0.85,
                "match_type": "AI_Analysis",
                "match_reason": "High similarity in physical characteristics and proximity to last seen location",
                "status": "Potential",
                "confirmed": False,
                "confirmed_by": None,
                "confirmed_date": None,
                "similarity_score": 0.82,
                "physical_match_score": 0.88,
                "temporal_match_score": 0.75,
                "geographical_match_score": 0.91,
                "investigated": False,
                "investigation_notes": None,
                "investigator_name": None,
                "investigation_date": None,
                "priority": "High",
                "requires_review": True,
                "review_notes": None,
                "created_date": "2024-01-02 10:30:00",
                "updated_date": "2024-01-02 10:30:00",
                "created_by": "AI System",
                "distance_km": 1.2,
                "time_difference_hours": 18,

                # Sighting data
                "sighting_number": "SGHT-001",
                "sighted_date": "2024-01-02 14:15:00",
                "sighted_address": "Union Station, 65 Front St W",
                "sighted_city": "Toronto",
                "sighted_country": "Canada",
                "sighted_latitude": 43.6465,
                "sighted_longitude": -79.3808,
                "apparent_gender": "Male",
                "apparent_age_range": "25-30",
                "height_estimate": 175.0,
                "weight_estimate": 70.0,
                "hair_color": "Brown",
                "eye_color": "Blue",
                "clothing_description": "Blue jeans, white t-shirt, black jacket",
                "distinguishing_features": "Small scar on left cheek",
                "sighting_description": "Individual matching description seen at Union Station",
                "sighting_circumstances": "Witnessed by station security camera",
                "confidence_level": "High",
                "photo_url": None,
                "video_url": "https://example.com/video1.mp4",
                "source_type": "Witness",
                "witness_name": "Security Officer Johnson",
                "witness_phone": "+1-416-555-0123",
                "witness_email": "security@unionstation.ca",
                "video_analytics_result_id": "VAR-001",
                "sighting_status": "Verified",
                "sighting_priority": "High",
                "verified": True,
                "sighting_notes": "High confidence match from security footage",
                "sighting_ml_summary": "Male individual aged 25-30 with brown hair and blue eyes spotted at Union Station"
            },
            {
                # Case sighting link data
                "link_id": "LINK-002",
                "missing_person_id": case_id,
                "sighting_id": "SGHT-002",
                "match_confidence": 0.72,
                "match_type": "Manual",
                "match_reason": "Similar clothing and general appearance reported by witness",
                "status": "Under_Review",
                "confirmed": False,
                "confirmed_by": None,
                "confirmed_date": None,
                "similarity_score": 0.68,
                "physical_match_score": 0.70,
                "temporal_match_score": 0.85,
                "geographical_match_score": 0.65,
                "investigated": True,
                "investigation_notes": "Witness interviewed, description matches but uncertain identification",
                "investigator_name": "Det. Sarah Miller",
                "investigation_date": "2024-01-03 09:00:00",
                "priority": "Medium",
                "requires_review": True,
                "review_notes": "Needs follow-up with additional witnesses",
                "created_date": "2024-01-03 14:15:00",
                "updated_date": "2024-01-03 16:30:00",
                "created_by": "Officer Martinez",
                "distance_km": 3.8,
                "time_difference_hours": 38,

                # Sighting data
                "sighting_number": "SGHT-002",
                "sighted_date": "2024-01-03 16:45:00",
                "sighted_address": "CN Tower Area, 290 Bremner Blvd",
                "sighted_city": "Toronto",
                "sighted_country": "Canada",
                "sighted_latitude": 43.6426,
                "sighted_longitude": -79.3871,
                "apparent_gender": "Male",
                "apparent_age_range": "20-35",
                "height_estimate": 178.0,
                "weight_estimate": 75.0,
                "hair_color": "Dark Brown",
                "eye_color": "Unknown",
                "clothing_description": "Dark jeans, hoodie",
                "distinguishing_features": "Walked with slight limp",
                "sighting_description": "Individual seen near CN Tower matching general description",
                "sighting_circumstances": "Reported by tourist visiting the area",
                "confidence_level": "Medium",
                "photo_url": None,
                "video_url": None,
                "source_type": "Witness",
                "witness_name": "Maria Rodriguez",
                "witness_phone": "+1-416-555-0456",
                "witness_email": "maria.r@email.com",
                "video_analytics_result_id": None,
                "sighting_status": "Under_Review",
                "sighting_priority": "Medium",
                "verified": False,
                "sighting_notes": "Witness seemed credible but lighting was poor",
                "sighting_ml_summary": "Male individual with dark features observed near CN Tower tourist area"
            },
            {
                # Case sighting link data
                "link_id": "LINK-003",
                "missing_person_id": case_id,
                "sighting_id": "SGHT-003",
                "match_confidence": 0.91,
                "match_type": "AI_Analysis",
                "match_reason": "Excellent facial recognition match and location correlation",
                "status": "Confirmed",
                "confirmed": True,
                "confirmed_by": "Det. Sarah Miller",
                "confirmed_date": "2024-01-04 11:20:00",
                "similarity_score": 0.94,
                "physical_match_score": 0.96,
                "temporal_match_score": 0.80,
                "geographical_match_score": 0.88,
                "investigated": True,
                "investigation_notes": "Positive identification confirmed through multiple sources",
                "investigator_name": "Det. Sarah Miller",
                "investigation_date": "2024-01-04 10:00:00",
                "priority": "High",
                "requires_review": False,
                "review_notes": "Case resolved - person located",
                "created_date": "2024-01-04 09:45:00",
                "updated_date": "2024-01-04 11:20:00",
                "created_by": "AI System",
                "distance_km": 0.8,
                "time_difference_hours": 65,

                # Sighting data
                "sighting_number": "SGHT-003",
                "sighted_date": "2024-01-04 09:30:00",
                "sighted_address": "Harbourfront Centre, 235 Queens Quay W",
                "sighted_city": "Toronto",
                "sighted_country": "Canada",
                "sighted_latitude": 43.6383,
                "sighted_longitude": -79.3816,
                "apparent_gender": "Male",
                "apparent_age_range": "25-30",
                "height_estimate": 175.0,
                "weight_estimate": 72.0,
                "hair_color": "Brown",
                "eye_color": "Blue",
                "clothing_description": "Same clothing as last seen",
                "distinguishing_features": "Visible scar on left cheek, distinctive gait",
                "sighting_description": "Clear identification by multiple witnesses and security footage",
                "sighting_circumstances": "Located at waterfront, appeared to be in good health",
                "confidence_level": "High",
                "photo_url": "https://example.com/photo3.jpg",
                "video_url": "https://example.com/video3.mp4",
                "source_type": "Witness",
                "witness_name": "Park Security Team",
                "witness_phone": "+1-416-555-0789",
                "witness_email": "security@harbourfront.com",
                "video_analytics_result_id": "VAR-003",
                "sighting_status": "Verified",
                "sighting_priority": "High",
                "verified": True,
                "sighting_notes": "Positive identification - person safely located",
                "sighting_ml_summary": "Confirmed sighting of missing person at Harbourfront Centre with positive identification"
            }
        ]

    def link_sighting_to_case(self, sighting_id: str, case_id: str, match_confidence: float = 0.5, match_type: str = "Manual", match_reason: str = None) -> bool:
        """Mock implementation - simulates linking a sighting to a case"""
        try:
            # In a real implementation, this would insert into the case_sightings table
            # For mock purposes, we'll just validate the inputs and return success

            # Basic validation
            if not sighting_id or not case_id:
                return False

            # Check if sighting exists
            sighting_exists = any(s.id == sighting_id for s in self._sightings)
            if not sighting_exists:
                return False

            # Check if case exists
            case_exists = any(c.id == case_id for c in self._cases)
            if not case_exists:
                return False

            # Validate confidence score
            if not (0.0 <= match_confidence <= 1.0):
                return False

            # For mock purposes, always return success after validation
            print(f"Mock: Successfully linked sighting {sighting_id} to case {case_id} with confidence {match_confidence}")
            return True

        except Exception as e:
            print(f"Mock: Error linking sighting to case: {str(e)}")
            return False

    def get_linked_case_for_sighting(self, sighting_id: str) -> dict:
        """Mock implementation - returns linked case data for a sighting if it exists"""
        try:
            # Check if sighting exists
            sighting_exists = any(s.id == sighting_id for s in self._sightings)
            if not sighting_exists:
                return None

            # For demo purposes, let's link the first sighting to a case
            # Get the first sighting ID dynamically
            if len(self._sightings) > 0:
                first_sighting_id = self._sightings[0].id
                second_sighting_id = self._sightings[1].id if len(self._sightings) > 1 else None

                # Create dynamic mock links based on actual sighting IDs
                mock_links = {}

                # Link first sighting to MP001
                mock_links[first_sighting_id] = {
                    "case_id": "MP001",
                    "case_number": "MP001-2024",
                    "case_name": "John",
                    "case_surname": "Smith",
                    "status": "Active",
                    "priority": "High",
                    "match_confidence": 0.85,
                    "match_type": "AI_Analysis",
                    "confirmed": False,
                    "link_status": "Potential",
                    "created_date": "2024-01-02",
                    "last_seen_city": "Toronto"
                }

                # Link second sighting to MP002 if it exists
                if second_sighting_id:
                    mock_links[second_sighting_id] = {
                        "case_id": "MP002",
                        "case_number": "MP002-2024",
                        "case_name": "Jane",
                        "case_surname": "Wilson",
                        "status": "Active",
                        "priority": "Medium",
                        "match_confidence": 0.74,
                        "match_type": "Manual",
                        "confirmed": True,
                        "link_status": "Confirmed",
                        "created_date": "2024-01-05",
                        "last_seen_city": "Vancouver"
                    }

                return mock_links.get(sighting_id, None)

            return None

        except Exception as e:
            print(f"Mock: Error getting linked case for sighting: {str(e)}")
            return None

    def search_cases_by_location(self, latitude: float, longitude: float, radius_km: float, page: int = 1, page_size: int = 20) -> tuple[list[MissingPersonCase], int]:
        """Search missing person cases by geographic location (mock implementation)"""
        import math

        def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            """Calculate distance between two points using Haversine formula"""
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.asin(math.sqrt(a))
            r = 6371  # Radius of earth in kilometers
            return c * r

        # Filter cases within the radius
        filtered_cases = []
        for case in self._cases:
            if case.last_seen_location.latitude and case.last_seen_location.longitude:
                distance = calculate_distance(
                    latitude, longitude,
                    case.last_seen_location.latitude,
                    case.last_seen_location.longitude
                )
                if distance <= radius_km:
                    filtered_cases.append((case, distance))

        # Sort by distance
        filtered_cases.sort(key=lambda x: x[1])
        cases_only = [case for case, distance in filtered_cases]

        # Apply pagination
        total_count = len(cases_only)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_cases = cases_only[start_idx:end_idx]

        return paginated_cases, total_count

    def search_sightings_by_location(self, latitude: float, longitude: float, radius_km: float, page: int = 1, page_size: int = 20) -> tuple[list[Sighting], int]:
        """Search sighting reports by geographic location (mock implementation)"""
        import math

        def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            """Calculate distance between two points using Haversine formula"""
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.asin(math.sqrt(a))
            r = 6371  # Radius of earth in kilometers
            return c * r

        # Filter sightings within the radius
        filtered_sightings = []
        for sighting in self._sightings:
            if sighting.sighted_location.latitude and sighting.sighted_location.longitude:
                distance = calculate_distance(
                    latitude, longitude,
                    sighting.sighted_location.latitude,
                    sighting.sighted_location.longitude
                )
                if distance <= radius_km:
                    filtered_sightings.append((sighting, distance))

        # Sort by distance
        filtered_sightings.sort(key=lambda x: x[1])
        sightings_only = [sighting for sighting, distance in filtered_sightings]

        # Apply pagination
        total_count = len(sightings_only)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_sightings = sightings_only[start_idx:end_idx]

        return paginated_sightings, total_count

    def get_video_evidence_for_case(self, case_id: str) -> list[dict]:
        """Get all video evidence linked to a specific case (mock implementation)"""
        # Mock video evidence data - in real implementation would query the database

        # Return empty list for mock - could be enhanced with mock data if needed
        mock_evidence = []

        # For demonstration, you could add some mock evidence like this:
        # mock_evidence = [
        #     {
        #         "result_id": "evidence_001",
        #         "case_id": case_id,
        #         "created_date": datetime.now(),
        #         "status": "Evidence",
        #         "video_timestamp": datetime(2023, 12, 1, 14, 30),
        #         "camera_id": "CAM_001",
        #         "camera_type": "CCTV",
        #         "latitude": 43.6532,
        #         "longitude": -79.3832,
        #         "address": "100 Queen St W, Toronto, ON",
        #         "distance_km": 1.2,
        #         "video_url": "gs://bucket/video_001.mp4",
        #         "confidence_score": 0.85,
        #         "ai_description": "Person matching description walking eastbound",
        #         "ai_summary": "High confidence match identified"
        #     }
        # ]

        return mock_evidence
