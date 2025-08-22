from datetime import datetime, timedelta

import pytest

from homeward.config import AppConfig, DataSource
from homeward.models.case import (
    CasePriority,
    CaseStatus,
    KPIData,
    Location,
    MissingPersonCase,
)
from homeward.services.mock_data_service import MockDataService


@pytest.fixture
def sample_location():
    """Create a sample location for testing"""
    return Location(
        address="Via Roma 15",
        city="Milano",
        country="Italy",
        postal_code="20121",
        latitude=45.4654,
        longitude=9.1859,
    )


@pytest.fixture
def sample_case(sample_location):
    """Create a sample missing person case for testing"""
    return MissingPersonCase(
        id="MP001",
        name="Test",
        surname="Person",
        age=30,
        gender="Male",
        last_seen_date=datetime.now() - timedelta(days=1),
        last_seen_location=sample_location,
        status=CaseStatus.ACTIVE,
        description="Test case description",
        priority=CasePriority.HIGH,
    )


@pytest.fixture
def sample_cases(sample_location):
    """Create a list of sample cases for testing"""
    cases = []
    for i in range(12):
        cases.append(
            MissingPersonCase(
                id=f"MP{i + 1:03d}",
                name=f"Person{i + 1}",
                surname=f"Surname{i + 1}",
                age=20 + i,
                gender="Male" if i % 2 == 0 else "Female",
                last_seen_date=datetime.now() - timedelta(days=i + 1),
                last_seen_location=sample_location,
                status=CaseStatus.ACTIVE,
                description=f"Test case {i + 1} description",
                priority=CasePriority.HIGH if i % 3 == 0 else CasePriority.MEDIUM,
            )
        )
    return cases


@pytest.fixture
def sample_kpi_data():
    """Create sample KPI data for testing"""
    return KPIData(
        total_cases=100,
        active_cases=15,
        resolved_cases=85,
        sightings_today=5,
        success_rate=85.0,
        avg_resolution_days=3.2,
    )


@pytest.fixture
def test_config():
    """Create test configuration"""
    return AppConfig(
        data_source=DataSource.MOCK,
        version="0.1.0-test",
        bigquery_project_id="test-project",
        bigquery_dataset="test_dataset",
        gcs_bucket_ingestion="test-ingestion",
        gcs_bucket_processed="test-processed",
    )


@pytest.fixture
def mock_data_service():
    """Create a mock data service for testing"""
    return MockDataService()


@pytest.fixture
def empty_data_service():
    """Create a data service with no cases for testing empty states"""
    service = MockDataService()
    service._cases = []
    service._kpi_data = KPIData(
        total_cases=0,
        active_cases=0,
        resolved_cases=0,
        sightings_today=0,
        success_rate=0.0,
        avg_resolution_days=0.0,
    )
    return service
