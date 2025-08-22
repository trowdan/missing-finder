-- Complete working example of insert_with_ml_summary.sql
-- This script demonstrates inserting a missing person with AI-generated summary
-- Copy and paste this entire script into BigQuery Studio to test

BEGIN
  -- Declare all variables with sample data (with correct data types)
  DECLARE id STRING DEFAULT GENERATE_UUID();
  DECLARE case_number STRING DEFAULT 'CASE-2024-031';
  DECLARE name STRING DEFAULT 'Emma';
  DECLARE surname STRING DEFAULT 'Johnson';
  DECLARE date_of_birth DATE DEFAULT '1995-03-15';
  DECLARE gender STRING DEFAULT 'Female';
  DECLARE height FLOAT64 DEFAULT 165.0;
  DECLARE weight FLOAT64 DEFAULT 58.0;
  DECLARE hair_color STRING DEFAULT 'Brown';
  DECLARE eye_color STRING DEFAULT 'Blue';
  DECLARE distinguishing_marks STRING DEFAULT 'Small scar on left cheek';
  DECLARE clothing_description STRING DEFAULT 'Blue jeans, white t-shirt, red backpack';
  DECLARE last_seen_date DATE DEFAULT '2024-08-15';
  DECLARE last_seen_time TIME DEFAULT TIME '14:30:00';
  DECLARE last_seen_address STRING DEFAULT '123 Main Street';
  DECLARE last_seen_city STRING DEFAULT 'San Francisco';
  DECLARE last_seen_country STRING DEFAULT 'USA';
  DECLARE last_seen_postal_code STRING DEFAULT '94102';
  DECLARE last_seen_latitude FLOAT64 DEFAULT 37.7749;
  DECLARE last_seen_longitude FLOAT64 DEFAULT -122.4194;
  DECLARE last_seen_geo GEOGRAPHY DEFAULT ST_GEOGPOINT(-122.4194, 37.7749);
  DECLARE circumstances STRING DEFAULT 'Left home for work but never arrived at office';
  DECLARE priority STRING DEFAULT 'High';
  DECLARE status STRING DEFAULT 'Active';
  DECLARE description STRING DEFAULT 'Missing software engineer';
  DECLARE medical_conditions STRING DEFAULT NULL;
  DECLARE additional_info STRING DEFAULT 'Very punctual person, never misses work without notice';
  DECLARE photo_url STRING DEFAULT 'https://example.com/photos/emma_johnson.jpg';
  DECLARE reporter_name STRING DEFAULT 'Michael Johnson';
  DECLARE reporter_phone STRING DEFAULT '4155551234';
  DECLARE reporter_email STRING DEFAULT 'michael.j@email.com';
  DECLARE relationship STRING DEFAULT 'Brother';

  -- Execute the MERGE statement with ML summary generation
  MERGE `homeward.missing_persons` AS target
  USING (
    -- Prepare the data with ML summary generated inline
    SELECT 
      id,
      case_number,
      name,
      surname,
      date_of_birth,
      gender,
      height,
      weight,
      hair_color,
      eye_color,
      distinguishing_marks,
      clothing_description,
      last_seen_date,
      last_seen_time,
      last_seen_address,
      last_seen_city,
      last_seen_country,
      last_seen_postal_code,
      last_seen_latitude,
      last_seen_longitude,
      last_seen_geo,
      circumstances,
      priority,
      status,
      description,
      medical_conditions,
      additional_info,
      photo_url,
      reporter_name,
      reporter_phone,
      reporter_email,
      relationship,
      CURRENT_TIMESTAMP() AS created_date,
      CURRENT_TIMESTAMP() AS updated_date,
      -- Generate ML summary inline during insert using AI.GENERATE with gemini-2.5-pro
      AI.GENERATE(
        CONCAT(
          'Generate a comprehensive summary paragraph for this missing person case for law enforcement analysis and matching purposes. ',
          'Write it as a single, flowing, discursive paragraph without bullet points, lists, or structured formatting. ',
          'Include key identifying features, circumstances, and critical search information in narrative form. ',
          'Return only the summary paragraph without any introduction, conclusion, or additional commentary from the model. ',
          'Person: ', name, ' ', surname, ', ',
          'Age: ', CAST(DATE_DIFF(CURRENT_DATE(), date_of_birth, YEAR) AS STRING), ' years old, ',
          'Gender: ', gender, ', ',
          CASE 
            WHEN height IS NOT NULL THEN CONCAT('Height: ', CAST(height AS STRING), 'cm, ')
            ELSE ''
          END,
          CASE 
            WHEN weight IS NOT NULL THEN CONCAT('Weight: ', CAST(weight AS STRING), 'kg, ')
            ELSE ''
          END,
          CASE 
            WHEN hair_color IS NOT NULL THEN CONCAT('Hair: ', hair_color, ', ')
            ELSE ''
          END,
          CASE 
            WHEN eye_color IS NOT NULL THEN CONCAT('Eyes: ', eye_color, ', ')
            ELSE ''
          END,
          CASE 
            WHEN distinguishing_marks IS NOT NULL THEN CONCAT('Distinguishing marks: ', distinguishing_marks, '. ')
            ELSE ''
          END,
          CASE 
            WHEN clothing_description IS NOT NULL THEN CONCAT('Last seen wearing: ', clothing_description, '. ')
            ELSE ''
          END,
          'Last seen on ', CAST(last_seen_date AS STRING), 
          CASE 
            WHEN last_seen_time IS NOT NULL THEN CONCAT(' at ', CAST(last_seen_time AS STRING))
            ELSE ''
          END,
          ' in ', last_seen_city, ', ', last_seen_country, '. ',
          'Location: ', last_seen_address, 
          CASE 
            WHEN last_seen_postal_code IS NOT NULL THEN CONCAT(', ', last_seen_postal_code)
            ELSE ''
          END,
          '. Circumstances: ', circumstances, '. ',
          CASE 
            WHEN medical_conditions IS NOT NULL THEN CONCAT('Medical conditions: ', medical_conditions, '. ')
            ELSE ''
          END,
          CASE 
            WHEN additional_info IS NOT NULL THEN CONCAT('Additional information: ', additional_info, '. ')
            ELSE ''
          END,
          'Case priority: ', priority, ', Status: ', status, '. ',
          'Reported by: ', reporter_name, ' (', relationship, ').'
        ),
        connection_id => 'bq-ai-hackaton.us-central1.homeward_gcp_connection',
        endpoint => 'gemini-2.5-pro',
        model_params => JSON '{"generation_config": {"temperature": 0}}'
      ).result AS ml_summary
  ) AS source
  ON target.id = source.id
  WHEN NOT MATCHED THEN
    INSERT (
      id, case_number, name, surname, date_of_birth, gender,
      height, weight, hair_color, eye_color, distinguishing_marks, clothing_description,
      last_seen_date, last_seen_time, last_seen_address, last_seen_city, last_seen_country,
      last_seen_postal_code, last_seen_latitude, last_seen_longitude, last_seen_geo,
      circumstances, priority, status, description, medical_conditions, additional_info,
      photo_url, reporter_name, reporter_phone, reporter_email, relationship,
      created_date, updated_date, ml_summary
    )
    VALUES (
      source.id, source.case_number, source.name, source.surname, source.date_of_birth, source.gender,
      source.height, source.weight, source.hair_color, source.eye_color, source.distinguishing_marks, source.clothing_description,
      source.last_seen_date, source.last_seen_time, source.last_seen_address, source.last_seen_city, source.last_seen_country,
      source.last_seen_postal_code, source.last_seen_latitude, source.last_seen_longitude, source.last_seen_geo,
      source.circumstances, source.priority, source.status, source.description, source.medical_conditions, source.additional_info,
      source.photo_url, source.reporter_name, source.reporter_phone, source.reporter_email, source.relationship,
      source.created_date, source.updated_date, source.ml_summary
    );
END;