/* Video Analytics Results Table Creation Script for BigQuery
   This table stores the raw results from AI visual intelligence insights before they are converted to sightings
   Contains detected persons from surveillance footage that can be reviewed and matched to cases */

CREATE TABLE IF NOT EXISTS `homeward.video_analytics_results` (
  /* Primary identifiers */
  id STRING NOT NULL OPTIONS(description="Unique analytics result identifier"),
  analysis_session_id STRING NOT NULL OPTIONS(description="Identifier for the analysis batch/session"),
  
  /* Video Source Information */
  video_url STRING NOT NULL OPTIONS(description="URL/path to the analyzed video file"),
  video_filename STRING NOT NULL OPTIONS(description="Original filename of the video"),
  camera_id STRING NOT NULL OPTIONS(description="Camera identifier from video filename"),
  video_timestamp TIMESTAMP NOT NULL OPTIONS(description="Timestamp from video filename (YYYYMMDDHHMMSS)"),
  video_latitude FLOAT64 NOT NULL OPTIONS(description="Camera latitude from video filename"),
  video_longitude FLOAT64 NOT NULL OPTIONS(description="Camera longitude from video filename"),
  video_geo GEOGRAPHY OPTIONS(description="SFS position of camera location"),
  camera_type STRING NOT NULL OPTIONS(description="Camera type from video filename"),
  video_resolution STRING NOT NULL OPTIONS(description="Video resolution from video filename"),
  
  /* Detection Information */
  detection_timestamp FLOAT64 NOT NULL OPTIONS(description="Timestamp within video when person was detected (seconds)"),
  detection_frame_number INT64 OPTIONS(description="Frame number where detection occurred"),
  detection_confidence FLOAT64 NOT NULL OPTIONS(description="AI confidence score for person detection (0.0-1.0)"),
  
  /* AI Model Information */
  model_name STRING NOT NULL OPTIONS(description="Name/version of AI model used"),
  model_version STRING OPTIONS(description="Version of the AI model"),
  analysis_parameters STRING OPTIONS(description="JSON string of analysis parameters used"),
  /* Metadata */
  created_date TIMESTAMP NOT NULL OPTIONS(description="Date and time when analysis result was created"),
  processed_date TIMESTAMP OPTIONS(description="Date and time when video was processed"),
  created_by STRING NOT NULL OPTIONS(description="System/service that created the result"),
)
PARTITION BY DATE(video_timestamp)
CLUSTER BY camera_id, created_date
OPTIONS(
  description="Table storing raw AI visual intelligence insights before conversion to sightings",
  labels=[("environment", "hackathon"), ("application", "homeward"), ("data_type", "video_analytics")]
);

/* Sample data validation constraints (enforced at application level)
   - detection_confidence: 0.0-1.0
   - detection_timestamp: >= 0.0
   - image_quality_score: 0.0-1.0 (if provided)
   - image_blur_score: 0.0-1.0 (if provided)
   - face_confidence: 0.0-1.0 (if provided)
   - overall_quality_score: 0.0-1.0 (if provided)
   - usability_score: 0.0-1.0 (if provided)
   - false_positive_probability: 0.0-1.0 (if provided)
   - apparent_gender: 'Male', 'Female', 'Other', 'Unknown'
   - lighting_conditions: 'Good', 'Fair', 'Poor', 'Night'
   - crowd_density: 'Low', 'Medium', 'High' */

/* Business Rules:
   1. Results can be filtered by time range, location, and confidence scores
   2. High confidence detections (>0.8) should be prioritized
   3. This table stores raw AI analysis results before human review */