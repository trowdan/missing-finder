from datetime import datetime
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
        """Create a new sighting in BigQuery"""
        # TODO: Implement BigQuery insert
        raise NotImplementedError("BigQuery implementation not yet available")
