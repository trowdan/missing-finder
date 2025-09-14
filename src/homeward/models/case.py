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
    postal_code: Optional[str]
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def get_full_address(self) -> str:
        """
        Construct a full address string for geocoding

        Returns:
            Formatted full address string
        """
        address_parts = []

        if self.address and self.address.strip():
            address_parts.append(self.address.strip())

        if self.city and self.city.strip():
            address_parts.append(self.city.strip())

        if self.postal_code and self.postal_code.strip():
            address_parts.append(self.postal_code.strip())

        if self.country and self.country.strip():
            address_parts.append(self.country.strip())

        return ", ".join(address_parts)

    def has_coordinates(self) -> bool:
        """
        Check if the location has valid coordinates

        Returns:
            True if both latitude and longitude are not None
        """
        return self.latitude is not None and self.longitude is not None

    def update_coordinates(self, latitude: float, longitude: float):
        """
        Update the location coordinates

        Args:
            latitude: New latitude value
            longitude: New longitude value
        """
        self.latitude = latitude
        self.longitude = longitude


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


class SightingSourceType(Enum):
    WITNESS = "Witness"
    MANUAL_ENTRY = "Manual_Entry"
    OTHER = "Other"


class SightingConfidenceLevel(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class SightingStatus(Enum):
    NEW = "New"
    UNDER_REVIEW = "Under_Review"
    VERIFIED = "Verified"
    FALSE_POSITIVE = "False_Positive"
    ARCHIVED = "Archived"


class SightingPriority(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class Sighting:
    # Required fields (no default values)
    id: str
    sighted_date: datetime  # This will be split into date and time in BigQuery
    sighted_location: Location  # Address, city, country, postal_code, lat, lng
    description: str  # Required field
    confidence_level: SightingConfidenceLevel  # Required field
    source_type: SightingSourceType  # Required field

    # Optional fields (with default values)
    sighting_number: Optional[str] = None

    # Person Description
    apparent_gender: Optional[str] = None
    apparent_age_range: Optional[str] = None
    height_estimate: Optional[float] = None  # in cm
    weight_estimate: Optional[float] = None  # in kg
    hair_color: Optional[str] = None
    eye_color: Optional[str] = None
    clothing_description: Optional[str] = None
    distinguishing_features: Optional[str] = None

    # Sighting Details
    circumstances: Optional[str] = None
    photo_url: Optional[str] = None
    video_url: Optional[str] = None

    # Source Information
    witness_name: Optional[str] = None
    witness_phone: Optional[str] = None
    witness_email: Optional[str] = None
    video_analytics_result_id: Optional[str] = None

    # Status and Processing
    status: SightingStatus = SightingStatus.NEW
    priority: SightingPriority = SightingPriority.MEDIUM
    verified: bool = False

    # Metadata
    created_date: datetime = datetime.now()
    updated_date: Optional[datetime] = None
    created_by: Optional[str] = None
    notes: Optional[str] = None

    # AI-Generated Content - these will be populated by BigQuery
    ml_summary: Optional[str] = None
    ml_summary_embedding: Optional[list[float]] = None


@dataclass
class KPIData:
    total_cases: int
    active_cases: int
    resolved_cases: int
    sightings_today: int
    success_rate: float
    avg_resolution_days: float
