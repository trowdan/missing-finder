from typing import Optional

from google.cloud import bigquery

from homeward.config import AppConfig
from homeward.models.case import KPIData, MissingPersonCase, Sighting
from homeward.services.data_service import DataService


class BigQueryDataService(DataService):
    """BigQuery implementation of DataService for production use"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.client = bigquery.Client(project=config.bigquery_project_id)

    def get_cases(self, status_filter: Optional[str] = None) -> list[MissingPersonCase]:
        """Get missing person cases from BigQuery"""
        # TODO: Implement BigQuery query
        raise NotImplementedError("BigQuery implementation not yet available")

    def get_kpi_data(self) -> KPIData:
        """Get KPI dashboard data from BigQuery"""
        # TODO: Implement BigQuery aggregation queries
        raise NotImplementedError("BigQuery implementation not yet available")

    def get_case_by_id(self, case_id: str) -> Optional[MissingPersonCase]:
        """Get a specific case by ID from BigQuery"""
        # TODO: Implement BigQuery query by ID
        raise NotImplementedError("BigQuery implementation not yet available")

    def create_case(self, case: MissingPersonCase) -> str:
        """Create a new case in BigQuery"""
        MISSING_PERSON_INSERT_QUERY = """
        MERGE `homeward.missing_persons` AS target
        USING (
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
            CASE
              WHEN @last_seen_latitude IS NOT NULL AND @last_seen_longitude IS NOT NULL
              THEN ST_GEOGPOINT(@last_seen_longitude, @last_seen_latitude)
              ELSE NULL
            END AS last_seen_geo,
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
            AI.GENERATE(
              CONCAT(
                'Generate a comprehensive summary paragraph for this missing person case for law enforcement analysis and matching purposes. ',
                'Write it as a single, flowing, discursive paragraph without bullet points, lists, or structured formatting. ',
                'Include key identifying features, circumstances, and critical search information in narrative form. ',
                'Return only the summary paragraph without any introduction, conclusion, or additional commentary from the model. ',
                'Person: ', @name, ' ', @surname, ', ',
                'Age: ', CAST(DATE_DIFF(CURRENT_DATE(), @date_of_birth, YEAR) AS STRING), ' years old, ',
                'Date of birth: ', CAST(@date_of_birth AS STRING), ', ',
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
                END
              ),
              connection_id => 'bq-ai-hackaton.us-central1.homeward_gcp_connection',
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
        """

        # Use the date_of_birth directly from the case (it's mandatory)
        date_of_birth = case.date_of_birth.date() if case.date_of_birth else None

        # Set up the query parameters
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("id", "STRING", case.id),
                bigquery.ScalarQueryParameter("case_number", "STRING", case.case_number),
                bigquery.ScalarQueryParameter("name", "STRING", case.name),
                bigquery.ScalarQueryParameter("surname", "STRING", case.surname),
                bigquery.ScalarQueryParameter("date_of_birth", "DATE", date_of_birth),
                bigquery.ScalarQueryParameter("gender", "STRING", case.gender),
                bigquery.ScalarQueryParameter("height", "FLOAT64", case.height),
                bigquery.ScalarQueryParameter("weight", "FLOAT64", case.weight),
                bigquery.ScalarQueryParameter("hair_color", "STRING", case.hair_color),
                bigquery.ScalarQueryParameter("eye_color", "STRING", case.eye_color),
                bigquery.ScalarQueryParameter("distinguishing_marks", "STRING", case.distinguishing_marks),
                bigquery.ScalarQueryParameter("clothing_description", "STRING", case.clothing_description),
                bigquery.ScalarQueryParameter("last_seen_date", "DATE", case.last_seen_date.date()),
                bigquery.ScalarQueryParameter("last_seen_time", "TIME", case.last_seen_date.time()),
                bigquery.ScalarQueryParameter("last_seen_address", "STRING", case.last_seen_location.address),
                bigquery.ScalarQueryParameter("last_seen_city", "STRING", case.last_seen_location.city),
                bigquery.ScalarQueryParameter("last_seen_country", "STRING", case.last_seen_location.country),
                bigquery.ScalarQueryParameter("last_seen_postal_code", "STRING", case.last_seen_location.postal_code),
                bigquery.ScalarQueryParameter("last_seen_latitude", "FLOAT64", case.last_seen_location.latitude if case.last_seen_location.latitude != 0.0 else None),
                bigquery.ScalarQueryParameter("last_seen_longitude", "FLOAT64", case.last_seen_location.longitude if case.last_seen_location.longitude != 0.0 else None),
                bigquery.ScalarQueryParameter("circumstances", "STRING", case.circumstances),
                bigquery.ScalarQueryParameter("priority", "STRING", case.priority.value),
                bigquery.ScalarQueryParameter("status", "STRING", case.status.value),
                bigquery.ScalarQueryParameter("description", "STRING", case.description),
                bigquery.ScalarQueryParameter("medical_conditions", "STRING", case.medical_conditions),
                bigquery.ScalarQueryParameter("additional_info", "STRING", case.additional_info),
                bigquery.ScalarQueryParameter("photo_url", "STRING", case.photo_url),
                bigquery.ScalarQueryParameter("reporter_name", "STRING", case.reporter_name),
                bigquery.ScalarQueryParameter("reporter_phone", "STRING", case.reporter_phone),
                bigquery.ScalarQueryParameter("reporter_email", "STRING", case.reporter_email),
                bigquery.ScalarQueryParameter("relationship", "STRING", case.relationship),
            ]
        )

        # Execute the parameterized query
        query_job = self.client.query(MISSING_PERSON_INSERT_QUERY, job_config=job_config)
        query_job.result()  # Wait for the query to complete

        return case.id

    def get_sightings(self, status_filter: Optional[str] = None) -> list[Sighting]:
        """Get sighting reports from BigQuery"""
        # TODO: Implement BigQuery query
        raise NotImplementedError("BigQuery implementation not yet available")

    def get_sighting_by_id(self, sighting_id: str) -> Sighting:
        """Get a specific sighting by ID from BigQuery"""
        # TODO: Implement BigQuery query by ID
        raise NotImplementedError("BigQuery implementation not yet available")

    def create_sighting(self, sighting: Sighting) -> str:
        """Create a new sighting in BigQuery with AI-generated summary"""
        SIGHTING_INSERT_QUERY = """
        MERGE `homeward.sightings` AS target
        USING (
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
            CASE
              WHEN @sighted_latitude IS NOT NULL AND @sighted_longitude IS NOT NULL
              THEN ST_GEOGPOINT(@sighted_longitude, @sighted_latitude)
              ELSE NULL
            END AS sighted_geo,
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
            AI.GENERATE(
              CONCAT(
                'Generate a comprehensive summary paragraph for this sighting report for law enforcement analysis and matching purposes. ',
                'Write it as a single, flowing, discursive paragraph without bullet points, lists, or structured formatting. ',
                'Include key identifying features, location details, and critical information for matching with missing persons in narrative form. ',
                'Return only the summary paragraph without any introduction, conclusion, or additional commentary from the model. ',
                'Sighting: ', @description, '. ',
                'Date and time: ', CAST(@sighted_date AS STRING),
                CASE
                  WHEN @sighted_time IS NOT NULL THEN CONCAT(' at ', CAST(@sighted_time AS STRING))
                  ELSE ''
                END,
                '. Location: ', @sighted_address, ', ', @sighted_city, ', ', @sighted_country,
                CASE
                  WHEN @sighted_postal_code IS NOT NULL THEN CONCAT(', ', @sighted_postal_code)
                  ELSE ''
                END,
                '. ',
                CASE
                  WHEN @apparent_gender IS NOT NULL THEN CONCAT('Gender: ', @apparent_gender, '. ')
                  ELSE ''
                END,
                CASE
                  WHEN @apparent_age_range IS NOT NULL THEN CONCAT('Age range: ', @apparent_age_range, '. ')
                  ELSE ''
                END,
                CASE
                  WHEN @height_estimate IS NOT NULL THEN CONCAT('Height: approximately ', CAST(@height_estimate AS STRING), 'cm. ')
                  ELSE ''
                END,
                CASE
                  WHEN @weight_estimate IS NOT NULL THEN CONCAT('Weight: approximately ', CAST(@weight_estimate AS STRING), 'kg. ')
                  ELSE ''
                END,
                CASE
                  WHEN @hair_color IS NOT NULL THEN CONCAT('Hair: ', @hair_color, '. ')
                  ELSE ''
                END,
                CASE
                  WHEN @eye_color IS NOT NULL THEN CONCAT('Eyes: ', @eye_color, '. ')
                  ELSE ''
                END,
                CASE
                  WHEN @clothing_description IS NOT NULL THEN CONCAT('Clothing: ', @clothing_description, '. ')
                  ELSE ''
                END,
                CASE
                  WHEN @distinguishing_features IS NOT NULL THEN CONCAT('Distinguishing features: ', @distinguishing_features, '. ')
                  ELSE ''
                END,
                CASE
                  WHEN @circumstances IS NOT NULL THEN CONCAT('Circumstances: ', @circumstances, '. ')
                  ELSE ''
                END,
                'Confidence level: ', @confidence_level, '. Source: ', @source_type,
                CASE
                  WHEN @witness_name IS NOT NULL THEN CONCAT(' (witness: ', @witness_name, ')')
                  ELSE ''
                END,
                '.'
              ),
              connection_id => 'bq-ai-hackaton.us-central1.homeward_gcp_connection',
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
            video_analytics_result_id, status, priority, verified, created_date, updated_date,
            created_by, notes, ml_summary
          )
          VALUES (
            source.id, source.sighting_number, source.sighted_date, source.sighted_time, source.sighted_address, source.sighted_city, source.sighted_country,
            source.sighted_postal_code, source.sighted_latitude, source.sighted_longitude, source.sighted_geo,
            source.apparent_gender, source.apparent_age_range, source.height_estimate, source.weight_estimate, source.hair_color, source.eye_color,
            source.clothing_description, source.distinguishing_features, source.description, source.circumstances, source.confidence_level,
            source.photo_url, source.video_url, source.source_type, source.witness_name, source.witness_phone, source.witness_email,
            source.video_analytics_result_id, source.status, source.priority, source.verified, source.created_date, source.updated_date,
            source.created_by, source.notes, source.ml_summary
          );
        """

        # Set up the query parameters
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("id", "STRING", sighting.id),
                bigquery.ScalarQueryParameter("sighting_number", "STRING", sighting.sighting_number),
                bigquery.ScalarQueryParameter("sighted_date", "DATE", sighting.sighted_date.date()),
                bigquery.ScalarQueryParameter("sighted_time", "TIME", sighting.sighted_date.time()),
                bigquery.ScalarQueryParameter("sighted_address", "STRING", sighting.sighted_location.address),
                bigquery.ScalarQueryParameter("sighted_city", "STRING", sighting.sighted_location.city),
                bigquery.ScalarQueryParameter("sighted_country", "STRING", sighting.sighted_location.country),
                bigquery.ScalarQueryParameter("sighted_postal_code", "STRING", sighting.sighted_location.postal_code),
                bigquery.ScalarQueryParameter("sighted_latitude", "FLOAT64", sighting.sighted_location.latitude if sighting.sighted_location.latitude != 0.0 else None),
                bigquery.ScalarQueryParameter("sighted_longitude", "FLOAT64", sighting.sighted_location.longitude if sighting.sighted_location.longitude != 0.0 else None),
                bigquery.ScalarQueryParameter("apparent_gender", "STRING", sighting.apparent_gender),
                bigquery.ScalarQueryParameter("apparent_age_range", "STRING", sighting.apparent_age_range),
                bigquery.ScalarQueryParameter("height_estimate", "FLOAT64", sighting.height_estimate),
                bigquery.ScalarQueryParameter("weight_estimate", "FLOAT64", sighting.weight_estimate),
                bigquery.ScalarQueryParameter("hair_color", "STRING", sighting.hair_color),
                bigquery.ScalarQueryParameter("eye_color", "STRING", sighting.eye_color),
                bigquery.ScalarQueryParameter("clothing_description", "STRING", sighting.clothing_description),
                bigquery.ScalarQueryParameter("distinguishing_features", "STRING", sighting.distinguishing_features),
                bigquery.ScalarQueryParameter("description", "STRING", sighting.description),
                bigquery.ScalarQueryParameter("circumstances", "STRING", sighting.circumstances),
                bigquery.ScalarQueryParameter("confidence_level", "STRING", sighting.confidence_level.value),
                bigquery.ScalarQueryParameter("photo_url", "STRING", sighting.photo_url),
                bigquery.ScalarQueryParameter("video_url", "STRING", sighting.video_url),
                bigquery.ScalarQueryParameter("source_type", "STRING", sighting.source_type.value),
                bigquery.ScalarQueryParameter("witness_name", "STRING", sighting.witness_name),
                bigquery.ScalarQueryParameter("witness_phone", "STRING", sighting.witness_phone),
                bigquery.ScalarQueryParameter("witness_email", "STRING", sighting.witness_email),
                bigquery.ScalarQueryParameter("video_analytics_result_id", "STRING", sighting.video_analytics_result_id),
                bigquery.ScalarQueryParameter("status", "STRING", sighting.status.value),
                bigquery.ScalarQueryParameter("priority", "STRING", sighting.priority.value),
                bigquery.ScalarQueryParameter("verified", "STRING", "TRUE" if sighting.verified else "FALSE"),
                bigquery.ScalarQueryParameter("created_by", "STRING", sighting.created_by),
                bigquery.ScalarQueryParameter("notes", "STRING", sighting.notes),
            ]
        )

        # Execute the parameterized query
        query_job = self.client.query(SIGHTING_INSERT_QUERY, job_config=job_config)
        query_job.result()  # Wait for the query to complete

        return sighting.id
