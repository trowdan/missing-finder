from datetime import datetime, timedelta

from homeward.models.case import (
    CasePriority,
    CaseStatus,
    KPIData,
    Location,
    MissingPersonCase,
)


class TestLocation:
    """Test cases for Location model"""

    def test_location_creation(self):
        """Test creating a location with all fields"""
        location = Location(
            address="Via Roma 15",
            city="Milano",
            country="Italy",
            postal_code="20121",
            latitude=45.4654,
            longitude=9.1859,
        )

        assert location.address == "Via Roma 15"
        assert location.city == "Milano"
        assert location.country == "Italy"
        assert location.postal_code == "20121"
        assert location.latitude == 45.4654
        assert location.longitude == 9.1859

    def test_location_with_negative_coordinates(self):
        """Test location with negative coordinates"""
        location = Location(
            address="Test Street",
            city="Test City",
            country="Test Country",
            postal_code="12345",
            latitude=-45.4654,
            longitude=-9.1859,
        )

        assert location.latitude == -45.4654
        assert location.longitude == -9.1859

    def test_location_equality(self):
        """Test location equality comparison"""
        location1 = Location(
            address="Via Roma 15",
            city="Milano",
            country="Italy",
            postal_code="20121",
            latitude=45.4654,
            longitude=9.1859,
        )

        location2 = Location(
            address="Via Roma 15",
            city="Milano",
            country="Italy",
            postal_code="20121",
            latitude=45.4654,
            longitude=9.1859,
        )

        assert location1 == location2


class TestCaseStatus:
    """Test cases for CaseStatus enum"""

    def test_case_status_values(self):
        """Test all case status enum values"""
        assert CaseStatus.ACTIVE.value == "Active"
        assert CaseStatus.RESOLVED.value == "Resolved"
        assert CaseStatus.SUSPENDED.value == "Suspended"

    def test_case_status_from_string(self):
        """Test creating case status from string"""
        assert CaseStatus("Active") == CaseStatus.ACTIVE
        assert CaseStatus("Resolved") == CaseStatus.RESOLVED
        assert CaseStatus("Suspended") == CaseStatus.SUSPENDED


class TestCasePriority:
    """Test cases for CasePriority enum"""

    def test_case_priority_values(self):
        """Test all case priority enum values"""
        assert CasePriority.HIGH.value == "High"
        assert CasePriority.MEDIUM.value == "Medium"
        assert CasePriority.LOW.value == "Low"

    def test_case_priority_from_string(self):
        """Test creating case priority from string"""
        assert CasePriority("High") == CasePriority.HIGH
        assert CasePriority("Medium") == CasePriority.MEDIUM
        assert CasePriority("Low") == CasePriority.LOW


