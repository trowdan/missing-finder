/* Case Sightings Link Table Creation Script for BigQuery
   This table manages the many-to-many relationship between missing person cases and sightings
   A missing person can have multiple sightings, and a sighting can be linked to multiple cases
   However, only one link per sighting can be confirmed as a positive match */

CREATE TABLE IF NOT EXISTS `homeward.case_sightings` (
  /* Primary identifiers */
  id STRING NOT NULL OPTIONS(description="Unique link identifier"),
  missing_person_id STRING NOT NULL OPTIONS(description="Reference to missing_persons.id"),
  sighting_id STRING NOT NULL OPTIONS(description="Reference to sightings.id"),
  
  /* Link Details */
  match_confidence FLOAT64 NOT NULL OPTIONS(description="Confidence score of the match (0.0-1.0)"),
  match_type STRING NOT NULL OPTIONS(description="How the match was identified (Manual/AI_Analysis/Tip/Investigation)"),
  match_reason STRING OPTIONS(description="Detailed explanation of why this sighting matches this case"),
  
  /* Status and Confirmation */
  status STRING NOT NULL OPTIONS(description="Link status (Potential/Under_Review/Confirmed/Rejected)"),
  confirmed BOOLEAN NOT NULL DEFAULT FALSE OPTIONS(description="Whether this link is confirmed as a positive match"),
  confirmed_by STRING OPTIONS(description="User who confirmed the match"),
  confirmed_date TIMESTAMP OPTIONS(description="Date and time when match was confirmed"),
  
  /* Analysis Details */
  similarity_score FLOAT64 OPTIONS(description="AI-calculated similarity score if applicable"),
  physical_match_score FLOAT64 OPTIONS(description="Score for physical characteristics match"),
  temporal_match_score FLOAT64 OPTIONS(description="Score for temporal proximity"),
  geographical_match_score FLOAT64 OPTIONS(description="Score for geographical proximity"),
  
  /* Investigation Details */
  investigated BOOLEAN NOT NULL DEFAULT FALSE OPTIONS(description="Whether this link has been investigated"),
  investigation_notes STRING OPTIONS(description="Notes from investigation of this potential match"),
  investigator_name STRING OPTIONS(description="Name of investigator who reviewed this link"),
  investigation_date TIMESTAMP OPTIONS(description="Date when investigation was completed"),
  
  /* Priority and Workflow */
  priority STRING NOT NULL OPTIONS(description="Priority level for reviewing this link (High/Medium/Low)"),
  requires_review BOOLEAN NOT NULL DEFAULT TRUE OPTIONS(description="Whether this link requires human review"),
  review_notes STRING OPTIONS(description="Notes from reviewers"),
  
  /* Metadata */
  created_date TIMESTAMP NOT NULL OPTIONS(description="Date and time when link was created"),
  updated_date TIMESTAMP NOT NULL OPTIONS(description="Date and time when link was last updated"),
  created_by STRING OPTIONS(description="User or system that created the link"),
  
  /* Distance and Time Calculations */
  distance_km FLOAT64 OPTIONS(description="Distance in kilometers between last seen and sighting locations"),
  time_difference_hours INT64 OPTIONS(description="Hours between last seen time and sighting time")
)
PARTITION BY DATE(created_date)
CLUSTER BY status, confirmed, priority, missing_person_id
OPTIONS(
  description="Table managing the many-to-many relationship between missing persons and sightings",
  labels=[("environment", "hackathon"), ("application", "homeward"), ("data_type", "relationships")]
);

/* Create unique constraint to prevent duplicate links */
-- Note: BigQuery doesn't enforce unique constraints, this is handled at application level
-- UNIQUE(missing_person_id, sighting_id)

/* Sample data validation constraints (enforced at application level)
   - match_confidence: 0.0-1.0
   - similarity_score: 0.0-1.0 (if provided)
   - physical_match_score: 0.0-1.0 (if provided)
   - temporal_match_score: 0.0-1.0 (if provided)
   - geographical_match_score: 0.0-1.0 (if provided)
   - status: 'Potential', 'Under_Review', 'Confirmed', 'Rejected'
   - match_type: 'Manual', 'AI_Analysis', 'Tip', 'Investigation'
   - priority: 'High', 'Medium', 'Low'
   - Only one confirmed=TRUE link per sighting_id (business rule)
   - missing_person_id must exist in missing_persons table
   - sighting_id must exist in sightings table */

/* Business Rules:
   1. A sighting can be linked to multiple missing person cases (many potential matches)
   2. Only ONE link per sighting can have confirmed=TRUE (one confirmed match)
   3. When a link is confirmed, all other links for that sighting should be rejected
   4. High confidence matches (>0.8) should have priority=High
   5. AI-generated matches should require_review=TRUE initially */