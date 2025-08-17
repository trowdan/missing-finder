from abc import ABC, abstractmethod

from homeward.models.video_analysis import VideoAnalysisRequest, VideoAnalysisResult


class VideoAnalysisService(ABC):
    """Abstract base class for video analysis services"""

    @abstractmethod
    def analyze_videos(self, request: VideoAnalysisRequest) -> list[VideoAnalysisResult]:
        """
        Perform AI video analysis and return results

        Args:
            request: VideoAnalysisRequest containing search parameters

        Returns:
            List of VideoAnalysisResult objects sorted by confidence
        """
        pass

    @abstractmethod
    def add_to_evidence(self, result_id: str, case_id: str) -> bool:
        """
        Add analysis result to case evidence

        Args:
            result_id: ID of the video analysis result
            case_id: ID of the missing person case

        Returns:
            True if successfully added to evidence, False otherwise
        """
        pass

    @abstractmethod
    def get_video_url(self, result_id: str) -> str:
        """
        Get the video URL for a specific analysis result

        Args:
            result_id: ID of the video analysis result

        Returns:
            URL to access the video
        """
        pass
