from dataclasses import dataclass
from datetime import datetime


@dataclass
class VideoAnalysisResult:
    """Data model for AI visual intelligence insights"""

    id: str
    timestamp: datetime
    latitude: float
    longitude: float
    address: str
    distance_from_last_seen: float  # in kilometers
    video_url: str
    confidence_score: float  # 0.0 to 1.0
    ai_description: str
    camera_id: str
    camera_type: str

    def get_confidence_percentage(self) -> str:
        """Get confidence as percentage string"""
        return f"{int(self.confidence_score * 100)}%"

    def get_distance_display(self) -> str:
        """Get formatted distance display"""
        if self.distance_from_last_seen < 1:
            return f"{int(self.distance_from_last_seen * 1000)}m"
        else:
            return f"{self.distance_from_last_seen:.1f}km"


@dataclass
class VideoAnalysisRequest:
    """Data model for video analysis request parameters"""

    case_id: str
    start_date: datetime
    end_date: datetime
    time_range: str
    search_radius_km: float
    last_seen_latitude: float
    last_seen_longitude: float
