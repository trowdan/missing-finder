/* Insert Missing Person with ML Summary Generation
   Production-ready approach using MERGE statement to handle insert + ML generation atomically
   This avoids separate insert/update operations */

MERGE `<DATASET>.missing_persons` AS target
USING (
  -- Prepare the data with ML summary generated inline
  SELECT 
    @id AS id,
    @case_number AS case_number,
    @name AS name,
    @surname AS surname,
    @date_of_birth AS date_of_birth,
    @gender AS gender,
    @height AS height,
    @weight AS weight,
    @hair_color AS hair_color,
    @eye_color AS eye_color,
    @distinguishing_marks AS distinguishing_marks,
    @clothing_description AS clothing_description,
    @last_seen_date AS last_seen_date,
    @last_seen_time AS last_seen_time,
    @last_seen_address AS last_seen_address,
    @last_seen_city AS last_seen_city,
    @last_seen_country AS last_seen_country,
    @last_seen_postal_code AS last_seen_postal_code,
    @last_seen_latitude AS last_seen_latitude,
    @last_seen_longitude AS last_seen_longitude,
    @last_seen_geo AS last_seen_geo,
    @circumstances AS circumstances,
    @priority AS priority,
    @status AS status,
    @description AS description,
    @medical_conditions AS medical_conditions,
    @additional_info AS additional_info,
    @photo_url AS photo_url,
    @reporter_name AS reporter_name,
    @reporter_phone AS reporter_phone,
    @reporter_email AS reporter_email,
    @relationship AS relationship,
    CURRENT_TIMESTAMP() AS created_date,
    CURRENT_TIMESTAMP() AS updated_date,
    -- Generate ML summary inline during insert using AI.GENERATE with gemini-2.5-pro
    AI.GENERATE(
      CONCAT(
        'Generate a comprehensive summary paragraph for this missing person case for law enforcement analysis and matching purposes. ',
        'Write it as a single, flowing, discursive paragraph without bullet points, lists, or structured formatting. ',
        'Include key identifying features, circumstances, and critical search information in narrative form. ',
        'Return only the summary paragraph without any introduction, conclusion, or additional commentary from the model. ',
        'Person: ', @name, ' ', @surname, ', ',
        'Age: ', CAST(DATE_DIFF(CURRENT_DATE(), @date_of_birth, YEAR) AS STRING), ' years old, ',
        'Gender: ', @gender, ', ',
        CASE 
          WHEN @height IS NOT NULL THEN CONCAT('Height: ', CAST(@height AS STRING), 'cm, ')
          ELSE ''
        END,
        CASE 
          WHEN @weight IS NOT NULL THEN CONCAT('Weight: ', CAST(@weight AS STRING), 'kg, ')
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
          WHEN @distinguishing_marks IS NOT NULL THEN CONCAT('Distinguishing marks: ', @distinguishing_marks, '. ')
          ELSE ''
        END,
        CASE 
          WHEN @clothing_description IS NOT NULL THEN CONCAT('Last seen wearing: ', @clothing_description, '. ')
          ELSE ''
        END,
        'Last seen on ', CAST(@last_seen_date AS STRING), 
        CASE 
          WHEN @last_seen_time IS NOT NULL THEN CONCAT(' at ', CAST(@last_seen_time AS STRING))
          ELSE ''
        END,
        ' in ', @last_seen_city, ', ', @last_seen_country, '. ',
        'Location: ', @last_seen_address, 
        CASE 
          WHEN @last_seen_postal_code IS NOT NULL THEN CONCAT(', ', @last_seen_postal_code)
          ELSE ''
        END,
        '. Circumstances: ', @circumstances, '. ',
        CASE 
          WHEN @medical_conditions IS NOT NULL THEN CONCAT('Medical conditions: ', @medical_conditions, '. ')
          ELSE ''
        END,
        CASE 
          WHEN @additional_info IS NOT NULL THEN CONCAT('Additional information: ', @additional_info, '. ')
          ELSE ''
        END,
        'Case priority: ', @priority, ', Status: ', @status, '. ',
        'Reported by: ', @reporter_name, ' (', @relationship, ').'
      ),
      connection_id => '<PROJECT_ID>.<REGION>.<CONNECTION_NAME>',
      endpoint => 'gemini-2.5-flash',
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

/* Usage Example:
DECLARE id STRING DEFAULT GENERATE_UUID();
DECLARE case_number STRING DEFAULT 'MP-2024-001';
-- ... declare other variables ...

EXECUTE IMMEDIATE '''
  [Above MERGE statement]
''' USING 
  id AS id,
  case_number AS case_number,
  -- ... pass other parameters ...
*/