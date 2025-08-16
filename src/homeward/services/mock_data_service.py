from typing import List, Optional
from homeward.models.case import MissingPersonCase, KPIData, CaseStatus
from homeward.services.data_service import DataService
from homeward.services.mock_data import get_mock_cases, get_mock_kpi_data


class MockDataService(DataService):
    """Mock implementation of DataService for development and testing"""
    
    def __init__(self):
        self._cases = get_mock_cases()
        self._kpi_data = get_mock_kpi_data()
    
    def get_cases(self, status_filter: Optional[str] = None) -> List[MissingPersonCase]:
        """Get missing person cases, optionally filtered by status"""
        if status_filter is None:
            return self._cases
        
        try:
            status_enum = CaseStatus(status_filter)
            return [case for case in self._cases if case.status == status_enum]
        except ValueError:
            return self._cases
    
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