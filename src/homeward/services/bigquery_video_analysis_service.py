import json
import logging
from datetime import datetime
from typing import Optional

from google.cloud import bigquery

from homeward.models.video_analysis import VideoAnalysisRequest, VideoAnalysisResult
from homeward.services.video_analysis_service import VideoAnalysisService

logger = logging.getLogger(__name__)


class BigQueryVideoAnalysisService(VideoAnalysisService):
    """BigQuery implementation of VideoAnalysisService using Gemini AI for video analysis"""

    def __init__(self, project_id: str, dataset_id: str, connection_id: str = None):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.connection_id = connection_id or f"{project_id}.us-central1.homeward_gcp_connection"
        self.client = bigquery.Client(project=project_id)

    def analyze_videos(
        self, request: VideoAnalysisRequest, missing_person_data: dict = None
    ) -> tuple[list[VideoAnalysisResult], dict]:
        """
        Perform AI video analysis using BigQuery and Gemini

        Returns:
            tuple: (video_results, analysis_stats) where analysis_stats contains:
                - total_analyzed: Total number of videos processed
                - matches_found: Number of videos where person was found
                - no_person_found: Number of videos where no person was found
                - errors: Number of videos that had processing errors
        """
        try:
            # Build the video analysis prompt from the missing person case data
            video_analysis_prompt = self._build_analysis_prompt(request, missing_person_data)

            # Build BigQuery query for video analysis
            query = self._build_video_analysis_query(request, video_analysis_prompt)

            logger.info(f"Executing BigQuery video analysis for case {request.case_id}")

            # Execute the BigQuery query with timeout
            query_job = self.client.query(query)

            # Wait for results with a longer timeout since video analysis with Gemini can take time
            # Set timeout to 300 seconds (5 minutes) for video analysis
            try:
                results = query_job.result(timeout=300)
            except Exception as timeout_error:
                logger.error(f"BigQuery video analysis query timed out after 300 seconds: {timeout_error}")
                raise TimeoutError("Video analysis query timed out. This may happen with large video datasets. Try reducing the search time range or area.") from timeout_error

            video_results = []
            total_videos_analyzed = 0
            videos_with_person_found = 0
            videos_with_no_person = 0
            videos_with_errors = 0

            for row in results:
                total_videos_analyzed += 1
                try:
                    # Parse the AI analysis result
                    ai_result_text = row.result

                    # Try to parse as JSON
                    if ai_result_text:
                        analysis_result = self._parse_ai_result(ai_result_text)

                        if analysis_result:
                            if analysis_result.get("personFound"):
                                videos_with_person_found += 1
                                # Extract video metadata from URI
                                video_metadata = self._extract_video_metadata(row.uri)

                                # Create VideoAnalysisResult
                                video_result = VideoAnalysisResult(
                                    id=f"video_{hash(row.uri)}",
                                    timestamp=video_metadata.get("timestamp", request.start_date),
                                    latitude=video_metadata.get("latitude", request.last_seen_latitude),
                                    longitude=video_metadata.get("longitude", request.last_seen_longitude),
                                    address=video_metadata.get("address", "Unknown"),
                                    distance_from_last_seen=self._calculate_distance(
                                        video_metadata.get("latitude", request.last_seen_latitude),
                                        video_metadata.get("longitude", request.last_seen_longitude),
                                        request.last_seen_latitude,
                                        request.last_seen_longitude
                                    ),
                                    video_url=row.uri,
                                    confidence_score=analysis_result.get("confidenceScore", 0.0),
                                    ai_description=analysis_result.get("summaryOfFindings", "AI analysis result"),
                                    camera_id=video_metadata.get("camera_id", "Unknown"),
                                    camera_type=video_metadata.get("camera_type", "Unknown")
                                )
                                video_results.append(video_result)
                            else:
                                videos_with_no_person += 1
                                logger.debug(f"Video {row.uri}: No person found - {analysis_result.get('matchJustification', 'No justification provided')}")
                        else:
                            videos_with_errors += 1
                            logger.warning(f"Failed to parse AI result for video {row.uri}")
                    else:
                        videos_with_errors += 1
                        logger.warning(f"Empty AI result for video {row.uri}")

                except Exception as e:
                    videos_with_errors += 1
                    logger.warning(f"Failed to process video analysis result for {row.uri}: {e}")
                    continue

            # Sort by confidence score (highest first)
            video_results.sort(key=lambda x: x.confidence_score, reverse=True)

            logger.info(f"Video analysis complete for case {request.case_id}: "
                       f"{total_videos_analyzed} videos analyzed, "
                       f"{videos_with_person_found} matches found, "
                       f"{videos_with_no_person} with no person, "
                       f"{videos_with_errors} errors")

            # Prepare analysis stats for the UI
            analysis_stats = {
                'total_analyzed': total_videos_analyzed,
                'matches_found': videos_with_person_found,
                'no_person_found': videos_with_no_person,
                'errors': videos_with_errors
            }

            return video_results, analysis_stats

        except Exception as e:
            logger.error(f"Video analysis failed for case {request.case_id}: {e}")
            raise

    def _build_analysis_prompt(self, request: VideoAnalysisRequest, missing_person_data: dict = None) -> str:
        """Build the video analysis prompt template based on missing person data"""

        # Extract person data or use defaults from the demo notebook format
        gender = missing_person_data.get("gender", "Unknown") if missing_person_data else "Unknown"
        age = str(missing_person_data.get("age", "Unknown")) if missing_person_data else "Unknown"
        height = str(missing_person_data.get("height", "Unknown")) if missing_person_data else "Unknown"
        weight = str(missing_person_data.get("weight", "Unknown")) if missing_person_data else "Unknown"
        hair_color = missing_person_data.get("hair_color", "Unknown") if missing_person_data else "Unknown"
        clothing_description = missing_person_data.get("clothing_description", "Unknown") if missing_person_data else "Unknown"
        distinguishing_marks = missing_person_data.get("distinguishing_marks", "None") if missing_person_data else "None"

        # Build height/weight description like in demo notebook
        build_height = f"{height}m, {weight}kg" if height != "Unknown" and weight != "Unknown" else "Unknown"

        # Extract clothing parts from description (simplified for demo)
        clothing_top = "Unknown"
        clothing_bottom = "Unknown"
        footwear = "Unknown"
        accessories = "None"

        if clothing_description and clothing_description != "Unknown":
            # Simple parsing - in real implementation this could be more sophisticated
            clothing_top = clothing_description
            clothing_bottom = "Unknown"

        # Use the exact VIDEO_ANALYSIS_PROMPT from demo notebook
        VIDEO_ANALYSIS_PROMPT = """# ROLE AND GOAL
You are a state-of-the-art AI visual analysis system with an expert specialization in human identification within low-quality video footage.
Your primary mission is to analyze the provided video for a critical missing person case with the highest degree of accuracy and diligence.
You must be methodical and detail-oriented in your analysis and reporting.

# TASK CONTEXT
This is a high-priority, time-sensitive analysis.
The provided video is a low-quality security footage from the street, where people are walking around.
The objective is to determine if the missing person is visible in this video, and if so, to extract all relevant information about their presence.

# MISSING PERSON DATA
Carefully analyze the following description of the missing person. Every detail is crucial.

- **Gender:** `{gender}`
- **Approximate Age:** `{age}`
- **Build - Height:** `{build_height}`
- **Hair Color and Style:** `{hair}`
- **Clothing (Top):** `{clothing_top}`
- **Clothing (Bottom):** `{clothing_botton}`
- **Footwear:** `{footwear}`
- **Accessories:** `{accessories}`
- **Distinguishing Features:** `{features}`

# ANALYSIS INSTRUCTIONS
You must perform the following steps in your analysis:

1.  **Full Video Scan:** Meticulously review the entire video from start to finish. Do not stop after a potential first match; the person may appear multiple times.
2.  **Feature Matching:** Compare every individual in the video against the `MISSING PERSON DATA`. Assess matches based on all available criteria: clothing, build, hair, accessories, and any visible distinguishing features or mannerisms.
3.  **Justification:** You MUST provide a step-by-step justification for your match. List the features that matched, the features that did not match, and any features that were ambiguous or obscured (e.g., 'Face was unclear, but clothing is a 90% match').
4.  **Contextual Analysis (If Found):** If you identify the person with confidence:
    -   Note the exact timestamp(s) (in `HH:MM:SS` format) of their appearance.
    -   Document their behavior, actions, and movements throughout their appearance in the video.
5. **Confidence Score (If Found):** If you identify a person with confidence:
    -   Return the confidence score of the finding in the range 0.0 to 1.0
"""

        # Use the exact VIDEO_ANALYSIS_PROMPT_OUTPUT from demo notebook
        VIDEO_ANALYSIS_PROMPT_OUTPUT = """
# OUTPUT FORMAT
Your final output MUST be a single JSON object. Do not include any text or explanations outside of this JSON structure.

**If the person is found:**
```json
{
  "personFound": true,
  "confidenceScore": 0.85,
  "matchJustification": "A detailed explanation of why the confidence score was given. List all matching and non-matching features. Example: 'Confidence is high due to a perfect match on the red hooded sweatshirt, blue jeans, and black backpack. Subject's build and hair color are also consistent. Face was partially obscured, preventing a 1.0 score.'",
  "summaryOfFindings": "A concise, human-readable summary of the events. Example: 'The missing person was spotted at 00:14:32 walking east on the station platform. They appeared to be alone and were walking at a normal pace while looking at their phone.'",
  "appearances": [
    {
      "timestampStart": "HH:MM:SS",
      "timestampEnd": "HH:MM:SS",
      "actionsAndBehavior": "Detailed description of what the subject is doing during this specific timeframe.",
      "directionOfTravel": "e.g., Northbound, Towards the exit, Away from the camera",
      "companions": [
        {
          "description": "Detailed description of companion 1: Gender, estimated age, build, hair, clothing (top, bottom, shoes), and any notable accessories or features."
        }
      ]
    }
  ]
}
```
**If the person is not found:**
```json
{
  "personFound": false,
  "confidenceScore": 0,
  "matchJustification": "",
  "summaryOfFindings": "",
  "appearances": [],
  "companions": []
}
```
"""

        # Format the prompt with the missing person data (just like in demo notebook)
        formatted_prompt = VIDEO_ANALYSIS_PROMPT.format(
            gender=gender,
            age=age,
            build_height=build_height,
            hair=hair_color,
            clothing_top=clothing_top,
            clothing_botton=clothing_bottom,  # Note: keeping the typo from demo notebook
            footwear=footwear,
            accessories=accessories,
            features=distinguishing_marks,
        )

        # Combine with output format (just like in demo notebook)
        complete_prompt = formatted_prompt + "\n" + VIDEO_ANALYSIS_PROMPT_OUTPUT

        return complete_prompt

    def _build_video_analysis_query(self, request: VideoAnalysisRequest, video_analysis_prompt: str) -> str:
        """Build the BigQuery query for video analysis"""

        # Escape the prompt for SQL
        escaped_prompt = video_analysis_prompt.encode("unicode-escape").replace(b'"', b'\\"').decode("utf-8")

        query = f"""
        SELECT
          uri,
          AI.GENERATE(
            (
              "{escaped_prompt}",
              "\\n# RECORDING:  ",
              OBJ.GET_ACCESS_URL(ref, 'r')
            ),
            connection_id => '{self.connection_id}',
            endpoint => 'gemini-2.5-pro',
            model_params => JSON '{{"generation_config": {{"temperature": 0}}}}'
          ).result
        FROM `{self.project_id}.{self.dataset_id}.video_objects`
        WHERE 1=1
        """

        # Add temporal filtering if needed
        # Note: This would require metadata extraction from video filenames or separate metadata table

        return query

    def _parse_ai_result(self, ai_result_text: str) -> Optional[dict]:
        """Parse the AI analysis result JSON"""
        try:
            # The AI result might have extra text, try to extract JSON
            if "```json" in ai_result_text:
                # Extract JSON from markdown code block
                start = ai_result_text.find("```json") + 7
                end = ai_result_text.find("```", start)
                json_text = ai_result_text[start:end].strip()
            elif ai_result_text.strip().startswith("{"):
                # Assume it's pure JSON
                json_text = ai_result_text.strip()
            else:
                # Try to find JSON-like content
                start = ai_result_text.find("{")
                end = ai_result_text.rfind("}") + 1
                if start != -1 and end > start:
                    json_text = ai_result_text[start:end]
                else:
                    return None

            return json.loads(json_text)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse AI result as JSON: {e}")
            return None

    def _extract_video_metadata(self, video_uri: str) -> dict:
        """Extract metadata from video URI/filename"""
        # Expected format: CameraID_YYYYMMDDHHMMSS_LATITUDE_LONGITUDE_CAMERATYPE_RESOLUTION.mp4
        try:
            filename = video_uri.split("/")[-1]
            parts = filename.replace(".mp4", "").split("_")

            if len(parts) >= 6:
                camera_id = parts[0]
                timestamp_str = parts[1]
                latitude = float(parts[2])
                longitude = float(parts[3])
                camera_type = parts[4]

                # Parse timestamp
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")

                return {
                    "camera_id": camera_id,
                    "timestamp": timestamp,
                    "latitude": latitude,
                    "longitude": longitude,
                    "camera_type": camera_type,
                    "address": f"Camera {camera_id} Location"
                }
        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to parse video metadata from {video_uri}: {e}")

        return {
            "camera_id": "Unknown",
            "timestamp": datetime.now(),
            "latitude": 0.0,
            "longitude": 0.0,
            "camera_type": "Unknown",
            "address": "Unknown Location"
        }

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers using Haversine formula"""
        from math import radians, sin, cos, sqrt, atan2

        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        # Earth radius in kilometers
        R = 6371.0
        distance = R * c

        return distance

    def add_to_evidence(self, result_id: str, case_id: str) -> bool:
        """Add analysis result to case evidence in BigQuery"""
        try:
            # Insert into video_analytics_results table
            query = f"""
            INSERT INTO `{self.project_id}.{self.dataset_id}.video_analytics_results`
            (case_id, result_id, created_date, status)
            VALUES (@case_id, @result_id, CURRENT_TIMESTAMP(), 'Evidence')
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("case_id", "STRING", case_id),
                    bigquery.ScalarQueryParameter("result_id", "STRING", result_id),
                ]
            )

            query_job = self.client.query(query, job_config=job_config)
            query_job.result()  # Wait for completion

            logger.info(f"Added video analysis result {result_id} to evidence for case {case_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add evidence for case {case_id}: {e}")
            return False

    def get_video_url(self, result_id: str) -> str:
        """Get the video URL from BigQuery/GCS"""
        try:
            # Query the video_objects table to get the URI
            query = f"""
            SELECT uri
            FROM `{self.project_id}.{self.dataset_id}.video_objects`
            WHERE CAST(FARM_FINGERPRINT(uri) AS STRING) = @result_id
            LIMIT 1
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("result_id", "STRING", result_id),
                ]
            )

            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()

            for row in results:
                return row.uri

            return ""

        except Exception as e:
            logger.error(f"Failed to get video URL for result {result_id}: {e}")
            return ""