# BigQuery Implementation Plan - Homepage Focus

## Overview

The Homeward application currently shows "NotImplementedError: BigQuery implementation not yet available" on the homepage. This document provides a focused plan to implement the three missing BigQuery methods required for homepage functionality with pagination support.

## Homepage Requirements Analysis

### Missing Implementations (Homepage Critical)

#### 1. `get_cases()` - Line 20 in `bigquery_data_service.py`
**Purpose:** Display missing person cases table on homepage dashboard
**Return:** `list[MissingPersonCase]` with optional status filtering

#### 2. `get_kpi_data()` - Line 25 in `bigquery_data_service.py`
**Purpose:** Display KPI statistics on homepage dashboard
**Return:** `KPIData` object with dashboard metrics

#### 3. `get_sightings()` - Line 531 in `bigquery_data_service.py`
**Purpose:** Display sightings table on homepage dashboard
**Return:** `list[Sighting]` with optional status filtering

## Implementation Plan

### Phase 1: Update Method Signatures for Pagination

```python
# Update abstract base class in src/homeward/services/data_service.py
@abstractmethod
def get_cases(self, status_filter: Optional[str] = None, page: int = 1, page_size: int = 20) -> tuple[list[MissingPersonCase], int]:
    """Get missing person cases with pagination. Returns (cases, total_count)"""
    pass

@abstractmethod
def get_sightings(self, status_filter: Optional[str] = None, page: int = 1, page_size: int = 20) -> tuple[list[Sighting], int]:
    """Get sighting reports with pagination. Returns (sightings, total_count)"""
    pass
```

### Phase 2: Implement `get_cases()` with Pagination

```python
def get_cases(self, status_filter: Optional[str] = None, page: int = 1, page_size: int = 20) -> tuple[list[MissingPersonCase], int]:
    """Get missing person cases from BigQuery with pagination"""

    # Calculate offset
    offset = (page - 1) * page_size

    # Count query
    COUNT_QUERY = """
    SELECT COUNT(*) as total_count
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
        # [Implementation follows same pattern as existing get_case_by_id method]
        # Create Location, parse enums, handle dates, etc.
        case = MissingPersonCase(...)
        cases.append(case)

    return cases, total_count
```

### Phase 3: Implement `get_kpi_data()`

```python
def get_kpi_data(self) -> KPIData:
    """Get KPI dashboard data from BigQuery"""

    KPI_QUERY = """
    WITH case_stats AS (
      SELECT
        COUNT(*) as total_cases,
        COUNTIF(status = 'Active') as active_cases,
        COUNTIF(status = 'Resolved') as resolved_cases,
        AVG(CASE
          WHEN status = 'Resolved'
          THEN DATE_DIFF(updated_date, created_date, DAY)
          END) as avg_resolution_days,
        SAFE_DIVIDE(COUNTIF(status = 'Resolved'), COUNT(*)) * 100 as success_rate
      FROM `homeward.missing_persons`
    ),
    sighting_stats AS (
      SELECT COUNT(*) as sightings_today
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
```

### Phase 4: Implement `get_sightings()` with Pagination

```python
def get_sightings(self, status_filter: Optional[str] = None, page: int = 1, page_size: int = 20) -> tuple[list[Sighting], int]:
    """Get sighting reports from BigQuery with pagination"""

    # Calculate offset
    offset = (page - 1) * page_size

    # Count query
    COUNT_QUERY = """
    SELECT COUNT(*) as total_count
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
        # [Implementation follows same pattern as existing get_sighting_by_id method]
        # Create Location, parse enums, handle dates, etc.
        sighting = Sighting(...)
        sightings.append(sighting)

    return sightings, total_count
```

### Phase 5: Update Homepage UI for Pagination

Update calls in dashboard page to handle pagination:

```python
# Update homepage service calls
cases, total_cases = data_service.get_cases(page=1, page_size=10)
sightings, total_sightings = data_service.get_sightings(page=1, page_size=10)
kpi_data = data_service.get_kpi_data()
```

## Database Requirements

### Required Tables (Must Exist)
1. **`homeward.missing_persons`** - Already referenced in working methods
2. **`homeward.sightings`** - Already referenced in working methods

