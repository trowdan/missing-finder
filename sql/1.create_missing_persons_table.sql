/* Missing Persons Table Creation Script for BigQuery
   Based on the MissingPersonCase dataclass and missing person form structure
   This table stores comprehensive information about missing person cases */

CREATE TABLE IF NOT EXISTS `homeward.missing_persons` (
  /* Primary identifiers */
  id STRING NOT NULL OPTIONS(description="Unique case identifier"),
  case_number STRING OPTIONS(description="Official case reference number if available"),
  
  /* Personal Information */
  name STRING NOT NULL OPTIONS(description="First name of the missing person"),
  surname STRING NOT NULL OPTIONS(description="Last name of the missing person"),
  date_of_birth DATE NOT NULL OPTIONS(description="Date of birth of the missing person"),
  gender STRING NOT NULL OPTIONS(description="Gender (Male/Female/Other/Prefer not to say)"),
  
  /* Physical Description */
  height FLOAT64 OPTIONS(description="Height in centimeters"),
  weight FLOAT64 OPTIONS(description="Weight in kilograms"),
  hair_color STRING OPTIONS(description="Hair color"),
  eye_color STRING OPTIONS(description="Eye color"),
  distinguishing_marks STRING OPTIONS(description="Scars, tattoos, birthmarks, unique features"),
  clothing_description STRING OPTIONS(description="Description of clothing and accessories when last seen"),
  
  /* Last Seen Information */
  last_seen_date DATE NOT NULL OPTIONS(description="Date when person was last seen"),
  last_seen_time TIME OPTIONS(description="Time when person was last seen"),
  last_seen_address STRING NOT NULL OPTIONS(description="Street address where person was last seen"),
  last_seen_city STRING NOT NULL OPTIONS(description="City where person was last seen"),
  last_seen_country STRING NOT NULL OPTIONS(description="Country where person was last seen"),
  last_seen_postal_code STRING OPTIONS(description="Postal code where person was last seen"),
  last_seen_latitude FLOAT64 OPTIONS(description="Latitude coordinates of last seen location"),
  last_seen_longitude FLOAT64 OPTIONS(description="Longitude coordinates of last seen location"),
  last_seen_geo GEOGRAPHY OPTIONS(description="SFS position of last seen location"),

  /* Case Details */
  circumstances STRING NOT NULL OPTIONS(description="Detailed description of circumstances of disappearance"),
  priority STRING NOT NULL OPTIONS(description="Priority level (High/Medium/Low)"),
  status STRING NOT NULL OPTIONS(description="Case status (Active/Resolved/Suspended)"),
  description STRING OPTIONS(description="General case description"),
  
  /* Additional Information */
  medical_conditions STRING OPTIONS(description="Medical conditions or mental health information"),
  additional_info STRING OPTIONS(description="Any other relevant information"),
  
  /* Media */
  photo_url STRING OPTIONS(description="URL to photo of missing person"),
  
  /* Contact Information (Reporter) */
  reporter_name STRING NOT NULL OPTIONS(description="Name of person reporting the missing person"),
  reporter_phone STRING NOT NULL OPTIONS(description="Phone number of reporter"),
  reporter_email STRING OPTIONS(description="Email address of reporter"),
  relationship STRING NOT NULL OPTIONS(description="Relationship of reporter to missing person"),
  
  /* Metadata */
  created_date TIMESTAMP NOT NULL OPTIONS(description="Date and time when case was created"),
  updated_date TIMESTAMP NOT NULL OPTIONS(description="Date and time when case was last updated")

  --TODO Add Missing Summary
  --TODO Add Missing Photo + Summary Embedding
)
PARTITION BY DATE(created_date)
CLUSTER BY status, priority, last_seen_city
OPTIONS(
  description="Table storing comprehensive missing person case information for the Homeward application",
  labels=[("environment", "hackathon"), ("application", "homeward"), ("data_type", "missing_persons")]
);

/* Sample data validation constraints (enforced at application level)
   - gender: 'Male', 'Female', 'Other', 'Prefer not to say'
   - priority: 'High', 'Medium', 'Low' 
   - status: 'Active', 'Resolved', 'Suspended'
   - name, surname, reporter_name: only letters, spaces, hyphens, apostrophes
   - phone: 10-15 digits
   - email: valid email format (if provided)
   - last_seen_date: not in the future, not more than 100 years ago
   - height: 10-300 cm (if provided)
   - weight: 1-1000 kg (if provided)
   - postal_code: valid format for country (if provided) */