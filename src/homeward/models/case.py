from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class CaseStatus(Enum):
    ACTIVE = "Active"
    RESOLVED = "Resolved"
    SUSPENDED = "Suspended"


class CasePriority(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class Location:
    address: str
    city: str
    country: str
    postal_code: str
    latitude: float
    longitude: float


@dataclass
class MissingPersonCase:
    id: str
    name: str
    surname: str
    age: int
    gender: str
    last_seen_date: datetime
    last_seen_location: Location
    status: CaseStatus
    description: str
    photo_url: Optional[str] = None
    created_date: datetime = datetime.now()
    priority: CasePriority = CasePriority.MEDIUM


@dataclass
class KPIData:
    total_cases: int
    active_cases: int
    resolved_cases: int
    sightings_today: int
    success_rate: float
    avg_resolution_days: float