class TestMissingPersonCase:
    """Test cases for MissingPersonCase model"""

    def test_case_creation_with_all_fields(self, sample_location):
        """Test creating a case with all fields"""
        case_date = datetime.now() - timedelta(days=1)
        created_date = datetime.now()

        case = MissingPersonCase(
            id="MP001",
            name="John",
            surname="Doe",
            date_of_birth=datetime(1994, 1, 15),
            gender="Male",
            last_seen_date=case_date,
            last_seen_location=sample_location,
            status=CaseStatus.ACTIVE,
            circumstances="Test circumstances",
            reporter_name="Jane Doe",
            reporter_phone="+39 333 1234567",
            relationship="Wife",
            description="Test case",
            photo_url="http://example.com/photo.jpg",
            created_date=created_date,
            priority=CasePriority.HIGH,
        )

        assert case.id == "MP001"
        assert case.name == "John"
        assert case.surname == "Doe"
        assert case.date_of_birth == datetime(1994, 1, 15)
        assert case.gender == "Male"
        assert case.last_seen_date == case_date
        assert case.last_seen_location == sample_location
        assert case.status == CaseStatus.ACTIVE
        assert case.description == "Test case"
        assert case.photo_url == "http://example.com/photo.jpg"
        assert case.created_date == created_date
        assert case.priority == CasePriority.HIGH

    def test_case_creation_with_defaults(self, sample_location):
        """Test creating a case with default values"""
        case_date = datetime.now() - timedelta(days=1)

        case = MissingPersonCase(
            id="MP001",
            name="John",
            surname="Doe",
            date_of_birth=datetime(1994, 1, 15),
            gender="Male",
            last_seen_date=case_date,
            last_seen_location=sample_location,
            status=CaseStatus.ACTIVE,
            circumstances="Test circumstances",
            reporter_name="Jane Doe",
            reporter_phone="+39 333 1234567",
            relationship="Wife",
            description="Test case",
        )

        assert case.photo_url is None
        assert case.priority == CasePriority.MEDIUM
        assert isinstance(case.created_date, datetime)

    def test_case_with_different_ages(self, sample_location):
        """Test cases with different age ranges"""
        case_date = datetime.now() - timedelta(days=1)

        # Child case
        child_case = MissingPersonCase(
            id="MP001",
            name="Child",
            surname="Test",
            date_of_birth=datetime(2012, 3, 10),
            gender="Male",
            last_seen_date=case_date,
            last_seen_location=sample_location,
            status=CaseStatus.ACTIVE,
            circumstances="Child case circumstances",
            reporter_name="Parent Test",
            reporter_phone="+39 333 1111111",
            relationship="Parent",
            description="Child case",
        )

        # Adult case
        adult_case = MissingPersonCase(
            id="MP002",
            name="Adult",
            surname="Test",
            date_of_birth=datetime(1979, 8, 22),
            gender="Female",
            last_seen_date=case_date,
            last_seen_location=sample_location,
            status=CaseStatus.ACTIVE,
            circumstances="Adult case circumstances",
            reporter_name="Spouse Test",
            reporter_phone="+39 333 2222222",
            relationship="Spouse",
            description="Adult case",
        )

        # Senior case
        senior_case = MissingPersonCase(
            id="MP003",
            name="Senior",
            surname="Test",
            date_of_birth=datetime(1949, 11, 5),
            gender="Male",
            last_seen_date=case_date,
            last_seen_location=sample_location,
            status=CaseStatus.ACTIVE,
            circumstances="Senior case circumstances",
            reporter_name="Child Test",
            reporter_phone="+39 333 3333333",
            relationship="Child",
            description="Senior case",
        )

        assert child_case.date_of_birth == datetime(2012, 3, 10)
        assert adult_case.date_of_birth == datetime(1979, 8, 22)
        assert senior_case.date_of_birth == datetime(1949, 11, 5)

    def test_case_equality(self, sample_location):
        """Test case equality comparison"""
        case_date = datetime.now() - timedelta(days=1)

        case1 = MissingPersonCase(
            id="MP001",
            name="John",
            surname="Doe",
            date_of_birth=datetime(1994, 1, 15),
            gender="Male",
            last_seen_date=case_date,
            last_seen_location=sample_location,
            status=CaseStatus.ACTIVE,
            circumstances="Test circumstances",
            reporter_name="Jane Doe",
            reporter_phone="+39 333 1234567",
            relationship="Wife",
            description="Test case",
        )

        case2 = MissingPersonCase(
            id="MP001",
            name="John",
            surname="Doe",
            date_of_birth=datetime(1994, 1, 15),
            gender="Male",
            last_seen_date=case_date,
            last_seen_location=sample_location,
            status=CaseStatus.ACTIVE,
            circumstances="Test circumstances",
            reporter_name="Jane Doe",
            reporter_phone="+39 333 1234567",
            relationship="Wife",
            description="Test case",
        )

        assert case1 == case2


class TestKPIData:
    """Test cases for KPIData model"""

    def test_kpi_data_creation(self):
        """Test creating KPI data"""
        kpi = KPIData(
            total_cases=100,
            active_cases=15,
            resolved_cases=85,
            sightings_today=5,
            success_rate=85.0,
            avg_resolution_days=3.2,
        )

        assert kpi.total_cases == 100
        assert kpi.active_cases == 15
        assert kpi.resolved_cases == 85
        assert kpi.sightings_today == 5
        assert kpi.success_rate == 85.0
        assert kpi.avg_resolution_days == 3.2

    def test_kpi_data_with_zero_values(self):
        """Test KPI data with zero values"""
        kpi = KPIData(
            total_cases=0,
            active_cases=0,
            resolved_cases=0,
            sightings_today=0,
            success_rate=0.0,
            avg_resolution_days=0.0,
        )

        assert kpi.total_cases == 0
        assert kpi.active_cases == 0
        assert kpi.resolved_cases == 0
        assert kpi.sightings_today == 0
        assert kpi.success_rate == 0.0
        assert kpi.avg_resolution_days == 0.0

    def test_kpi_data_calculations(self):
        """Test KPI data consistency"""
        kpi = KPIData(
            total_cases=100,
            active_cases=15,
            resolved_cases=85,
            sightings_today=5,
            success_rate=85.0,
            avg_resolution_days=3.2,
        )

        # Total should equal active + resolved
        assert kpi.total_cases == kpi.active_cases + kpi.resolved_cases

        # Success rate should be calculated from resolved/total
        expected_rate = (kpi.resolved_cases / kpi.total_cases) * 100
        assert kpi.success_rate == expected_rate

    def test_kpi_data_equality(self):
        """Test KPI data equality comparison"""
        kpi1 = KPIData(
            total_cases=100,
            active_cases=15,
            resolved_cases=85,
            sightings_today=5,
            success_rate=85.0,
            avg_resolution_days=3.2,
        )

        kpi2 = KPIData(
            total_cases=100,
            active_cases=15,
            resolved_cases=85,
            sightings_today=5,
            success_rate=85.0,
            avg_resolution_days=3.2,
        )

        assert kpi1 == kpi2
