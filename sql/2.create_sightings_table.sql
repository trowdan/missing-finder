/* Sightings Table Creation Script for BigQuery
   This table stores sighting reports that can be linked to missing person cases
   A sighting represents an observation of a person that might match a missing person */

CREATE TABLE IF NOT EXISTS `homeward.sightings` (
  /* Primary identifiers */
  id STRING NOT NULL OPTIONS(description="Unique sighting identifier"),
  sighting_number STRING OPTIONS(description="Official sighting reference number if available"),
  
  /* Sighting Information */
  sighted_date DATE NOT NULL OPTIONS(description="Date when person was sighted"),
  sighted_time TIME OPTIONS(description="Time when person was sighted"),
  sighted_address STRING NOT NULL OPTIONS(description="Street address where person was sighted"),
  sighted_city STRING NOT NULL OPTIONS(description="City where person was sighted"),
  sighted_country STRING NOT NULL OPTIONS(description="Country where person was sighted"),
  sighted_postal_code STRING OPTIONS(description="Postal code where person was sighted"),
  sighted_latitude FLOAT64 OPTIONS(description="Latitude coordinates of sighting location"),
  sighted_longitude FLOAT64 OPTIONS(description="Longitude coordinates of sighting location"),
  sighted_geo GEOGRAPHY OPTIONS(description="SFS position of sighting location"),
  
  /* Person Description */
  apparent_gender STRING OPTIONS(description="Apparent gender of sighted person"),
  apparent_age_range STRING OPTIONS(description="Estimated age range (e.g., '20-30', '40-50')"),
  height_estimate FLOAT64 OPTIONS(description="Estimated height in centimeters"),
  weight_estimate FLOAT64 OPTIONS(description="Estimated weight in kilograms"),
  hair_color STRING OPTIONS(description="Observed hair color"),
  eye_color STRING OPTIONS(description="Observed eye color"),
  clothing_description STRING OPTIONS(description="Description of clothing and accessories observed"),
  distinguishing_features STRING OPTIONS(description="Notable features, marks, or characteristics observed"),
  
  /* Sighting Details */
  description STRING NOT NULL OPTIONS(description="Detailed description of the sighting"),
  circumstances STRING OPTIONS(description="Circumstances under which person was sighted"),
  confidence_level STRING NOT NULL OPTIONS(description="Reporter's confidence level (High/Medium/Low)"),
  photo_url STRING OPTIONS(description="URL to photo of sighted person if available"),
  video_url STRING OPTIONS(description="URL to video footage if available"),
  
  /* Source Information */
  source_type STRING NOT NULL OPTIONS(description="Source of sighting (Witness/Manual_Entry/Other)"),
  witness_name STRING OPTIONS(description="Name of witness (if applicable)"),
  witness_phone STRING OPTIONS(description="Phone number of witness (if applicable)"),
  witness_email STRING OPTIONS(description="Email address of witness (if applicable)"),
  video_analytics_result_id STRING OPTIONS(description="Reference to video_analytics_results.id if converted from AI detection"),
  
  /* Status and Processing */
  status STRING NOT NULL OPTIONS(description="Sighting status (New/Under_Review/Verified/False_Positive/Archived)"),
  priority STRING NOT NULL OPTIONS(description="Priority level (High/Medium/Low)"),
  verified BOOLEAN NOT NULL DEFAULT FALSE OPTIONS(description="Whether sighting has been verified"),
  
  /* Metadata */
  created_date TIMESTAMP NOT NULL OPTIONS(description="Date and time when sighting was created"),
  updated_date TIMESTAMP NOT NULL OPTIONS(description="Date and time when sighting was last updated"),
  created_by STRING OPTIONS(description="User or system that created the sighting"),
  notes STRING OPTIONS(description="Additional notes or comments about the sighting")
)
PARTITION BY DATE(created_date)
CLUSTER BY status, priority, sighted_city, source_type
OPTIONS(
  description="Table storing sighting reports that can be linked to missing person cases",
  labels=[("environment", "hackathon"), ("application", "homeward"), ("data_type", "sightings")]
);

/* Sample data validation constraints (enforced at application level)
   - confidence_level: 'High', 'Medium', 'Low'
   - priority: 'High', 'Medium', 'Low'
   - status: 'New', 'Under_Review', 'Verified', 'False_Positive', 'Archived'
   - source_type: 'Witness', 'Manual_Entry', 'Other'
   - apparent_gender: 'Male', 'Female', 'Other', 'Unknown'
   - sighted_date: not in the future
   - height_estimate: 10-300 cm (if provided)
   - weight_estimate: 1-1000 kg (if provided)
   - phone: 10-15 digits (if provided)
   - email: valid email format (if provided) */