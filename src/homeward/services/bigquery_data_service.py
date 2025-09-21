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

    def get_cases(self, status_filter: Optional[str] = None, page: int = 1, page_size: int = 20) -> tuple[list[MissingPersonCase], int]:
        """Get missing person cases from BigQuery with pagination"""

        # Calculate offset
        offset = (page - 1) * page_size

        # Count query - optimized to count only on id field
        COUNT_QUERY = """
        SELECT COUNT(id) as total_count
        FROM `homeward.missing_persons`
        WHERE (@status_filter IS NULL OR status = @status_filter)
        """

        # Data query with pagination
        CASES_QUERY = """
        SELECT
            id, case_number, name, surname, date_of_birth, gender,
            height, weight, hair_color, eye_color, distinguishing_marks, clothing_description,
            last_seen_date, last_seen_time, last_seen_address, last_seen_city,
            last_seen_country, last_seen_postal_code, last_seen_latitude, last_seen_longitude,
            circumstances, priority, status, description, medical_conditions, additional_info,
            photo_url, reporter_name, reporter_phone, reporter_email, relationship,
            created_date, updated_date, ml_summary
        FROM `homeward.missing_persons`
        WHERE (@status_filter IS NULL OR status = @status_filter)
        ORDER BY created_date DESC
        LIMIT @page_size OFFSET @offset
        """

        # Execute count query
        count_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("status_filter", "STRING", status_filter)
            ]
        )
        count_job = self.client.query(COUNT_QUERY, job_config=count_job_config)
        total_count = list(count_job.result())[0].total_count

        # Execute data query
        data_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("status_filter", "STRING", status_filter),
                bigquery.ScalarQueryParameter("page_size", "INT64", page_size),
                bigquery.ScalarQueryParameter("offset", "INT64", offset)
            ]
        )
        data_job = self.client.query(CASES_QUERY, job_config=data_job_config)

        # Convert results to MissingPersonCase objects (using existing pattern from get_case_by_id)
        cases = []
        for row in data_job.result():
            # Combine date and time for last_seen_date
            last_seen_date = row.last_seen_date
            last_seen_time = row.last_seen_time

            if last_seen_date and last_seen_time:
                from datetime import datetime, time
                if isinstance(last_seen_time, time):
                    last_seen_datetime = datetime.combine(last_seen_date, last_seen_time)
                else:
                    last_seen_datetime = datetime.combine(last_seen_date, datetime.min.time())
            else:
                last_seen_datetime = datetime.combine(last_seen_date, datetime.min.time()) if last_seen_date else datetime.now()

            # Create Location object
            from homeward.models.case import Location, CaseStatus, CasePriority
            location = Location(
                address=row.last_seen_address or "",
                city=row.last_seen_city or "",
                country=row.last_seen_country or "",
                postal_code=row.last_seen_postal_code,
                latitude=row.last_seen_latitude,
                longitude=row.last_seen_longitude
            )

            # Parse enum values
            status = CaseStatus.ACTIVE
            try:
                status = CaseStatus(row.status)
            except ValueError:
                pass

            priority = CasePriority.MEDIUM
            try:
                priority = CasePriority(row.priority)
            except ValueError:
                pass

            # Convert date_of_birth from date to datetime
            from datetime import datetime
            date_of_birth = row.date_of_birth
            if date_of_birth and not isinstance(date_of_birth, datetime):
                date_of_birth = datetime.combine(date_of_birth, datetime.min.time())

            # Create MissingPersonCase object
            case = MissingPersonCase(
                id=row.id,
                name=row.name or "",
                surname=row.surname or "",
                date_of_birth=date_of_birth or datetime.now(),
                gender=row.gender or "",
                last_seen_date=last_seen_datetime,
                last_seen_location=location,
                status=status,
                circumstances=row.circumstances or "",
                reporter_name=row.reporter_name or "",
                reporter_phone=row.reporter_phone or "",
                relationship=row.relationship or "",
                case_number=row.case_number,
                height=row.height,
                weight=row.weight,
                hair_color=row.hair_color,
                eye_color=row.eye_color,
                distinguishing_marks=row.distinguishing_marks,
                clothing_description=row.clothing_description,
                medical_conditions=row.medical_conditions,
                additional_info=row.additional_info,
                description=row.description,
                photo_url=row.photo_url,
                reporter_email=row.reporter_email,
                created_date=row.created_date or datetime.now(),
                priority=priority,
                ml_summary=row.ml_summary,
            )
            cases.append(case)

        return cases, total_count

    def get_kpi_data(self) -> KPIData:
        """Get KPI dashboard data from BigQuery"""

        KPI_QUERY = """
        WITH case_stats AS (
          SELECT
            COUNT(id) as total_cases,
            COUNTIF(status = 'Active') as active_cases,
            COUNTIF(status = 'Resolved') as resolved_cases,
            AVG(CASE
              WHEN status = 'Resolved'
              THEN DATE_DIFF(updated_date, created_date, DAY)
              END) as avg_resolution_days,
            SAFE_DIVIDE(COUNTIF(status = 'Resolved'), COUNT(id)) * 100 as success_rate
          FROM `homeward.missing_persons`
        ),
        sighting_stats AS (
          SELECT COUNT(id) as sightings_today
          FROM `homeward.sightings`
          WHERE DATE(created_date) = CURRENT_DATE()
        )
        SELECT
          c.total_cases,
          c.active_cases,
          c.resolved_cases,
          s.sightings_today,
          c.success_rate,
          c.avg_resolution_days
        FROM case_stats c
        CROSS JOIN sighting_stats s
        """

        query_job = self.client.query(KPI_QUERY)
        row = list(query_job.result())[0]

        return KPIData(
            total_cases=row.total_cases or 0,
            active_cases=row.active_cases or 0,
            resolved_cases=row.resolved_cases or 0,
            sightings_today=row.sightings_today or 0,
            success_rate=row.success_rate or 0.0,
            avg_resolution_days=row.avg_resolution_days or 0.0
        )

    def get_case_by_id(self, case_id: str) -> Optional[MissingPersonCase]:
        """Get a specific case by ID from BigQuery"""
        CASE_SELECT_QUERY = """
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
            created_date,
            updated_date,
            ml_summary
        FROM `homeward.missing_persons`
        WHERE id = @case_id
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("case_id", "STRING", case_id),
            ]
        )

        try:
            query_job = self.client.query(CASE_SELECT_QUERY, job_config=job_config)
            results = list(query_job.result())

            if not results:
                return None

            row = results[0]

            # Combine date and time for last_seen_date
            last_seen_date = row.last_seen_date
            last_seen_time = row.last_seen_time

            if last_seen_date and last_seen_time:
                from datetime import datetime, time
                if isinstance(last_seen_time, time):
                    last_seen_datetime = datetime.combine(last_seen_date, last_seen_time)
                else:
                    last_seen_datetime = datetime.combine(last_seen_date, datetime.min.time())
            else:
                last_seen_datetime = datetime.combine(last_seen_date, datetime.min.time()) if last_seen_date else datetime.now()

            # Create Location object
            from homeward.models.case import Location, CaseStatus, CasePriority
            location = Location(
                address=row.last_seen_address or "",
                city=row.last_seen_city or "",
                country=row.last_seen_country or "",
                postal_code=row.last_seen_postal_code,
                latitude=row.last_seen_latitude,
                longitude=row.last_seen_longitude
            )

            # Parse enum values
            status = CaseStatus.ACTIVE
            try:
                status = CaseStatus(row.status)
            except ValueError:
                pass

            priority = CasePriority.MEDIUM
            try:
                priority = CasePriority(row.priority)
            except ValueError:
                pass

            # Convert date_of_birth from date to datetime
            date_of_birth = row.date_of_birth
            if date_of_birth and not isinstance(date_of_birth, datetime):
                date_of_birth = datetime.combine(date_of_birth, datetime.min.time())

            # Create MissingPersonCase object
            case = MissingPersonCase(
                id=row.id,
                name=row.name or "",
                surname=row.surname or "",
                date_of_birth=date_of_birth or datetime.now(),
                gender=row.gender or "",
                last_seen_date=last_seen_datetime,
                last_seen_location=location,
                status=status,
                circumstances=row.circumstances or "",
                reporter_name=row.reporter_name or "",
                reporter_phone=row.reporter_phone or "",
                relationship=row.relationship or "",
                case_number=row.case_number,
                height=row.height,
                weight=row.weight,
                hair_color=row.hair_color,
                eye_color=row.eye_color,
                distinguishing_marks=row.distinguishing_marks,
                clothing_description=row.clothing_description,
                medical_conditions=row.medical_conditions,
                additional_info=row.additional_info,
                description=row.description,
                photo_url=row.photo_url,
                reporter_email=row.reporter_email,
                created_date=row.created_date or datetime.now(),
                priority=priority,
                ml_summary=row.ml_summary,
            )

            return case

        except Exception as e:
            print(f"Error retrieving case {case_id}: {str(e)}")
            return None

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
                bigquery.ScalarQueryParameter("last_seen_latitude", "FLOAT64", case.last_seen_location.latitude if case.last_seen_location.latitude is not None and case.last_seen_location.latitude != 0.0 else None),
                bigquery.ScalarQueryParameter("last_seen_longitude", "FLOAT64", case.last_seen_location.longitude if case.last_seen_location.longitude is not None and case.last_seen_location.longitude != 0.0 else None),
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

    def update_case(self, case: MissingPersonCase) -> bool:
        """Update an existing case in BigQuery with AI regeneration and embedding clearing"""
        MISSING_PERSON_UPDATE_QUERY = """
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
        WHEN MATCHED THEN
          UPDATE SET
            case_number = source.case_number,
            name = source.name,
            surname = source.surname,
            date_of_birth = source.date_of_birth,
            gender = source.gender,
            height = source.height,
            weight = source.weight,
            hair_color = source.hair_color,
            eye_color = source.eye_color,
            distinguishing_marks = source.distinguishing_marks,
            clothing_description = source.clothing_description,
            last_seen_date = source.last_seen_date,
            last_seen_time = source.last_seen_time,
            last_seen_address = source.last_seen_address,
            last_seen_city = source.last_seen_city,
            last_seen_country = source.last_seen_country,
            last_seen_postal_code = source.last_seen_postal_code,
            last_seen_latitude = source.last_seen_latitude,
            last_seen_longitude = source.last_seen_longitude,
            last_seen_geo = source.last_seen_geo,
            circumstances = source.circumstances,
            priority = source.priority,
            status = source.status,
            description = source.description,
            medical_conditions = source.medical_conditions,
            additional_info = source.additional_info,
            photo_url = source.photo_url,
            reporter_name = source.reporter_name,
            reporter_phone = source.reporter_phone,
            reporter_email = source.reporter_email,
            relationship = source.relationship,
            updated_date = source.updated_date,
            ml_summary = source.ml_summary,
            ml_summary_embedding = NULL;
        """

        try:
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
                    bigquery.ScalarQueryParameter("last_seen_latitude", "FLOAT64", case.last_seen_location.latitude if case.last_seen_location.latitude is not None and case.last_seen_location.latitude != 0.0 else None),
                    bigquery.ScalarQueryParameter("last_seen_longitude", "FLOAT64", case.last_seen_location.longitude if case.last_seen_location.longitude is not None and case.last_seen_location.longitude != 0.0 else None),
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
            query_job = self.client.query(MISSING_PERSON_UPDATE_QUERY, job_config=job_config)
            query_job.result()  # Wait for the query to complete

            return True

        except Exception as e:
            print(f"Error updating case {case.id}: {str(e)}")
            return False

    def get_sightings(self, status_filter: Optional[str] = None, page: int = 1, page_size: int = 20) -> tuple[list[Sighting], int]:
        """Get sighting reports from BigQuery with pagination"""

        # Calculate offset
        offset = (page - 1) * page_size

        # Count query - optimized to count only on id field
        COUNT_QUERY = """
        SELECT COUNT(id) as total_count
        FROM `homeward.sightings`
        WHERE (@status_filter IS NULL OR status = @status_filter)
        """

        # Data query with pagination
        SIGHTINGS_QUERY = """
        SELECT
            id, sighting_number, sighted_date, sighted_time, sighted_address, sighted_city,
            sighted_country, sighted_postal_code, sighted_latitude, sighted_longitude,
            apparent_gender, apparent_age_range, height_estimate, weight_estimate,
            hair_color, eye_color, clothing_description, distinguishing_features,
            description, circumstances, confidence_level, photo_url, video_url,
            source_type, witness_name, witness_phone, witness_email,
            video_analytics_result_id, status, priority, verified,
            created_date, updated_date, created_by, notes, ml_summary
        FROM `homeward.sightings`
        WHERE (@status_filter IS NULL OR status = @status_filter)
        ORDER BY created_date DESC
        LIMIT @page_size OFFSET @offset
        """

        # Execute count query
        count_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("status_filter", "STRING", status_filter)
            ]
        )
        count_job = self.client.query(COUNT_QUERY, job_config=count_job_config)
        total_count = list(count_job.result())[0].total_count

        # Execute data query
        data_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("status_filter", "STRING", status_filter),
                bigquery.ScalarQueryParameter("page_size", "INT64", page_size),
                bigquery.ScalarQueryParameter("offset", "INT64", offset)
            ]
        )
        data_job = self.client.query(SIGHTINGS_QUERY, job_config=data_job_config)

        # Convert results to Sighting objects (using existing pattern from get_sighting_by_id)
        sightings = []
        for row in data_job.result():
            # Combine date and time for sighted_date
            sighted_date = row.sighted_date
            sighted_time = row.sighted_time

            if sighted_date and sighted_time:
                from datetime import datetime, time
                if isinstance(sighted_time, time):
                    sighted_datetime = datetime.combine(sighted_date, sighted_time)
                else:
                    sighted_datetime = datetime.combine(sighted_date, datetime.min.time())
            else:
                sighted_datetime = datetime.combine(sighted_date, datetime.min.time()) if sighted_date else datetime.now()

            # Create Location object
            from homeward.models.case import Location, SightingStatus, SightingPriority, SightingConfidenceLevel, SightingSourceType
            location = Location(
                address=row.sighted_address or "",
                city=row.sighted_city or "",
                country=row.sighted_country or "",
                postal_code=row.sighted_postal_code,
                latitude=row.sighted_latitude,
                longitude=row.sighted_longitude
            )

            # Map enum values
            status_map = {
                "New": SightingStatus.NEW,
                "Under_Review": SightingStatus.UNDER_REVIEW,
                "Verified": SightingStatus.VERIFIED,
                "False_Positive": SightingStatus.FALSE_POSITIVE,
                "Archived": SightingStatus.ARCHIVED,
            }

            priority_map = {
                "High": SightingPriority.HIGH,
                "Medium": SightingPriority.MEDIUM,
                "Low": SightingPriority.LOW,
            }

            confidence_map = {
                "High": SightingConfidenceLevel.HIGH,
                "Medium": SightingConfidenceLevel.MEDIUM,
                "Low": SightingConfidenceLevel.LOW,
            }

            source_type_map = {
                "Witness": SightingSourceType.WITNESS,
                "Manual_Entry": SightingSourceType.MANUAL_ENTRY,
                "Other": SightingSourceType.OTHER,
            }

            # Create Sighting object
            sighting = Sighting(
                id=row.id,
                sighting_number=row.sighting_number,
                sighted_date=sighted_datetime,
                sighted_location=location,
                description=row.description or "",
                confidence_level=confidence_map.get(row.confidence_level, SightingConfidenceLevel.MEDIUM),
                source_type=source_type_map.get(row.source_type, SightingSourceType.OTHER),
                apparent_gender=row.apparent_gender,
                apparent_age_range=row.apparent_age_range,
                height_estimate=row.height_estimate,
                weight_estimate=row.weight_estimate,
                hair_color=row.hair_color,
                eye_color=row.eye_color,
                clothing_description=row.clothing_description,
                distinguishing_features=row.distinguishing_features,
                circumstances=row.circumstances,
                photo_url=row.photo_url,
                video_url=row.video_url,
                witness_name=row.witness_name,
                witness_phone=row.witness_phone,
                witness_email=row.witness_email,
                video_analytics_result_id=row.video_analytics_result_id,
                status=status_map.get(row.status, SightingStatus.NEW),
                priority=priority_map.get(row.priority, SightingPriority.MEDIUM),
                verified=row.verified or False,
                created_date=row.created_date or datetime.now(),
                updated_date=row.updated_date,
                created_by=row.created_by,
                notes=row.notes,
                ml_summary=row.ml_summary
            )
            sightings.append(sighting)

        return sightings, total_count

    def get_sighting_by_id(self, sighting_id: str) -> Optional[Sighting]:
        """Get a specific sighting by ID from BigQuery"""
        SIGHTING_SELECT_QUERY = """
        SELECT
            id,
            sighting_number,
            sighted_date,
            sighted_time,
            sighted_address,
            sighted_city,
            sighted_country,
            sighted_postal_code,
            sighted_latitude,
            sighted_longitude,
            apparent_gender,
            apparent_age_range,
            height_estimate,
            weight_estimate,
            hair_color,
            eye_color,
            clothing_description,
            distinguishing_features,
            description,
            circumstances,
            confidence_level,
            photo_url,
            video_url,
            source_type,
            witness_name,
            witness_phone,
            witness_email,
            video_analytics_result_id,
            status,
            priority,
            verified,
            created_date,
            updated_date,
            created_by,
            notes,
            ml_summary
        FROM `homeward.sightings`
        WHERE id = @sighting_id
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("sighting_id", "STRING", sighting_id),
            ]
        )

        try:
            query_job = self.client.query(SIGHTING_SELECT_QUERY, job_config=job_config)
            results = list(query_job.result())

            if not results:
                return None

            row = results[0]

            # Combine date and time for sighted_date
            sighted_date = row.sighted_date
            sighted_time = row.sighted_time

            if sighted_date and sighted_time:
                from datetime import datetime, time
                if isinstance(sighted_time, time):
                    sighted_datetime = datetime.combine(sighted_date, sighted_time)
                else:
                    sighted_datetime = datetime.combine(sighted_date, datetime.min.time())
            else:
                sighted_datetime = datetime.combine(sighted_date, datetime.min.time()) if sighted_date else datetime.now()

            # Create Location object
            from homeward.models.case import Location, SightingStatus, SightingPriority, SightingConfidenceLevel, SightingSourceType
            location = Location(
                address=row.sighted_address or "",
                city=row.sighted_city or "",
                country=row.sighted_country or "",
                postal_code=row.sighted_postal_code,
                latitude=row.sighted_latitude,
                longitude=row.sighted_longitude
            )

            # Map enum values
            status_map = {
                "New": SightingStatus.NEW,
                "Under_Review": SightingStatus.UNDER_REVIEW,
                "Verified": SightingStatus.VERIFIED,
                "False_Positive": SightingStatus.FALSE_POSITIVE,
                "Archived": SightingStatus.ARCHIVED,
            }

            priority_map = {
                "High": SightingPriority.HIGH,
                "Medium": SightingPriority.MEDIUM,
                "Low": SightingPriority.LOW,
            }

            confidence_map = {
                "High": SightingConfidenceLevel.HIGH,
                "Medium": SightingConfidenceLevel.MEDIUM,
                "Low": SightingConfidenceLevel.LOW,
            }

            source_type_map = {
                "Witness": SightingSourceType.WITNESS,
                "Manual_Entry": SightingSourceType.MANUAL_ENTRY,
                "Other": SightingSourceType.OTHER,
            }

            # Create and return Sighting object
            return Sighting(
                id=row.id,
                sighting_number=row.sighting_number,
                sighted_date=sighted_datetime,
                sighted_location=location,
                description=row.description or "",
                confidence_level=confidence_map.get(row.confidence_level, SightingConfidenceLevel.MEDIUM),
                source_type=source_type_map.get(row.source_type, SightingSourceType.OTHER),
                apparent_gender=row.apparent_gender,
                apparent_age_range=row.apparent_age_range,
                height_estimate=row.height_estimate,
                weight_estimate=row.weight_estimate,
                hair_color=row.hair_color,
                eye_color=row.eye_color,
                clothing_description=row.clothing_description,
                distinguishing_features=row.distinguishing_features,
                circumstances=row.circumstances,
                photo_url=row.photo_url,
                video_url=row.video_url,
                witness_name=row.witness_name,
                witness_phone=row.witness_phone,
                witness_email=row.witness_email,
                video_analytics_result_id=row.video_analytics_result_id,
                status=status_map.get(row.status, SightingStatus.NEW),
                priority=priority_map.get(row.priority, SightingPriority.MEDIUM),
                verified=row.verified or False,
                created_date=row.created_date or datetime.now(),
                updated_date=row.updated_date,
                created_by=row.created_by,
                notes=row.notes,
                ml_summary=row.ml_summary
            )

        except Exception as e:
            print(f"Error retrieving sighting {sighting_id}: {str(e)}")
            return None

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
                bigquery.ScalarQueryParameter("sighted_latitude", "FLOAT64", sighting.sighted_location.latitude if sighting.sighted_location.latitude is not None and sighting.sighted_location.latitude != 0.0 else None),
                bigquery.ScalarQueryParameter("sighted_longitude", "FLOAT64", sighting.sighted_location.longitude if sighting.sighted_location.longitude is not None and sighting.sighted_location.longitude != 0.0 else None),
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
                bigquery.ScalarQueryParameter("verified", "BOOL", sighting.verified),
                bigquery.ScalarQueryParameter("created_by", "STRING", sighting.created_by),
                bigquery.ScalarQueryParameter("notes", "STRING", sighting.notes),
            ]
        )

        # Execute the parameterized query
        query_job = self.client.query(SIGHTING_INSERT_QUERY, job_config=job_config)
        query_job.result()  # Wait for the query to complete

        return sighting.id

    def update_sighting(self, sighting: Sighting) -> bool:
        """Update an existing sighting in BigQuery with AI regeneration and embedding clearing"""
        SIGHTING_UPDATE_QUERY = """
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
        WHEN MATCHED THEN
          UPDATE SET
            sighting_number = source.sighting_number,
            sighted_date = source.sighted_date,
            sighted_time = source.sighted_time,
            sighted_address = source.sighted_address,
            sighted_city = source.sighted_city,
            sighted_country = source.sighted_country,
            sighted_postal_code = source.sighted_postal_code,
            sighted_latitude = source.sighted_latitude,
            sighted_longitude = source.sighted_longitude,
            sighted_geo = source.sighted_geo,
            apparent_gender = source.apparent_gender,
            apparent_age_range = source.apparent_age_range,
            height_estimate = source.height_estimate,
            weight_estimate = source.weight_estimate,
            hair_color = source.hair_color,
            eye_color = source.eye_color,
            clothing_description = source.clothing_description,
            distinguishing_features = source.distinguishing_features,
            description = source.description,
            circumstances = source.circumstances,
            confidence_level = source.confidence_level,
            photo_url = source.photo_url,
            video_url = source.video_url,
            source_type = source.source_type,
            witness_name = source.witness_name,
            witness_phone = source.witness_phone,
            witness_email = source.witness_email,
            video_analytics_result_id = source.video_analytics_result_id,
            status = source.status,
            priority = source.priority,
            verified = source.verified,
            updated_date = source.updated_date,
            created_by = source.created_by,
            notes = source.notes,
            ml_summary = source.ml_summary,
            ml_summary_embedding = NULL;
        """

        try:
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
                    bigquery.ScalarQueryParameter("sighted_latitude", "FLOAT64", sighting.sighted_location.latitude if sighting.sighted_location.latitude is not None and sighting.sighted_location.latitude != 0.0 else None),
                    bigquery.ScalarQueryParameter("sighted_longitude", "FLOAT64", sighting.sighted_location.longitude if sighting.sighted_location.longitude is not None and sighting.sighted_location.longitude != 0.0 else None),
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
                    bigquery.ScalarQueryParameter("verified", "BOOL", sighting.verified),
                    bigquery.ScalarQueryParameter("created_by", "STRING", sighting.created_by),
                    bigquery.ScalarQueryParameter("notes", "STRING", sighting.notes),
                ]
            )

            # Execute the parameterized query
            query_job = self.client.query(SIGHTING_UPDATE_QUERY, job_config=job_config)
            query_job.result()  # Wait for the query to complete

            return True

        except Exception as e:
            print(f"Error updating sighting {sighting.id}: {str(e)}")
            return False

    def search_cases(self, query: str, field: str = "all", page: int = 1, page_size: int = 20) -> tuple[list[MissingPersonCase], int]:
        """Search missing person cases with LIKE filtering"""
        if not query or not query.strip():
            return self.get_cases(page=page, page_size=page_size)

        query = query.strip()
        offset = (page - 1) * page_size

        # Build WHERE clause based on field selection
        where_conditions = []
        if field == "all" or field == "id":
            where_conditions.append("LOWER(id) LIKE @query")
        if field == "all" or field == "full name":
            where_conditions.append("(LOWER(name) LIKE @query OR LOWER(surname) LIKE @query OR LOWER(CONCAT(name, ' ', surname)) LIKE @query)")
        if field == "all":
            # When searching "all", include additional searchable fields
            where_conditions.append("LOWER(description) LIKE @query")
            where_conditions.append("LOWER(circumstances) LIKE @query")
            where_conditions.append("(LOWER(last_seen_address) LIKE @query OR LOWER(last_seen_city) LIKE @query)")
            where_conditions.append("LOWER(case_number) LIKE @query")

        where_clause = " OR ".join(where_conditions) if where_conditions else "1=1"

        # Count query
        COUNT_QUERY = f"""
        SELECT COUNT(id) as total_count
        FROM `homeward.missing_persons`
        WHERE {where_clause}
        """

        # Data query with pagination
        SEARCH_QUERY = f"""
        SELECT
            id, case_number, name, surname, date_of_birth, gender,
            height, weight, hair_color, eye_color, distinguishing_marks, clothing_description,
            last_seen_date, last_seen_time, last_seen_address, last_seen_city,
            last_seen_country, last_seen_postal_code, last_seen_latitude, last_seen_longitude,
            circumstances, priority, status, description, medical_conditions, additional_info,
            photo_url, reporter_name, reporter_phone, reporter_email, relationship,
            created_date, updated_date, ml_summary
        FROM `homeward.missing_persons`
        WHERE {where_clause}
        ORDER BY created_date DESC
        LIMIT @page_size OFFSET @offset
        """

        search_param = f"%{query.lower()}%"

        # Execute count query
        count_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("query", "STRING", search_param)
            ]
        )
        count_job = self.client.query(COUNT_QUERY, job_config=count_job_config)
        total_count = list(count_job.result())[0].total_count

        # Execute data query
        data_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("query", "STRING", search_param),
                bigquery.ScalarQueryParameter("page_size", "INT64", page_size),
                bigquery.ScalarQueryParameter("offset", "INT64", offset)
            ]
        )
        data_job = self.client.query(SEARCH_QUERY, job_config=data_job_config)

        # Convert results to MissingPersonCase objects (reuse existing conversion logic)
        cases = []
        for row in data_job.result():
            # Same conversion logic as in get_cases method
            last_seen_date = row.last_seen_date
            last_seen_time = row.last_seen_time

            if last_seen_date and last_seen_time:
                from datetime import datetime, time
                if isinstance(last_seen_time, time):
                    last_seen_datetime = datetime.combine(last_seen_date, last_seen_time)
                else:
                    last_seen_datetime = datetime.combine(last_seen_date, datetime.min.time())
            else:
                last_seen_datetime = datetime.combine(last_seen_date, datetime.min.time()) if last_seen_date else datetime.now()

            from homeward.models.case import Location, CaseStatus, CasePriority
            location = Location(
                address=row.last_seen_address or "",
                city=row.last_seen_city or "",
                country=row.last_seen_country or "",
                postal_code=row.last_seen_postal_code,
                latitude=row.last_seen_latitude,
                longitude=row.last_seen_longitude
            )

            status = CaseStatus.ACTIVE
            try:
                status = CaseStatus(row.status)
            except ValueError:
                pass

            priority = CasePriority.MEDIUM
            try:
                priority = CasePriority(row.priority)
            except ValueError:
                pass

            from datetime import datetime
            date_of_birth = row.date_of_birth
            if date_of_birth and not isinstance(date_of_birth, datetime):
                date_of_birth = datetime.combine(date_of_birth, datetime.min.time())

            case = MissingPersonCase(
                id=row.id,
                name=row.name or "",
                surname=row.surname or "",
                date_of_birth=date_of_birth or datetime.now(),
                gender=row.gender or "",
                last_seen_date=last_seen_datetime,
                last_seen_location=location,
                status=status,
                circumstances=row.circumstances or "",
                reporter_name=row.reporter_name or "",
                reporter_phone=row.reporter_phone or "",
                relationship=row.relationship or "",
                case_number=row.case_number,
                height=row.height,
                weight=row.weight,
                hair_color=row.hair_color,
                eye_color=row.eye_color,
                distinguishing_marks=row.distinguishing_marks,
                clothing_description=row.clothing_description,
                medical_conditions=row.medical_conditions,
                additional_info=row.additional_info,
                description=row.description,
                photo_url=row.photo_url,
                reporter_email=row.reporter_email,
                created_date=row.created_date or datetime.now(),
                priority=priority,
                ml_summary=row.ml_summary,
            )
            cases.append(case)

        return cases, total_count

    def search_sightings(self, query: str, field: str = "all", page: int = 1, page_size: int = 20) -> tuple[list[Sighting], int]:
        """Search sighting reports with LIKE filtering"""
        if not query or not query.strip():
            return self.get_sightings(page=page, page_size=page_size)

        query = query.strip()
        offset = (page - 1) * page_size

        # Build WHERE clause based on field selection
        where_conditions = []
        if field == "all" or field == "id":
            where_conditions.append("LOWER(id) LIKE @query")
        if field == "all":
            # When searching "all", include additional searchable fields
            where_conditions.append("LOWER(description) LIKE @query")
            where_conditions.append("LOWER(circumstances) LIKE @query")
            where_conditions.append("(LOWER(sighted_address) LIKE @query OR LOWER(sighted_city) LIKE @query)")
            where_conditions.append("LOWER(witness_name) LIKE @query")
            where_conditions.append("LOWER(sighting_number) LIKE @query")

        where_clause = " OR ".join(where_conditions) if where_conditions else "1=1"

        # Count query
        COUNT_QUERY = f"""
        SELECT COUNT(id) as total_count
        FROM `homeward.sightings`
        WHERE {where_clause}
        """

        # Data query with pagination
        SEARCH_QUERY = f"""
        SELECT
            id, sighting_number, sighted_date, sighted_time, sighted_address, sighted_city,
            sighted_country, sighted_postal_code, sighted_latitude, sighted_longitude,
            apparent_gender, apparent_age_range, height_estimate, weight_estimate,
            hair_color, eye_color, clothing_description, distinguishing_features,
            description, circumstances, confidence_level, photo_url, video_url,
            source_type, witness_name, witness_phone, witness_email,
            video_analytics_result_id, status, priority, verified,
            created_date, updated_date, created_by, notes, ml_summary
        FROM `homeward.sightings`
        WHERE {where_clause}
        ORDER BY created_date DESC
        LIMIT @page_size OFFSET @offset
        """

        search_param = f"%{query.lower()}%"

        # Execute count query
        count_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("query", "STRING", search_param)
            ]
        )
        count_job = self.client.query(COUNT_QUERY, job_config=count_job_config)
        total_count = list(count_job.result())[0].total_count

        # Execute data query
        data_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("query", "STRING", search_param),
                bigquery.ScalarQueryParameter("page_size", "INT64", page_size),
                bigquery.ScalarQueryParameter("offset", "INT64", offset)
            ]
        )
        data_job = self.client.query(SEARCH_QUERY, job_config=data_job_config)

        # Convert results to Sighting objects (reuse existing conversion logic)
        sightings = []
        for row in data_job.result():
            # Same conversion logic as in get_sightings method
            sighted_date = row.sighted_date
            sighted_time = row.sighted_time

            if sighted_date and sighted_time:
                from datetime import datetime, time
                if isinstance(sighted_time, time):
                    sighted_datetime = datetime.combine(sighted_date, sighted_time)
                else:
                    sighted_datetime = datetime.combine(sighted_date, datetime.min.time())
            else:
                sighted_datetime = datetime.combine(sighted_date, datetime.min.time()) if sighted_date else datetime.now()

            from homeward.models.case import Location, SightingStatus, SightingPriority, SightingConfidenceLevel, SightingSourceType
            location = Location(
                address=row.sighted_address or "",
                city=row.sighted_city or "",
                country=row.sighted_country or "",
                postal_code=row.sighted_postal_code,
                latitude=row.sighted_latitude,
                longitude=row.sighted_longitude
            )

            status_map = {
                "New": SightingStatus.NEW,
                "Under_Review": SightingStatus.UNDER_REVIEW,
                "Verified": SightingStatus.VERIFIED,
                "False_Positive": SightingStatus.FALSE_POSITIVE,
                "Archived": SightingStatus.ARCHIVED,
            }

            priority_map = {
                "High": SightingPriority.HIGH,
                "Medium": SightingPriority.MEDIUM,
                "Low": SightingPriority.LOW,
            }

            confidence_map = {
                "High": SightingConfidenceLevel.HIGH,
                "Medium": SightingConfidenceLevel.MEDIUM,
                "Low": SightingConfidenceLevel.LOW,
            }

            source_type_map = {
                "Witness": SightingSourceType.WITNESS,
                "Manual_Entry": SightingSourceType.MANUAL_ENTRY,
                "Other": SightingSourceType.OTHER,
            }

            sighting = Sighting(
                id=row.id,
                sighting_number=row.sighting_number,
                sighted_date=sighted_datetime,
                sighted_location=location,
                description=row.description or "",
                confidence_level=confidence_map.get(row.confidence_level, SightingConfidenceLevel.MEDIUM),
                source_type=source_type_map.get(row.source_type, SightingSourceType.OTHER),
                apparent_gender=row.apparent_gender,
                apparent_age_range=row.apparent_age_range,
                height_estimate=row.height_estimate,
                weight_estimate=row.weight_estimate,
                hair_color=row.hair_color,
                eye_color=row.eye_color,
                clothing_description=row.clothing_description,
                distinguishing_features=row.distinguishing_features,
                circumstances=row.circumstances,
                photo_url=row.photo_url,
                video_url=row.video_url,
                witness_name=row.witness_name,
                witness_phone=row.witness_phone,
                witness_email=row.witness_email,
                video_analytics_result_id=row.video_analytics_result_id,
                status=status_map.get(row.status, SightingStatus.NEW),
                priority=priority_map.get(row.priority, SightingPriority.MEDIUM),
                verified=row.verified or False,
                created_date=row.created_date or datetime.now(),
                updated_date=row.updated_date,
                created_by=row.created_by,
                notes=row.notes,
                ml_summary=row.ml_summary
            )
            sightings.append(sighting)

        return sightings, total_count

    def update_missing_persons_embeddings(self) -> dict:
        """Update embeddings for missing persons that don't have them yet"""
        UPDATE_MISSING_PERSONS_EMBEDDINGS_QUERY = """
        UPDATE `homeward.missing_persons` AS mp
        SET mp.ml_summary_embedding = e.ml_generate_embedding_result
        FROM ML.GENERATE_EMBEDDING(
            MODEL `homeward.text_embedding_model`,
            (SELECT id, ml_summary as content FROM `homeward.missing_persons` WHERE ml_summary IS NOT NULL AND (ml_summary_embedding IS NULL OR ARRAY_LENGTH(ml_summary_embedding) = 0)),
            STRUCT('SEMANTIC_SIMILARITY' as task_type)
        ) as e
        WHERE mp.id = e.id;
        """

        try:
            query_job = self.client.query(UPDATE_MISSING_PERSONS_EMBEDDINGS_QUERY)

            # Wait for job completion with timeout
            query_job.result(timeout=120)  # 2 minute timeout for embedding calculation

            # Additional check to ensure embeddings were actually created
            if query_job.num_dml_affected_rows == 0:
                # Check if there are any records that need embeddings
                check_query = """
                SELECT COUNT(*) as records_needing_embeddings
                FROM `homeward.missing_persons`
                WHERE ml_summary IS NOT NULL AND (ml_summary_embedding IS NULL OR ARRAY_LENGTH(ml_summary_embedding) = 0)
                """
                check_job = self.client.query(check_query)
                check_result = list(check_job.result())[0]

                if check_result.records_needing_embeddings > 0:
                    return {
                        "success": False,
                        "rows_modified": 0,
                        "message": f"Embedding calculation failed - {check_result.records_needing_embeddings} records still need embeddings"
                    }

            return {
                "success": True,
                "rows_modified": query_job.num_dml_affected_rows or 0,
                "message": f"Updated embeddings for {query_job.num_dml_affected_rows or 0} missing person records"
            }
        except Exception as e:
            return {
                "success": False,
                "rows_modified": 0,
                "message": f"Error updating embeddings: {str(e)}"
            }

    def update_sightings_embeddings(self) -> dict:
        """Update embeddings for sightings that don't have them yet"""
        UPDATE_SIGHTINGS_EMBEDDINGS_QUERY = """
        UPDATE `homeward.sightings` as s
        SET s.ml_summary_embedding = e.ml_generate_embedding_result
        FROM ML.GENERATE_EMBEDDING(
            MODEL `homeward.text_embedding_model`,
            (SELECT id, ml_summary as content FROM `homeward.sightings` WHERE ml_summary IS NOT NULL AND (ml_summary_embedding IS NULL OR ARRAY_LENGTH(ml_summary_embedding) = 0)),
            STRUCT('SEMANTIC_SIMILARITY' as task_type)
        ) as e
        WHERE e.id = s.id;
        """

        try:
            query_job = self.client.query(UPDATE_SIGHTINGS_EMBEDDINGS_QUERY)

            # Wait for job completion with timeout
            query_job.result(timeout=120)  # 2 minute timeout for embedding calculation

            # Additional check to ensure embeddings were actually created
            if query_job.num_dml_affected_rows == 0:
                # Check if there are any records that need embeddings
                check_query = """
                SELECT COUNT(*) as records_needing_embeddings
                FROM `homeward.sightings`
                WHERE ml_summary IS NOT NULL AND (ml_summary_embedding IS NULL OR ARRAY_LENGTH(ml_summary_embedding) = 0)
                """
                check_job = self.client.query(check_query)
                check_result = list(check_job.result())[0]

                if check_result.records_needing_embeddings > 0:
                    return {
                        "success": False,
                        "rows_modified": 0,
                        "message": f"Embedding calculation failed - {check_result.records_needing_embeddings} records still need embeddings"
                    }

            return {
                "success": True,
                "rows_modified": query_job.num_dml_affected_rows or 0,
                "message": f"Updated embeddings for {query_job.num_dml_affected_rows or 0} sighting records"
            }
        except Exception as e:
            return {
                "success": False,
                "rows_modified": 0,
                "message": f"Error updating embeddings: {str(e)}"
            }

    def find_similar_sightings_for_missing_person(self, missing_person_id: str, search_radius_meters: float = 10000.0, delta_days: int = 30, top_k: int = 5) -> list[dict]:
        """Find sightings similar to a missing person using vector search - matches demo notebook implementation"""

        # First get the missing person details for geo/time filtering
        missing_person = self.get_case_by_id(missing_person_id)
        if not missing_person:
            print(f"Missing person with id {missing_person_id} not found")
            return []

        # Verify that the missing person has embeddings
        check_embeddings_query = """
        SELECT
            COUNT(*) as mp_with_embeddings,
            (SELECT COUNT(*) FROM `homeward.sightings` WHERE ml_summary_embedding IS NOT NULL AND ARRAY_LENGTH(ml_summary_embedding) > 0) as sightings_with_embeddings
        FROM `homeward.missing_persons`
        WHERE id = @missing_person_id
        AND ml_summary_embedding IS NOT NULL
        AND ARRAY_LENGTH(ml_summary_embedding) > 0
        """

        check_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("missing_person_id", "STRING", missing_person_id)
            ]
        )

        try:
            check_job = self.client.query(check_embeddings_query, job_config=check_job_config)
            check_result = list(check_job.result())[0]

            if check_result.mp_with_embeddings == 0:
                print(f"Missing person {missing_person_id} has no embeddings calculated")
                return []

            if check_result.sightings_with_embeddings == 0:
                print("No sightings have embeddings calculated")
                return []

            print(f"Found embeddings: {check_result.mp_with_embeddings} missing person, {check_result.sightings_with_embeddings} sightings")

        except Exception as e:
            print(f"Error checking embeddings: {str(e)}")
            return []

        # Corrected query structure based on demo notebook
        SIMILARITY_SEARCH_MP_TO_SIGHTINGS_QUERY = """
        SELECT
        query.id,
        query.case_number,
        distance,
        base.id,
        base.sighting_number,
        base.sighted_date,
        base.sighted_time,
        base.sighted_city,
        base.sighted_geo,
        base.witness_name,
        base.confidence_level,
        base.ml_summary,
        ST_DISTANCE(
          base.sighted_geo,
          ST_GEOGPOINT(@last_seen_longitude, @last_seen_latitude)
        ) / 1000 as distance_km
        FROM
        VECTOR_SEARCH(
            (
              SELECT *
              FROM
                `homeward.sightings`
              WHERE
                DATE(created_date) >= DATE_SUB(@last_seen_date, INTERVAL @delta_days DAY)
            ),
            'ml_summary_embedding',
            (SELECT id, case_number, ml_summary_embedding FROM `homeward.missing_persons` WHERE id = @missing_person_id),
            top_k => @top_k,
            distance_type => 'COSINE',
            options => '{"fraction_lists_to_search": 0.005}')
        WHERE ST_DWITHIN(
          base.sighted_geo,
          ST_GEOGPOINT(@last_seen_longitude, @last_seen_latitude),
          @search_radius_meters
        );
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("missing_person_id", "STRING", missing_person_id),
                bigquery.ScalarQueryParameter("last_seen_latitude", "FLOAT64", missing_person.last_seen_location.latitude),
                bigquery.ScalarQueryParameter("last_seen_longitude", "FLOAT64", missing_person.last_seen_location.longitude),
                bigquery.ScalarQueryParameter("search_radius_meters", "FLOAT64", search_radius_meters),
                bigquery.ScalarQueryParameter("last_seen_date", "DATE", missing_person.last_seen_date.date()),
                bigquery.ScalarQueryParameter("delta_days", "INT64", delta_days),
                bigquery.ScalarQueryParameter("top_k", "INT64", top_k)
            ]
        )

        try:
            query_job = self.client.query(SIMILARITY_SEARCH_MP_TO_SIGHTINGS_QUERY, job_config=job_config)
            results = query_job.result()

            similar_sightings = []
            for row in results:
                similar_sightings.append({
                    "missing_person_id": row[0],
                    "case_number": row[1],
                    "similarity_distance": float(row[2]),
                    "sighting_id": row[3],
                    "sighting_number": row[4],
                    "sighted_date": row[5],
                    "sighted_time": row[6],
                    "sighted_city": row[7],
                    "witness_name": row[9],
                    "confidence_level": row[10],
                    "ml_summary": row[11],
                    "distance_km": float(row[12])
                })

            return similar_sightings

        except Exception as e:
            print(f"Error executing similarity search: {str(e)}")
            return []

    def find_similar_missing_persons_for_sighting(self, sighting_id: str, search_radius_meters: float = 10000.0, delta_days: int = 30, top_k: int = 5) -> list[dict]:
        """Find missing persons similar to a sighting using vector search - reverse of sighting search"""
        # First get the sighting details for geo/time filtering
        sighting = self.get_sighting_by_id(sighting_id)
        if not sighting:
            print(f"Sighting with id {sighting_id} not found")
            return []

        # Verify that the sighting has embeddings
        check_embeddings_query = """
        SELECT
            COUNT(*) as sighting_with_embeddings,
            (SELECT COUNT(*) FROM `homeward.missing_persons` WHERE ml_summary_embedding IS NOT NULL AND ARRAY_LENGTH(ml_summary_embedding) > 0) as mp_with_embeddings
        FROM `homeward.sightings`
        WHERE id = @sighting_id
        AND ml_summary_embedding IS NOT NULL
        AND ARRAY_LENGTH(ml_summary_embedding) > 0
        """

        check_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("sighting_id", "STRING", sighting_id)
            ]
        )

        try:
            check_job = self.client.query(check_embeddings_query, job_config=check_job_config)
            check_result = list(check_job.result())[0]

            if check_result.sighting_with_embeddings == 0:
                print(f"Sighting {sighting_id} has no embeddings calculated")
                return []

            if check_result.mp_with_embeddings == 0:
                print("No missing persons have embeddings calculated")
                return []

            print(f"Found embeddings: {check_result.sighting_with_embeddings} sighting, {check_result.mp_with_embeddings} missing persons")

        except Exception as e:
            print(f"Error checking embeddings: {str(e)}")
            return []

        # Query structure based on SIMILARITY_SEARCH_SIGHTINGS_TO_MP_QUERY from demo notebook
        SIMILARITY_SEARCH_SIGHTINGS_TO_MP_QUERY = """
        SELECT
        query.id as sighting_id,
        query.sighting_number,
        distance,
        base.id,
        base.case_number,
        base.name,
        base.surname,
        base.age,
        base.gender,
        base.priority,
        base.last_seen_date,
        base.last_seen_city,
        base.ml_summary,
        ST_DISTANCE(
          base.last_seen_geo,
          ST_GEOGPOINT(@sighted_longitude, @sighted_latitude)
        ) / 1000 as distance_km
        FROM
          VECTOR_SEARCH(
            (
              SELECT *
              FROM
                `homeward.missing_persons`
              WHERE
                DATE(created_date) >= DATE_SUB(@sighted_date, INTERVAL @delta_days DAY)
            ),
            'ml_summary_embedding',
            (SELECT id, sighting_number, ml_summary_embedding FROM `homeward.sightings` WHERE id = @sighting_id),
            top_k => @top_k,
            distance_type => 'COSINE',
            options => '{"fraction_lists_to_search": 0.005}')
        WHERE ST_DWITHIN(
          base.last_seen_geo,
          ST_GEOGPOINT(@sighted_longitude, @sighted_latitude),
          @search_radius_meters
        );
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("sighting_id", "STRING", sighting_id),
                bigquery.ScalarQueryParameter("sighted_latitude", "FLOAT64", sighting.sighted_location.latitude),
                bigquery.ScalarQueryParameter("sighted_longitude", "FLOAT64", sighting.sighted_location.longitude),
                bigquery.ScalarQueryParameter("search_radius_meters", "FLOAT64", search_radius_meters),
                bigquery.ScalarQueryParameter("sighted_date", "DATE", sighting.sighted_date.date()),
                bigquery.ScalarQueryParameter("delta_days", "INT64", delta_days),
                bigquery.ScalarQueryParameter("top_k", "INT64", top_k)
            ]
        )

        try:
            query_job = self.client.query(SIMILARITY_SEARCH_SIGHTINGS_TO_MP_QUERY, job_config=job_config)
            results = query_job.result()

            similar_cases = []
            for row in results:
                similar_cases.append({
                    "sighting_id": row[0],
                    "sighting_number": row[1],
                    "similarity_distance": float(row[2]),
                    "id": row[3],
                    "case_number": row[4],
                    "name": row[5],
                    "surname": row[6],
                    "age": int(row[7]) if row[7] is not None else None,
                    "gender": row[8],
                    "priority": row[9],
                    "last_seen_date": row[10],
                    "last_seen_city": row[11],
                    "ml_summary": row[12],
                    "distance_km": float(row[13])
                })

            return similar_cases

        except Exception as e:
            print(f"Error executing reverse similarity search: {str(e)}")
            return []

    def get_case_sightings(self, case_id: str) -> list[dict]:
        """Get all sightings linked to a specific case from the case_sightings table"""
        CASE_SIGHTINGS_QUERY = """
        SELECT
            cs.id as link_id,
            cs.missing_person_id,
            cs.sighting_id,
            cs.match_confidence,
            cs.match_type,
            cs.match_reason,
            cs.status,
            cs.confirmed,
            cs.confirmed_by,
            cs.confirmed_date,
            cs.similarity_score,
            cs.physical_match_score,
            cs.temporal_match_score,
            cs.geographical_match_score,
            cs.investigated,
            cs.investigation_notes,
            cs.investigator_name,
            cs.investigation_date,
            cs.priority,
            cs.requires_review,
            cs.review_notes,
            cs.created_date,
            cs.updated_date,
            cs.created_by,
            cs.distance_km,
            cs.time_difference_hours,
            s.sighting_number,
            s.sighted_date,
            s.sighted_time,
            s.sighted_address,
            s.sighted_city,
            s.sighted_country,
            s.sighted_latitude,
            s.sighted_longitude,
            s.apparent_gender,
            s.apparent_age_range,
            s.height_estimate,
            s.weight_estimate,
            s.hair_color,
            s.eye_color,
            s.clothing_description,
            s.distinguishing_features,
            s.description as sighting_description,
            s.circumstances as sighting_circumstances,
            s.confidence_level,
            s.photo_url,
            s.video_url,
            s.source_type,
            s.witness_name,
            s.witness_phone,
            s.witness_email,
            s.video_analytics_result_id,
            s.status as sighting_status,
            s.priority as sighting_priority,
            s.verified,
            s.notes as sighting_notes,
            s.ml_summary as sighting_ml_summary
        FROM `homeward.case_sightings` cs
        JOIN `homeward.sightings` s ON cs.sighting_id = s.id
        WHERE cs.missing_person_id = @case_id
        ORDER BY cs.created_date DESC, cs.match_confidence DESC
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("case_id", "STRING", case_id)
            ]
        )

        try:
            query_job = self.client.query(CASE_SIGHTINGS_QUERY, job_config=job_config)
            results = query_job.result()

            case_sightings = []
            for row in results:
                # Combine date and time for sighted_date
                sighted_date = row.sighted_date
                sighted_time = row.sighted_time

                if sighted_date and sighted_time:
                    from datetime import datetime, time
                    if isinstance(sighted_time, time):
                        sighted_datetime = datetime.combine(sighted_date, sighted_time)
                    else:
                        sighted_datetime = datetime.combine(sighted_date, datetime.min.time())
                else:
                    sighted_datetime = datetime.combine(sighted_date, datetime.min.time()) if sighted_date else datetime.now()

                case_sightings.append({
                    # Case sighting link data
                    "link_id": row.link_id,
                    "missing_person_id": row.missing_person_id,
                    "sighting_id": row.sighting_id,
                    "match_confidence": float(row.match_confidence) if row.match_confidence else 0.0,
                    "match_type": row.match_type,
                    "match_reason": row.match_reason,
                    "status": row.status,
                    "confirmed": row.confirmed,
                    "confirmed_by": row.confirmed_by,
                    "confirmed_date": row.confirmed_date,
                    "similarity_score": float(row.similarity_score) if row.similarity_score else None,
                    "physical_match_score": float(row.physical_match_score) if row.physical_match_score else None,
                    "temporal_match_score": float(row.temporal_match_score) if row.temporal_match_score else None,
                    "geographical_match_score": float(row.geographical_match_score) if row.geographical_match_score else None,
                    "investigated": row.investigated,
                    "investigation_notes": row.investigation_notes,
                    "investigator_name": row.investigator_name,
                    "investigation_date": row.investigation_date,
                    "priority": row.priority,
                    "requires_review": row.requires_review,
                    "review_notes": row.review_notes,
                    "created_date": row.created_date,
                    "updated_date": row.updated_date,
                    "created_by": row.created_by,
                    "distance_km": float(row.distance_km) if row.distance_km else None,
                    "time_difference_hours": int(row.time_difference_hours) if row.time_difference_hours else None,

                    # Sighting data
                    "sighting_number": row.sighting_number,
                    "sighted_date": sighted_datetime,
                    "sighted_address": row.sighted_address,
                    "sighted_city": row.sighted_city,
                    "sighted_country": row.sighted_country,
                    "sighted_latitude": row.sighted_latitude,
                    "sighted_longitude": row.sighted_longitude,
                    "apparent_gender": row.apparent_gender,
                    "apparent_age_range": row.apparent_age_range,
                    "height_estimate": row.height_estimate,
                    "weight_estimate": row.weight_estimate,
                    "hair_color": row.hair_color,
                    "eye_color": row.eye_color,
                    "clothing_description": row.clothing_description,
                    "distinguishing_features": row.distinguishing_features,
                    "sighting_description": row.sighting_description,
                    "sighting_circumstances": row.sighting_circumstances,
                    "confidence_level": row.confidence_level,
                    "photo_url": row.photo_url,
                    "video_url": row.video_url,
                    "source_type": row.source_type,
                    "witness_name": row.witness_name,
                    "witness_phone": row.witness_phone,
                    "witness_email": row.witness_email,
                    "video_analytics_result_id": row.video_analytics_result_id,
                    "sighting_status": row.sighting_status,
                    "sighting_priority": row.sighting_priority,
                    "verified": row.verified,
                    "sighting_notes": row.sighting_notes,
                    "sighting_ml_summary": row.sighting_ml_summary
                })

            return case_sightings

        except Exception as e:
            print(f"Error retrieving case sightings for case {case_id}: {str(e)}")
            return []

    def link_sighting_to_case(self, sighting_id: str, case_id: str, match_confidence: float = 0.5, match_type: str = "Manual", match_reason: str = None) -> bool:
        """Link a sighting to a missing person case by inserting into case_sightings table"""
        try:
            from datetime import datetime
            import uuid

            # Generate unique ID for the link
            link_id = str(uuid.uuid4())
            current_time = datetime.now()

            # Determine priority based on confidence
            priority = "High" if match_confidence >= 0.8 else "Medium" if match_confidence >= 0.6 else "Low"

            # Determine status based on match type and confidence
            if match_type == "AI_Analysis":
                status = "Potential" if match_confidence < 0.9 else "Under_Review"
                requires_review = True
            else:
                status = "Under_Review"
                requires_review = False

            # Prepare the INSERT query
            INSERT_LINK_QUERY = """
            INSERT INTO `homeward.case_sightings` (
                id, missing_person_id, sighting_id, match_confidence, match_type, match_reason,
                status, confirmed, confirmed_by, confirmed_date, similarity_score,
                investigated, investigation_notes, investigator_name, investigation_date,
                priority, requires_review, review_notes, created_date, updated_date, created_by
            ) VALUES (
                @link_id, @missing_person_id, @sighting_id, @match_confidence, @match_type, @match_reason,
                @status, @confirmed, @confirmed_by, @confirmed_date, @similarity_score,
                @investigated, @investigation_notes, @investigator_name, @investigation_date,
                @priority, @requires_review, @review_notes, @created_date, @updated_date, @created_by
            )
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("link_id", "STRING", link_id),
                    bigquery.ScalarQueryParameter("missing_person_id", "STRING", case_id),
                    bigquery.ScalarQueryParameter("sighting_id", "STRING", sighting_id),
                    bigquery.ScalarQueryParameter("match_confidence", "FLOAT64", match_confidence),
                    bigquery.ScalarQueryParameter("match_type", "STRING", match_type),
                    bigquery.ScalarQueryParameter("match_reason", "STRING", match_reason),
                    bigquery.ScalarQueryParameter("status", "STRING", status),
                    bigquery.ScalarQueryParameter("confirmed", "BOOL", False),
                    bigquery.ScalarQueryParameter("confirmed_by", "STRING", None),
                    bigquery.ScalarQueryParameter("confirmed_date", "TIMESTAMP", None),
                    bigquery.ScalarQueryParameter("similarity_score", "FLOAT64", match_confidence),
                    bigquery.ScalarQueryParameter("investigated", "BOOL", False),
                    bigquery.ScalarQueryParameter("investigation_notes", "STRING", None),
                    bigquery.ScalarQueryParameter("investigator_name", "STRING", None),
                    bigquery.ScalarQueryParameter("investigation_date", "TIMESTAMP", None),
                    bigquery.ScalarQueryParameter("priority", "STRING", priority),
                    bigquery.ScalarQueryParameter("requires_review", "BOOL", requires_review),
                    bigquery.ScalarQueryParameter("review_notes", "STRING", None),
                    bigquery.ScalarQueryParameter("created_date", "TIMESTAMP", current_time),
                    bigquery.ScalarQueryParameter("updated_date", "TIMESTAMP", current_time),
                    bigquery.ScalarQueryParameter("created_by", "STRING", "System_User")
                ]
            )

            # Execute the insert query
            query_job = self.client.query(INSERT_LINK_QUERY, job_config=job_config)
            query_job.result()  # Wait for the job to complete

            print(f"Successfully linked sighting {sighting_id} to case {case_id} with confidence {match_confidence}")
            return True

        except Exception as e:
            print(f"Error linking sighting to case: {str(e)}")
            return False

    def get_linked_case_for_sighting(self, sighting_id: str) -> dict:
        """Get the linked case information for a sighting by querying case_sightings table"""
        try:
            # Query to get the linked case for a sighting
            LINKED_CASE_QUERY = """
            SELECT
                cs.missing_person_id as case_id,
                mp.case_number,
                mp.name as case_name,
                mp.surname as case_surname,
                mp.status,
                mp.priority,
                mp.last_seen_city,
                mp.created_date,
                cs.match_confidence,
                cs.match_type,
                cs.confirmed,
                cs.status as link_status,
                cs.created_date as link_created_date
            FROM `homeward.case_sightings` cs
            JOIN `homeward.missing_persons` mp ON cs.missing_person_id = mp.id
            WHERE cs.sighting_id = @sighting_id
            AND cs.status IN ('Potential', 'Under_Review', 'Confirmed')
            ORDER BY cs.created_date DESC
            LIMIT 1
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("sighting_id", "STRING", sighting_id)
                ]
            )

            query_job = self.client.query(LINKED_CASE_QUERY, job_config=job_config)
            results = query_job.result()

            for row in results:
                return {
                    "case_id": row.case_id,
                    "case_number": row.case_number,
                    "case_name": row.case_name,
                    "case_surname": row.case_surname,
                    "status": row.status,
                    "priority": row.priority,
                    "last_seen_city": row.last_seen_city,
                    "created_date": row.created_date.strftime("%Y-%m-%d") if row.created_date else None,
                    "match_confidence": row.match_confidence,
                    "match_type": row.match_type,
                    "confirmed": row.confirmed,
                    "link_status": row.link_status,
                    "link_created_date": row.link_created_date.strftime("%Y-%m-%d") if row.link_created_date else None
                }

            # No confirmed link found
            return None

        except Exception as e:
            print(f"Error getting linked case for sighting {sighting_id}: {str(e)}")
            return None

    def search_cases_by_location(self, latitude: float, longitude: float, radius_km: float, page: int = 1, page_size: int = 20) -> tuple[list[MissingPersonCase], int]:
        """Search missing person cases by geographic location using BigQuery geo functions"""

        # Calculate offset
        offset = (page - 1) * page_size

        # Count query using ST_DWITHIN for geographic distance filtering
        COUNT_QUERY = """
        SELECT COUNT(id) as total_count
        FROM `homeward.missing_persons`
        WHERE last_seen_latitude IS NOT NULL
            AND last_seen_longitude IS NOT NULL
            AND ST_DWITHIN(
                ST_GEOGPOINT(last_seen_longitude, last_seen_latitude),
                ST_GEOGPOINT(@search_longitude, @search_latitude),
                @radius_meters
            )
        """

        # Data query with geographic filtering and distance calculation
        CASES_QUERY = """
        SELECT
            id, case_number, name, surname, date_of_birth, gender,
            height, weight, hair_color, eye_color, distinguishing_marks, clothing_description,
            last_seen_date, last_seen_time, last_seen_address, last_seen_city,
            last_seen_country, last_seen_postal_code, last_seen_latitude, last_seen_longitude,
            circumstances, priority, status, description, medical_conditions, additional_info,
            photo_url, reporter_name, reporter_phone, reporter_email, relationship,
            created_date, updated_date, ml_summary,
            ST_DISTANCE(
                ST_GEOGPOINT(last_seen_longitude, last_seen_latitude),
                ST_GEOGPOINT(@search_longitude, @search_latitude)
            ) / 1000 as distance_km
        FROM `homeward.missing_persons`
        WHERE last_seen_latitude IS NOT NULL
            AND last_seen_longitude IS NOT NULL
            AND ST_DWITHIN(
                ST_GEOGPOINT(last_seen_longitude, last_seen_latitude),
                ST_GEOGPOINT(@search_longitude, @search_latitude),
                @radius_meters
            )
        ORDER BY distance_km ASC, created_date DESC
        LIMIT @page_size OFFSET @offset
        """

        try:
            # Convert radius from km to meters for BigQuery ST_DWITHIN
            radius_meters = radius_km * 1000

            # Execute count query
            count_job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("search_latitude", "FLOAT64", latitude),
                    bigquery.ScalarQueryParameter("search_longitude", "FLOAT64", longitude),
                    bigquery.ScalarQueryParameter("radius_meters", "FLOAT64", radius_meters)
                ]
            )
            count_query_job = self.client.query(COUNT_QUERY, job_config=count_job_config)
            count_results = count_query_job.result()
            total_count = next(count_results).total_count

            # Execute data query
            data_job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("search_latitude", "FLOAT64", latitude),
                    bigquery.ScalarQueryParameter("search_longitude", "FLOAT64", longitude),
                    bigquery.ScalarQueryParameter("radius_meters", "FLOAT64", radius_meters),
                    bigquery.ScalarQueryParameter("page_size", "INT64", page_size),
                    bigquery.ScalarQueryParameter("offset", "INT64", offset)
                ]
            )
            data_query_job = self.client.query(CASES_QUERY, job_config=data_job_config)
            data_results = data_query_job.result()

            # Convert results to MissingPersonCase objects
            cases = []
            for row in data_results:
                case = self._row_to_missing_person_case(row)
                cases.append(case)

            return cases, total_count

        except Exception as e:
            print(f"Error searching cases by location: {str(e)}")
            return [], 0

    def search_sightings_by_location(self, latitude: float, longitude: float, radius_km: float, page: int = 1, page_size: int = 20) -> tuple[list[Sighting], int]:
        """Search sighting reports by geographic location using BigQuery geo functions"""

        # Calculate offset
        offset = (page - 1) * page_size

        # Count query using ST_DWITHIN for geographic distance filtering
        COUNT_QUERY = """
        SELECT COUNT(id) as total_count
        FROM `homeward.sightings`
        WHERE sighted_latitude IS NOT NULL
            AND sighted_longitude IS NOT NULL
            AND ST_DWITHIN(
                ST_GEOGPOINT(sighted_longitude, sighted_latitude),
                ST_GEOGPOINT(@search_longitude, @search_latitude),
                @radius_meters
            )
        """

        # Data query with geographic filtering and distance calculation
        SIGHTINGS_QUERY = """
        SELECT
            id, witness_name, witness_email, witness_phone, sighted_date,
            sighted_address, sighted_city, sighted_country, sighted_postal_code,
            sighted_latitude, sighted_longitude, individual_age, apparent_gender,
            height_estimate, weight_estimate, hair_color, clothing_description,
            distinguishing_features, description, confidence_level, source_type,
            created_date, updated_date, ml_summary,
            ST_DISTANCE(
                ST_GEOGPOINT(sighted_longitude, sighted_latitude),
                ST_GEOGPOINT(@search_longitude, @search_latitude)
            ) / 1000 as distance_km
        FROM `homeward.sightings`
        WHERE sighted_latitude IS NOT NULL
            AND sighted_longitude IS NOT NULL
            AND ST_DWITHIN(
                ST_GEOGPOINT(sighted_longitude, sighted_latitude),
                ST_GEOGPOINT(@search_longitude, @search_latitude),
                @radius_meters
            )
        ORDER BY distance_km ASC, created_date DESC
        LIMIT @page_size OFFSET @offset
        """

        try:
            # Convert radius from km to meters for BigQuery ST_DWITHIN
            radius_meters = radius_km * 1000

            # Execute count query
            count_job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("search_latitude", "FLOAT64", latitude),
                    bigquery.ScalarQueryParameter("search_longitude", "FLOAT64", longitude),
                    bigquery.ScalarQueryParameter("radius_meters", "FLOAT64", radius_meters)
                ]
            )
            count_query_job = self.client.query(COUNT_QUERY, job_config=count_job_config)
            count_results = count_query_job.result()
            total_count = next(count_results).total_count

            # Execute data query
            data_job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("search_latitude", "FLOAT64", latitude),
                    bigquery.ScalarQueryParameter("search_longitude", "FLOAT64", longitude),
                    bigquery.ScalarQueryParameter("radius_meters", "FLOAT64", radius_meters),
                    bigquery.ScalarQueryParameter("page_size", "INT64", page_size),
                    bigquery.ScalarQueryParameter("offset", "INT64", offset)
                ]
            )
            data_query_job = self.client.query(SIGHTINGS_QUERY, job_config=data_job_config)
            data_results = data_query_job.result()

            # Convert results to Sighting objects
            sightings = []
            for row in data_results:
                sighting = self._row_to_sighting(row)
                sightings.append(sighting)

            return sightings, total_count

        except Exception as e:
            print(f"Error searching sightings by location: {str(e)}")
            return [], 0

    def _row_to_missing_person_case(self, row):
        """Convert BigQuery row to MissingPersonCase object"""
        # Combine date and time for last_seen_date
        last_seen_date = row.last_seen_date
        last_seen_time = row.last_seen_time

        if last_seen_date and last_seen_time:
            from datetime import datetime, time
            if isinstance(last_seen_time, time):
                last_seen_datetime = datetime.combine(last_seen_date, last_seen_time)
            else:
                last_seen_datetime = datetime.combine(last_seen_date, datetime.min.time())
        else:
            last_seen_datetime = datetime.combine(last_seen_date, datetime.min.time()) if last_seen_date else datetime.now()

        # Create Location object
        from homeward.models.case import Location, CaseStatus, CasePriority
        location = Location(
            address=row.last_seen_address or "",
            city=row.last_seen_city or "",
            country=row.last_seen_country or "",
            postal_code=row.last_seen_postal_code,
            latitude=row.last_seen_latitude,
            longitude=row.last_seen_longitude
        )

        # Parse enum values
        status = CaseStatus.ACTIVE
        try:
            status = CaseStatus(row.status)
        except ValueError:
            pass

        priority = CasePriority.MEDIUM
        try:
            priority = CasePriority(row.priority)
        except ValueError:
            pass

        # Convert date_of_birth from date to datetime
        from datetime import datetime
        date_of_birth = row.date_of_birth
        if date_of_birth and not isinstance(date_of_birth, datetime):
            date_of_birth = datetime.combine(date_of_birth, datetime.min.time())

        # Create MissingPersonCase object
        case = MissingPersonCase(
            id=row.id,
            name=row.name or "",
            surname=row.surname or "",
            date_of_birth=date_of_birth or datetime.now(),
            gender=row.gender or "",
            last_seen_date=last_seen_datetime,
            last_seen_location=location,
            status=status,
            circumstances=row.circumstances or "",
            reporter_name=row.reporter_name or "",
            reporter_phone=row.reporter_phone or "",
            relationship=row.relationship or "",
            case_number=row.case_number,
            height=row.height,
            weight=row.weight,
            hair_color=row.hair_color,
            eye_color=row.eye_color,
            distinguishing_marks=row.distinguishing_marks,
            clothing_description=row.clothing_description,
            medical_conditions=row.medical_conditions,
            additional_info=row.additional_info,
            description=row.description,
            photo_url=row.photo_url,
            reporter_email=row.reporter_email,
            created_date=row.created_date or datetime.now(),
            priority=priority,
            ml_summary=row.ml_summary,
        )
        return case

    def _row_to_sighting(self, row):
        """Convert BigQuery row to Sighting object"""
        from homeward.models.case import Location, Sighting, ConfidenceLevel, SourceType
        from datetime import datetime

        # Create Location object
        location = Location(
            address=row.sighted_address or "",
            city=row.sighted_city or "",
            country=row.sighted_country or "",
            postal_code=row.sighted_postal_code,
            latitude=row.sighted_latitude,
            longitude=row.sighted_longitude
        )

        # Parse enum values
        confidence_level = ConfidenceLevel.MEDIUM
        try:
            confidence_level = ConfidenceLevel(row.confidence_level)
        except (ValueError, AttributeError):
            pass

        source_type = SourceType.WITNESS
        try:
            source_type = SourceType(row.source_type)
        except (ValueError, AttributeError):
            pass

        # Create Sighting object
        sighting = Sighting(
            id=row.id,
            witness_name=row.witness_name or "",
            witness_email=row.witness_email or "",
            witness_phone=row.witness_phone or "",
            sighted_date=row.sighted_date or datetime.now(),
            sighted_location=location,
            individual_age=row.individual_age,
            apparent_gender=row.apparent_gender or "",
            height_estimate=row.height_estimate,
            weight_estimate=row.weight_estimate,
            hair_color=row.hair_color or "",
            clothing_description=row.clothing_description or "",
            distinguishing_features=row.distinguishing_features or "",
            description=row.description or "",
            confidence_level=confidence_level,
            source_type=source_type,
            created_date=row.created_date or datetime.now(),
            ml_summary=row.ml_summary
        )
        return sighting

    def search_cases_semantic(self, query: str, page: int = 1, page_size: int = 20) -> tuple[list[MissingPersonCase], int]:
        """Perform semantic search on missing person cases using embeddings and cosine similarity"""

        if not query or not query.strip():
            return self.get_cases(page=page, page_size=page_size)

        # Calculate offset
        offset = (page - 1) * page_size

        # Generate embedding for the search query
        EMBEDDING_QUERY = """
        SELECT ml_generate_embedding_result
        FROM ML.GENERATE_EMBEDDING(
            MODEL `homeward.text_embedding_model`,
            (SELECT @query_text as content),
            STRUCT('SEMANTIC_SIMILARITY' as task_type)
        )
        """

        # Get query embedding
        try:
            embedding_job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("query_text", "STRING", query.strip())
                ]
            )
            embedding_job = self.client.query(EMBEDDING_QUERY, job_config=embedding_job_config)
            embedding_result = list(embedding_job.result())[0]
            query_embedding = embedding_result.ml_generate_embedding_result

            if not query_embedding:
                # Fallback to regular cases if embedding generation fails
                return self.get_cases(page=page, page_size=page_size)

        except Exception as e:
            print(f"Error generating embedding for query: {str(e)}")
            # Fallback to regular cases if embedding generation fails
            return self.get_cases(page=page, page_size=page_size)

        # Count query for semantic search results
        COUNT_QUERY = """
        SELECT COUNT(*) as total_count
        FROM `homeward.missing_persons`
        WHERE ml_summary_embedding IS NOT NULL
        AND ARRAY_LENGTH(ml_summary_embedding) > 0
        AND ml_summary IS NOT NULL
        """

        # Semantic search query with cosine similarity
        SEMANTIC_SEARCH_QUERY = """
        SELECT
            id, case_number, name, surname, date_of_birth, gender,
            height, weight, hair_color, eye_color, distinguishing_marks, clothing_description,
            last_seen_date, last_seen_time, last_seen_address, last_seen_city,
            last_seen_country, last_seen_postal_code, last_seen_latitude, last_seen_longitude,
            circumstances, priority, status, description, medical_conditions, additional_info,
            photo_url, reporter_name, reporter_phone, reporter_email, relationship,
            created_date, updated_date, ml_summary,
            ML.DISTANCE(ml_summary_embedding, @query_embedding, 'COSINE') as cosine_distance
        FROM `homeward.missing_persons`
        WHERE ml_summary_embedding IS NOT NULL
        AND ARRAY_LENGTH(ml_summary_embedding) > 0
        AND ml_summary IS NOT NULL
        ORDER BY cosine_distance ASC
        LIMIT @page_size OFFSET @offset
        """

        try:
            # Execute count query
            count_job = self.client.query(COUNT_QUERY)
            total_count = list(count_job.result())[0].total_count

            # Execute semantic search query
            search_job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ArrayQueryParameter("query_embedding", "FLOAT64", query_embedding),
                    bigquery.ScalarQueryParameter("page_size", "INT64", page_size),
                    bigquery.ScalarQueryParameter("offset", "INT64", offset)
                ]
            )
            search_job = self.client.query(SEMANTIC_SEARCH_QUERY, job_config=search_job_config)

            # Convert results to MissingPersonCase objects
            cases = []
            for row in search_job.result():
                # Same conversion logic as get_cases method
                last_seen_date = row.last_seen_date
                last_seen_time = row.last_seen_time

                if last_seen_date and last_seen_time:
                    from datetime import datetime, time
                    if isinstance(last_seen_time, time):
                        last_seen_datetime = datetime.combine(last_seen_date, last_seen_time)
                    else:
                        last_seen_datetime = datetime.combine(last_seen_date, datetime.min.time())
                else:
                    last_seen_datetime = datetime.combine(last_seen_date, datetime.min.time()) if last_seen_date else datetime.now()

                from homeward.models.case import Location, CaseStatus, CasePriority
                location = Location(
                    address=row.last_seen_address or "",
                    city=row.last_seen_city or "",
                    country=row.last_seen_country or "",
                    postal_code=row.last_seen_postal_code,
                    latitude=row.last_seen_latitude,
                    longitude=row.last_seen_longitude
                )

                status = CaseStatus.ACTIVE
                try:
                    status = CaseStatus(row.status)
                except ValueError:
                    pass

                priority = CasePriority.MEDIUM
                try:
                    priority = CasePriority(row.priority)
                except ValueError:
                    pass

                from datetime import datetime
                date_of_birth = row.date_of_birth
                if date_of_birth and not isinstance(date_of_birth, datetime):
                    date_of_birth = datetime.combine(date_of_birth, datetime.min.time())

                case = MissingPersonCase(
                    id=row.id,
                    name=row.name or "",
                    surname=row.surname or "",
                    date_of_birth=date_of_birth or datetime.now(),
                    gender=row.gender or "",
                    last_seen_date=last_seen_datetime,
                    last_seen_location=location,
                    status=status,
                    circumstances=row.circumstances or "",
                    reporter_name=row.reporter_name or "",
                    reporter_phone=row.reporter_phone or "",
                    relationship=row.relationship or "",
                    case_number=row.case_number,
                    height=row.height,
                    weight=row.weight,
                    hair_color=row.hair_color,
                    eye_color=row.eye_color,
                    distinguishing_marks=row.distinguishing_marks,
                    clothing_description=row.clothing_description,
                    medical_conditions=row.medical_conditions,
                    additional_info=row.additional_info,
                    description=row.description,
                    photo_url=row.photo_url,
                    reporter_email=row.reporter_email,
                    created_date=row.created_date or datetime.now(),
                    priority=priority,
                    ml_summary=row.ml_summary,
                )
                cases.append(case)

            return cases, total_count

        except Exception as e:
            print(f"Error performing semantic search: {str(e)}")
            # Fallback to regular cases if semantic search fails
            return self.get_cases(page=page, page_size=page_size)

    def search_sightings_semantic(self, query: str, page: int = 1, page_size: int = 20) -> tuple[list[Sighting], int]:
        """Perform semantic search on sightings using embeddings and cosine similarity"""

        if not query or not query.strip():
            return self.get_sightings(page=page, page_size=page_size)

        # Calculate offset
        offset = (page - 1) * page_size

        # Generate embedding for the search query
        EMBEDDING_QUERY = """
        SELECT ml_generate_embedding_result
        FROM ML.GENERATE_EMBEDDING(
            MODEL `homeward.text_embedding_model`,
            (SELECT @query_text as content),
            STRUCT('SEMANTIC_SIMILARITY' as task_type)
        )
        """

        # Get query embedding
        try:
            embedding_job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("query_text", "STRING", query.strip())
                ]
            )
            embedding_job = self.client.query(EMBEDDING_QUERY, job_config=embedding_job_config)
            embedding_result = list(embedding_job.result())[0]
            query_embedding = embedding_result.ml_generate_embedding_result

            if not query_embedding:
                # Fallback to regular sightings if embedding generation fails
                return self.get_sightings(page=page, page_size=page_size)

        except Exception as e:
            print(f"Error generating embedding for query: {str(e)}")
            # Fallback to regular sightings if embedding generation fails
            return self.get_sightings(page=page, page_size=page_size)

        # Count query for semantic search results
        COUNT_QUERY = """
        SELECT COUNT(*) as total_count
        FROM `homeward.sightings`
        WHERE ml_summary_embedding IS NOT NULL
        AND ARRAY_LENGTH(ml_summary_embedding) > 0
        AND ml_summary IS NOT NULL
        """

        # Semantic search query with cosine similarity
        SEMANTIC_SEARCH_QUERY = """
        SELECT
            id, sighting_number, sighted_date, sighted_time, sighted_address, sighted_city,
            sighted_country, sighted_postal_code, sighted_latitude, sighted_longitude,
            apparent_gender, apparent_age_range, height_estimate, weight_estimate,
            hair_color, eye_color, clothing_description, distinguishing_features,
            description, circumstances, confidence_level, photo_url, video_url,
            source_type, witness_name, witness_phone, witness_email,
            status, priority, verified, created_date, updated_date,
            created_by, notes, ml_summary,
            ML.DISTANCE(ml_summary_embedding, @query_embedding, 'COSINE') as cosine_distance
        FROM `homeward.sightings`
        WHERE ml_summary_embedding IS NOT NULL
        AND ARRAY_LENGTH(ml_summary_embedding) > 0
        AND ml_summary IS NOT NULL
        ORDER BY cosine_distance ASC
        LIMIT @page_size OFFSET @offset
        """

        try:
            # Execute count query
            count_job = self.client.query(COUNT_QUERY)
            total_count = list(count_job.result())[0].total_count

            # Execute semantic search query
            search_job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ArrayQueryParameter("query_embedding", "FLOAT64", query_embedding),
                    bigquery.ScalarQueryParameter("page_size", "INT64", page_size),
                    bigquery.ScalarQueryParameter("offset", "INT64", offset)
                ]
            )
            search_job = self.client.query(SEMANTIC_SEARCH_QUERY, job_config=search_job_config)

            # Convert results to Sighting objects
            sightings = []
            for row in search_job.result():
                # Same conversion logic as get_sightings method
                sighted_date = row.sighted_date
                sighted_time = row.sighted_time

                if sighted_date and sighted_time:
                    from datetime import datetime, time
                    if isinstance(sighted_time, time):
                        sighted_datetime = datetime.combine(sighted_date, sighted_time)
                    else:
                        sighted_datetime = datetime.combine(sighted_date, datetime.min.time())
                else:
                    sighted_datetime = datetime.combine(sighted_date, datetime.min.time()) if sighted_date else datetime.now()

                from homeward.models.case import Location, SightingStatus, SightingPriority, SightingConfidenceLevel, SightingSourceType
                location = Location(
                    address=row.sighted_address or "",
                    city=row.sighted_city or "",
                    country=row.sighted_country or "",
                    postal_code=row.sighted_postal_code,
                    latitude=row.sighted_latitude,
                    longitude=row.sighted_longitude
                )

                status = SightingStatus.NEW
                try:
                    status = SightingStatus(row.status)
                except ValueError:
                    pass

                priority = SightingPriority.MEDIUM
                try:
                    priority = SightingPriority(row.priority)
                except ValueError:
                    pass

                confidence_level = SightingConfidenceLevel.MEDIUM
                try:
                    confidence_level = SightingConfidenceLevel(row.confidence_level)
                except ValueError:
                    pass

                source_type = SightingSourceType.WITNESS
                try:
                    source_type = SightingSourceType(row.source_type)
                except ValueError:
                    pass

                sighting = Sighting(
                    id=row.id,
                    sighting_number=row.sighting_number,
                    sighted_date=sighted_datetime,
                    sighted_location=location,
                    apparent_gender=row.apparent_gender or "",
                    height_estimate=row.height_estimate,
                    weight_estimate=row.weight_estimate,
                    hair_color=row.hair_color or "",
                    clothing_description=row.clothing_description or "",
                    distinguishing_features=row.distinguishing_features or "",
                    description=row.description or "",
                    confidence_level=confidence_level,
                    source_type=source_type,
                    created_date=row.created_date or datetime.now(),
                    ml_summary=row.ml_summary,
                    status=status,
                    priority=priority,
                    verified=row.verified or False,
                    witness_name=row.witness_name,
                    witness_phone=row.witness_phone,
                    witness_email=row.witness_email,
                    photo_url=row.photo_url,
                    video_url=row.video_url,
                    circumstances=row.circumstances,
                    notes=row.notes,
                    created_by=row.created_by,
                    apparent_age_range=row.apparent_age_range,
                    eye_color=row.eye_color
                )
                sightings.append(sighting)

            return sightings, total_count

        except Exception as e:
            print(f"Error performing semantic search on sightings: {str(e)}")
            # Fallback to regular sightings if semantic search fails
            return self.get_sightings(page=page, page_size=page_size)

    def get_video_evidence_for_case(self, case_id: str) -> list[dict]:
        """Get all video evidence linked to a specific case from the video_analytics_results table"""
        try:
            # Use the same hardcoded format as other methods in this class
            query = """
            SELECT
                var.result_id,
                var.case_id,
                var.created_date,
                var.status,
                -- Get video analysis data from the AI analysis view
                va.video_timestamp,
                va.video_camera_id,
                va.video_camera_type,
                va.video_latitude,
                va.video_longitude,
                va.video_address,
                va.distance_from_last_seen_km,
                va.video_gcs_uri,
                va.confidence_score,
                va.ai_description,
                va.ai_summary
            FROM `homeward.video_analytics_results` var
            LEFT JOIN `homeward.video_analysis_ai_view` va
                ON var.result_id = va.analysis_id
            WHERE var.case_id = @case_id
                AND var.status = 'Evidence'
            ORDER BY var.created_date DESC
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("case_id", "STRING", case_id)
                ]
            )

            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()

            video_evidence = []
            for row in results:
                evidence = {
                    "result_id": row.result_id,
                    "case_id": row.case_id,
                    "created_date": row.created_date,
                    "status": row.status,
                    "video_timestamp": row.video_timestamp,
                    "camera_id": row.video_camera_id,
                    "camera_type": row.video_camera_type,
                    "latitude": row.video_latitude,
                    "longitude": row.video_longitude,
                    "address": row.video_address,
                    "distance_km": row.distance_from_last_seen_km,
                    "video_url": row.video_gcs_uri,
                    "confidence_score": row.confidence_score,
                    "ai_description": row.ai_description,
                    "ai_summary": row.ai_summary
                }
                video_evidence.append(evidence)

            return video_evidence

        except Exception as e:
            print(f"Error getting video evidence for case {case_id}: {str(e)}")
            return []
