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


class SightingStatus(Enum):
    UNVERIFIED = "Unverified"
    VERIFIED = "Verified"
    FALSE_POSITIVE = "False Positive"


class ConfidenceLevel(Enum):
    VERY_HIGH = "Very High - I'm certain it was them"
    HIGH = "High - Very likely it was them"
    MEDIUM = "Medium - Possibly them"
    LOW = "Low - Uncertain but worth reporting"


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
    date_of_birth: datetime  # Required field, age will be calculated from this
    gender: str
    last_seen_date: datetime
    last_seen_location: Location
    status: CaseStatus
    circumstances: str  # Required field
    reporter_name: str  # Required field
    reporter_phone: str  # Required field
    relationship: str  # Required field

    # Optional fields
    case_number: Optional[str] = None
    height: Optional[float] = None  # in cm
    weight: Optional[float] = None  # in kg
    hair_color: Optional[str] = None
    eye_color: Optional[str] = None
    distinguishing_marks: Optional[str] = None
    clothing_description: Optional[str] = None
    medical_conditions: Optional[str] = None
    additional_info: Optional[str] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None
    reporter_email: Optional[str] = None

    # Metadata
    created_date: datetime = datetime.now()
    priority: CasePriority = CasePriority.MEDIUM


@dataclass
class Sighting:
    id: str
    reporter_name: str
    sighting_date: datetime
    sighting_location: Location
    individual_age: Optional[int]
    individual_gender: str
    description: str
    confidence: ConfidenceLevel
    status: SightingStatus
    linked_case_id: Optional[str] = None
    reporter_email: Optional[str] = None
    reporter_phone: Optional[str] = None
    created_date: datetime = datetime.now()


@dataclass
class KPIData:
    total_cases: int
    active_cases: int
    resolved_cases: int
    sightings_today: int
    success_rate: float
    avg_resolution_days: float
