import pytest

from homeward.config import AppConfig, DataSource
from homeward.models.case import CaseStatus, MissingPersonCase
from homeward.services.bigquery_data_service import BigQueryDataService
from homeward.services.mock_data_service import MockDataService
from homeward.services.service_factory import create_data_service


class TestMockDataService:
    """Test cases for MockDataService"""

    def test_mock_service_initialization(self):
        """Test mock service initializes with data"""
        service = MockDataService()

        assert service is not None
        assert len(service._cases) > 0
        assert service._kpi_data is not None

    def test_get_all_cases(self):
        """Test getting all cases without filter"""
        service = MockDataService()
        cases = service.get_cases()

        assert len(cases) > 0
        assert all(isinstance(case, MissingPersonCase) for case in cases)

    def test_get_cases_by_status_filter(self):
        """Test filtering cases by status"""
        service = MockDataService()

        # Test active cases
        active_cases = service.get_cases(status_filter="Active")
        assert all(case.status == CaseStatus.ACTIVE for case in active_cases)

        # Test with invalid status - should return all cases
        all_cases = service.get_cases(status_filter="InvalidStatus")
        assert len(all_cases) == len(service._cases)

    def test_get_cases_no_filter(self):
        """Test getting cases with None filter"""
        service = MockDataService()

        cases_no_filter = service.get_cases(status_filter=None)
        all_cases = service.get_cases()

        assert len(cases_no_filter) == len(all_cases)

    def test_get_kpi_data(self):
        """Test getting KPI data"""
        service = MockDataService()
        kpi_data = service.get_kpi_data()

        assert kpi_data is not None
        assert kpi_data.total_cases >= 0
        assert kpi_data.active_cases >= 0
        assert kpi_data.resolved_cases >= 0
        assert kpi_data.sightings_today >= 0
        assert 0.0 <= kpi_data.success_rate <= 100.0
        assert kpi_data.avg_resolution_days >= 0.0

    def test_get_case_by_id_existing(self):
        """Test getting an existing case by ID"""
        service = MockDataService()
        cases = service.get_cases()

        if cases:
            first_case = cases[0]
            found_case = service.get_case_by_id(first_case.id)

            assert found_case is not None
            assert found_case.id == first_case.id
            assert found_case == first_case

    def test_get_case_by_id_non_existing(self):
        """Test getting a non-existing case by ID"""
        service = MockDataService()
        found_case = service.get_case_by_id("NON_EXISTING_ID")

        assert found_case is None

    def test_create_case(self, sample_case):
        """Test creating a new case"""
        service = MockDataService()
        initial_count = len(service._cases)

        case_id = service.create_case(sample_case)

        assert case_id == sample_case.id
        assert len(service._cases) == initial_count + 1
        assert sample_case in service._cases

    def test_create_multiple_cases(self, sample_cases):
        """Test creating multiple cases"""
        service = MockDataService()
        initial_count = len(service._cases)

        for case in sample_cases[:3]:  # Add first 3 cases
            service.create_case(case)

        assert len(service._cases) == initial_count + 3

    def test_data_persistence_across_calls(self):
        """Test that data persists across multiple calls"""
        service = MockDataService()

        # Get data multiple times
        cases1 = service.get_cases()
        kpi1 = service.get_kpi_data()
        cases2 = service.get_cases()
        kpi2 = service.get_kpi_data()

        # Should be the same
        assert len(cases1) == len(cases2)
        assert kpi1 == kpi2


class TestBigQueryDataService:
    """Test cases for BigQueryDataService"""

    def test_bigquery_service_initialization(self, test_config):
        """Test BigQuery service initialization"""
        service = BigQueryDataService(test_config)

        assert service is not None
        assert service.config == test_config

    def test_bigquery_methods_not_implemented(self, test_config):
        """Test that BigQuery methods raise NotImplementedError"""
        service = BigQueryDataService(test_config)

        with pytest.raises(NotImplementedError):
            service.get_cases()

        with pytest.raises(NotImplementedError):
            service.get_kpi_data()

        with pytest.raises(NotImplementedError):
            service.get_case_by_id("MP001")

        # create_case is now implemented, but will fail with None input
        with pytest.raises(AttributeError):
            service.create_case(None)


class TestServiceFactory:
    """Test cases for service factory"""

    def test_create_mock_data_service(self):
        """Test creating mock data service via factory"""
        config = AppConfig(data_source=DataSource.MOCK, version="0.1.0")

        service = create_data_service(config)

        assert isinstance(service, MockDataService)

    def test_create_bigquery_data_service(self):
        """Test creating BigQuery data service via factory"""
        config = AppConfig(
            data_source=DataSource.BIGQUERY,
            version="0.1.0",
            bigquery_project_id="test-project",
        )

        service = create_data_service(config)

        assert isinstance(service, BigQueryDataService)
        assert service.config == config

    def test_invalid_data_source(self):
        """Test factory with invalid data source"""
        # This would require modifying the enum, so we'll test the error handling
        config = AppConfig(
            data_source=DataSource.MOCK,  # Use valid source
            version="0.1.0",
        )

        # Temporarily modify the data source to an invalid value
        config.data_source = "invalid_source"

        with pytest.raises(ValueError, match="Unknown data source"):
            create_data_service(config)


class TestDataServiceInterface:
    """Test cases for data service interface compliance"""

    def test_mock_service_implements_interface(self):
        """Test that MockDataService implements all required methods"""
        service = MockDataService()

        # Check that all abstract methods are implemented
        assert hasattr(service, "get_cases")
        assert hasattr(service, "get_kpi_data")
        assert hasattr(service, "get_case_by_id")
        assert hasattr(service, "create_case")

        # Check that methods are callable
        assert callable(service.get_cases)
        assert callable(service.get_kpi_data)
        assert callable(service.get_case_by_id)
        assert callable(service.create_case)

    def test_bigquery_service_implements_interface(self, test_config):
        """Test that BigQueryDataService implements all required methods"""
        service = BigQueryDataService(test_config)

        # Check that all abstract methods are implemented
        assert hasattr(service, "get_cases")
        assert hasattr(service, "get_kpi_data")
        assert hasattr(service, "get_case_by_id")
        assert hasattr(service, "create_case")

        # Check that methods are callable (even if not implemented)
        assert callable(service.get_cases)
        assert callable(service.get_kpi_data)
        assert callable(service.get_case_by_id)
        assert callable(service.create_case)


class TestEmptyDataService:
    """Test cases for empty data scenarios"""

    def test_empty_service_behavior(self, empty_data_service):
        """Test service behavior with no data"""
        # Test empty cases
        cases = empty_data_service.get_cases()
        assert len(cases) == 0

        # Test empty KPI data
        kpi_data = empty_data_service.get_kpi_data()
        assert kpi_data.total_cases == 0
        assert kpi_data.active_cases == 0
        assert kpi_data.resolved_cases == 0

        # Test non-existing case
        case = empty_data_service.get_case_by_id("MP001")
        assert case is None

    def test_filtered_cases_empty_result(self, empty_data_service):
        """Test filtering when no cases match"""
        # Test with active filter on empty service
        active_cases = empty_data_service.get_cases(status_filter="Active")
        assert len(active_cases) == 0

        # Test with resolved filter on empty service
        resolved_cases = empty_data_service.get_cases(status_filter="Resolved")
        assert len(resolved_cases) == 0
