from abc import ABC, abstractmethod
from typing import List
from homeward.models.case import MissingPersonCase, KPIData


class DataService(ABC):
    """Abstract base class for data services"""
    
    @abstractmethod
    def get_cases(self, status_filter: str = None) -> List[MissingPersonCase]:
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