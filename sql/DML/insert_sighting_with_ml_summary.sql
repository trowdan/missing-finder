/* Insert Sighting with ML Summary Generation
   Production-ready approach using MERGE statement to handle insert + ML generation atomically
   This avoids separate insert/update operations */

MERGE `<DATASET>.sightings` AS target
USING (
  -- Prepare the data with ML summary generated inline
  SELECT 
    @id AS id,
    @sighting_number AS sighting_number,
    @sighted_date AS sighted_date,
    @sighted_time AS sighted_time,
    @sighted_address AS sighted_address,
    @sighted_city AS sighted_city,
    @sighted_country AS sighted_country,
    @sighted_postal_code AS sighted_postal_code,
    @sighted_latitude AS sighted_latitude,
    @sighted_longitude AS sighted_longitude,
    @sighted_geo AS sighted_geo,
    @apparent_gender AS apparent_gender,
    @apparent_age_range AS apparent_age_range,
    @height_estimate AS height_estimate,
    @weight_estimate AS weight_estimate,
    @hair_color AS hair_color,
    @eye_color AS eye_color,
    @clothing_description AS clothing_description,
    @distinguishing_features AS distinguishing_features,
    @description AS description,
    @circumstances AS circumstances,
    @confidence_level AS confidence_level,
    @photo_url AS photo_url,
    @video_url AS video_url,
    @source_type AS source_type,
    @witness_name AS witness_name,
    @witness_phone AS witness_phone,
    @witness_email AS witness_email,
    @video_analytics_result_id AS video_analytics_result_id,
    @status AS status,
    @priority AS priority,
    @verified AS verified,
    CURRENT_TIMESTAMP() AS created_date,
    CURRENT_TIMESTAMP() AS updated_date,
    @created_by AS created_by,
    @notes AS notes,
    -- Generate ML summary inline during insert using AI.GENERATE with gemini-2.5-pro
    AI.GENERATE(
      CONCAT(
        'Generate a comprehensive summary paragraph for this sighting report for law enforcement analysis and matching purposes. ',
        'Write it as a single, flowing, discursive paragraph without bullet points, lists, or structured formatting. ',
        'Include key identifying features, location details, and critical matching information in narrative form. ',
        'Return only the summary paragraph without any introduction, conclusion, or additional commentary from the model. ',
        'Sighting details: ',
        CASE 
          WHEN @apparent_gender IS NOT NULL THEN CONCAT('Gender: ', @apparent_gender, ', ')
          ELSE ''
        END,
        CASE 
          WHEN @apparent_age_range IS NOT NULL THEN CONCAT('Age range: ', @apparent_age_range, ', ')
          ELSE ''
        END,
        CASE 
          WHEN @height_estimate IS NOT NULL THEN CONCAT('Height: ', CAST(@height_estimate AS STRING), 'cm, ')
          ELSE ''
        END,
        CASE 
          WHEN @weight_estimate IS NOT NULL THEN CONCAT('Weight: ', CAST(@weight_estimate AS STRING), 'kg, ')
          ELSE ''
        END,
        CASE 
          WHEN @hair_color IS NOT NULL THEN CONCAT('Hair: ', @hair_color, ', ')
          ELSE ''
        END,
        CASE 
          WHEN @eye_color IS NOT NULL THEN CONCAT('Eyes: ', @eye_color, ', ')
          ELSE ''
        END,
        CASE 
          WHEN @distinguishing_features IS NOT NULL THEN CONCAT('Distinguishing features: ', @distinguishing_features, '. ')
          ELSE ''
        END,
        CASE 
          WHEN @clothing_description IS NOT NULL THEN CONCAT('Clothing: ', @clothing_description, '. ')
          ELSE ''
        END,
        'Sighted on ', CAST(@sighted_date AS STRING), 
        CASE 
          WHEN @sighted_time IS NOT NULL THEN CONCAT(' at ', CAST(@sighted_time AS STRING))
          ELSE ''
        END,
        ' in ', @sighted_city, ', ', @sighted_country, '. ',
        'Location: ', @sighted_address, 
        CASE 
          WHEN @sighted_postal_code IS NOT NULL THEN CONCAT(', ', @sighted_postal_code)
          ELSE ''
        END,
        '. Description: ', @description, '. ',
        CASE 
          WHEN @circumstances IS NOT NULL THEN CONCAT('Circumstances: ', @circumstances, '. ')
          ELSE ''
        END,
        'Confidence level: ', @confidence_level, ', Priority: ', @priority, ', Status: ', @status, '. ',
        'Source: ', @source_type,
        CASE 
          WHEN @witness_name IS NOT NULL THEN CONCAT(', Witness: ', @witness_name)
          ELSE ''
        END,
        '. ',
        CASE 
          WHEN @notes IS NOT NULL THEN CONCAT('Additional notes: ', @notes, '. ')
          ELSE ''
        END
      ),
      connection_id => '<PROJECT_ID>.<REGION>.<CONNECTION_NAME>',
      endpoint => 'gemini-2.5-flash',
      model_params => JSON '{"generation_config": {"temperature": 0}}'
    ).result AS ml_summary
) AS source
ON target.id = source.id
WHEN NOT MATCHED THEN
  INSERT (
    id, sighting_number, sighted_date, sighted_time, sighted_address, sighted_city, sighted_country,
    sighted_postal_code, sighted_latitude, sighted_longitude, sighted_geo,
    apparent_gender, apparent_age_range, height_estimate, weight_estimate, hair_color, eye_color,
    clothing_description, distinguishing_features, description, circumstances, confidence_level,
    photo_url, video_url, source_type, witness_name, witness_phone, witness_email,
    video_analytics_result_id, status, priority, verified,
    created_date, updated_date, created_by, notes, ml_summary
  )
  VALUES (
    source.id, source.sighting_number, source.sighted_date, source.sighted_time, source.sighted_address, source.sighted_city, source.sighted_country,
    source.sighted_postal_code, source.sighted_latitude, source.sighted_longitude, source.sighted_geo,
    source.apparent_gender, source.apparent_age_range, source.height_estimate, source.weight_estimate, source.hair_color, source.eye_color,
    source.clothing_description, source.distinguishing_features, source.description, source.circumstances, source.confidence_level,
    source.photo_url, source.video_url, source.source_type, source.witness_name, source.witness_phone, source.witness_email,
    source.video_analytics_result_id, source.status, source.priority, source.verified,
    source.created_date, source.updated_date, source.created_by, source.notes, source.ml_summary
  );

/* Usage Example:
DECLARE id STRING DEFAULT GENERATE_UUID();
DECLARE sighting_number STRING DEFAULT 'S-2024-001';
DECLARE sighted_date DATE DEFAULT '2024-01-15';
DECLARE sighted_time TIME DEFAULT '14:30:00';
DECLARE sighted_address STRING DEFAULT '123 Main Street';
DECLARE sighted_city STRING DEFAULT 'New York';
DECLARE sighted_country STRING DEFAULT 'USA';
-- ... declare other variables ...

EXECUTE IMMEDIATE '''
  [Above MERGE statement]
''' USING 
  id AS id,
  sighting_number AS sighting_number,
  sighted_date AS sighted_date,
  -- ... pass other parameters ...
*/