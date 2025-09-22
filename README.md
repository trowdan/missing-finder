# Homeward: AI-Powered missing persons finder

**🥽 This repo contains my submission for the [BigQuery AI Hackathon](https://www.kaggle.com/competitions/bigquery-ai-hackathon)**

![Homeward Logo](docs/img/homeward_logo.png)

## Overview

**Homeward** is an innovative missing persons finder application that leverages the power of Google Cloud Platform's AI capabilities to help law enforcement agencies locate missing individuals through video surveillance analysis and semantic matching between case reports and sightings.

The primary goals and objectives of the Homeward application are:

* **Accelerate search operations**: Significantly reduce the time required to find a missing person by automating the analysis of video footage and the matching of case reports and sightings.
* **Improve investigation accuracy**: Leverage AI to identify potential sightings and connections that might be missed by human operators.
* **Centralize case information**: Provide a single, unified platform for registering missing persons, logging sightings, and managing all related case data.

The primary users of this application are:

* **Law enforcement officers**: Police officers and detectives directly responsible for investigating missing person cases.
* **Government agency personnel**: Staff from national or regional centers for missing persons who are involved in the coordination and management of these cases.

## 🎯 Hackathon Highlights

This submission showcases several innovative features of BigQuery:

1. **Object tables for Video processing**: Utilizing BigQuery's object tables to create external references to video files in Cloud Storage
2. **Multimodal data analysis**: Analyzing video content through Gemini models for person detection and matching with just SQL.
3. **Object table metadata enrichment and filtering**: Using object metadata to filter-out unwanted files (time-filtering and geo-filtering) and let Gemini analyze only the needed files.
4. **Semantic matching**: Leveraging Gemini summarizations, embeddings and vector similarity to match cases with sightings.
5. **Semantic search**: Natural language queries for finding specific missing cases.

## 🏗️ Architecture
![Google Cloud Architecture](./docs/img/architecture.png "Google Cloud Architecture")

### Technology Stack

- **Frontend/Backend**: Python with NiceGUI framework
- **Database**: Google BigQuery
- **Object Storage**: Google Cloud Storage
- **AI/ML**: Google Gemini multimodal models and Vertex AI embedding models

### Data Model

The application consists of the following core tables:

- **`missing_persons`**: Central registry of missing person cases with demographics, descriptions, and case metadata
- **`sightings`**: Individual sighting reports from various sources (manual reports, AI analysis)
- **`case_sightings`**: Junction table linking sightings to specific missing person cases
- **`video_objects`**: External table referencing video files in Cloud Storage with metadata
- **`video_analytics_results`**: AI analysis results from Gemini model processing

If you want to know more the `sql` folder contains the DDL and DML of the application.

### Data Flow - Case Registration

1. **Case intake**: Law enforcement officers input missing person details through the NiceGUI interface
2. **Location geocoding**: Addresses are geocoded using Google's Geocoding API
3. **AI Summarization**: Gemini 2.5 Flash generates standardized summaries of the missing person
4. **Embedding generation**: Text embedding models (text-embedding-004) create vector representations of case descriptions
5. **Storage**: Case data, embeddings, and metadata are stored in the `missing_persons` table

### Data Flow - Sighting Registration

1. **Manual sighting input**: Officers or citizens report potential sightings through the application interface
2. **Location geocoding**: Addresses are geocoded using Google's Geocoding API
3. **AI Summarization**: Sighting descriptions are summarized using Gemini 2.5 Flash
4. **Embedding creation**: Vector embeddings are generated for semantic similarity matching
5. **Storage**: Sightings are stored in BigQuery

### Data Flow - Video Intelligence

1. **Video Ingestion**: Surveillance videos are uploaded to Cloud Storage using the naming convention: `CameraID_YYYYMMDDHHMMSS_LATITUDE_LONGITUDE_CAMERATYPE_RESOLUTION.mp4`
2. **Metadata Extraction**: BigQuery object tables automatically detect filename metadata (timestamp, location, camera details)
3. **Geographic Filtering**: Native BigQuery geocoding functions like `ST_GEOGPOINT` and `ST_DWITHIN` are used to filter videos by proximity to case locations
4. **Temporal Filtering**: Time-based filtering selects relevant video footage based on case timelines
5. **AI Analysis**: Gemini 2.5 Pro models analyze video content using missing person descriptions as prompts
6. **Result Processing**: Analysis results are structured and stored in `video_analytics_results` with confidence scores
7. **Sighting Generation**: High-confidence matches automatically create sighting records

### Data Flow - Semantic Matching

1. **Vector Similarity**: Text embeddings from missing person cases are compared against sighting embeddings using cosine similarity
2. **Threshold Filtering**: Matches above configurable similarity thresholds are identified as potential links
3. **Contextual Analysis**: Gemini models provide additional context and reasoning for potential matches
4. **Confidence Scoring**: Multi-factor confidence scores incorporate semantic similarity, temporal proximity, and geographic correlation
5. **Link Creation**: Validated matches create entries in the `case_sightings` junction table

### Data Flow - Semantic Search

1. **User input**: The user type natural language query in the search bar of the NiceGUI UI
2. **Query Processing**: Natural language search queries are converted to embeddings using the same text-embedding-004 model
3. **Vector Search**: BigQuery performs similarity searches against stored case and sighting embeddings
4. **Result Ranking**: Results are ranked by semantic similarity and filtered by relevance thresholds
5. **Context Enhancement**: Gemini models enrich search results with explanatory context and highlights

### BigQuery data integration points

#### Object Tables Configuration
```sql
CREATE EXTERNAL TABLE `{project}.{dataset}.video_objects`
OPTIONS (
  object_metadata = 'SIMPLE',
  max_staleness = INTERVAL 1 HOUR,
  metadata_cache_mode = 'AUTOMATIC'
);
```

#### Spatial Operations
- **Geocoding**: Geocoding APIs from Google Maps are used to retrieve coordinates starting from an address in a case or a sighting
- **ST_GEOGPOINT()**: Convert latitude/longitude from video filenames to geographic points within BigQuery
- **ST_DWITHIN()**: Proximity-based filtering for relevant surveillance footage within BigQuery

## 🚀 Quick Start

### Prerequisites

- Google Cloud Platform account with billing enabled
- `gcloud` CLI installed and authenticated
- Python 3.8+ with `uv` package manager
- Access to the following GCP APIs:
  - BigQuery API
  - Cloud Storage API
  - Vertex AI API
  - Geocoding API

### Project setup
This repository includes two versions of the same use case:
- A Jupyter notebook with a light version of the use case (same functionalities and BQ queries)
- A web application with a UI interface to interact with BigQuery (suggested if you want to see all the capabilities of the solution)

Depending of the version you want to try, you can follow the following instructions for the setup:

### Project Setup - 📊 Notebook
---

Open the `demo-notebook.ipynb` file with your preferred Jupyter notebook editor or run the following command:

```bash
jupyter notebook demo-notebook.ipynb
```

The notebook contains the code for:
- Setting up BigQuery object tables for video files
- Creating Gemini model connections
- Running multimodal AI queries on video content
- Processing results and extracting insights

### Project Setup - 💻 Web Application
---

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd missing-finder
   ```

2. **Run the setup script:**
   ```bash
   ./setup.sh --project-id your-project-id --region us-central1
   ```

   **Optional: Include demo data**
   ```bash
   ./setup.sh --project-id your-project-id --region us-central1 --demo-folder ./demo
   ```

   The setup script will:
   - Create necessary GCP resources (storage buckets, BigQuery datasets, connections)
   - Configure IAM permissions
   - Set up Gemini AI model endpoints
   - Populate demo data if specified

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

4. **Run the application:**
   ```bash
   uv run --env-file=.env python src/homeward/main.py
   ```

   The application will be available at `http://localhost:8080`

## 🎮 Core Features

### Missing Person Case Management
- **Comprehensive Forms**: Detailed missing person registration with photos and metadata
- **Case Timeline**: Track all sightings and analysis results
- **CRUD Operations**: Full case management capabilities

### AI-Powered Video Analysis
- **Geographic Filtering**: Select cameras by location and search radius
- **Temporal Filtering**: Analyze videos within specific time ranges
- **Semantic Matching**: Natural language descriptions for person identification
- **Confidence Scoring**: AI-generated confidence levels for potential matches

### Sighting Management
- **Manual Registration**: Allow manual sighting reports from various sources
- **Automatic Linking**: Connect AI-detected sightings to existing cases
- **Timeline Integration**: Visualize sightings on case timelines

### Interactive Dashboard
- **KPI Cards**: Real-time statistics on cases, sightings, and analysis results
- **Interactive Maps**: Visualize camera locations and sighting patterns
- **Result Management**: Review and confirm AI-generated matches

## 📁 Project Structure

```
homeward/
├── src/homeward/           # Main application code
│   ├── ui/                 # NiceGUI user interface components
│   ├── services/           # Business logic and data services
│   ├── models/             # Data models and schemas
│   └── main.py             # Application entry point
├── demo/                   # Demo data and examples
│   ├── videos/             # Sample surveillance footage
│   └── reports/            # Sample case and sighting data
├── sql/                    # Database schemas and migrations
├── setup.sh                # Automated GCP setup script
├── demo-notebook.ipynb     # Interactive BigQuery + Gemini demo
├── limitations.ipynb       # Known limitations and workarounds
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

The application uses the following environment variables (see `.env.example`):

```bash
# Application Configuration
HOMEWARD_VERSION=0.1.0
HOMEWARD_DATA_SOURCE=bigquery  # or "mock" for development

# BigQuery Configuration
HOMEWARD_BIGQUERY_PROJECT_ID=your-project-id
HOMEWARD_BIGQUERY_DATASET=homeward

# Google Cloud Storage
HOMEWARD_VIDEO_BUCKET=your-video-bucket
HOMEWARD_GCS_BUCKET_INGESTION=your-ingestion-bucket
HOMEWARD_GCS_BUCKET_PROCESSED=your-processed-bucket

# BigQuery AI Configuration
HOMEWARD_BQ_CONNECTION=homeward_gcp_connection
HOMEWARD_BQ_TABLE=video_objects
HOMEWARD_BQ_MODEL=gemini_2_5_pro

# API Keys
HOMEWARD_GEOCODING_API_KEY=your-geocoding-api-key

# Service Account
HOMEWARD_SERVICE_ACCOUNT_KEY_PATH=downloads/key.json
```

### Setup Script Parameters

The `setup.sh` script accepts the following parameters:

- `--project-id`: Google Cloud Project ID (required)
- `--region`: Google Cloud region (required, e.g., `us-central1`)
- `--demo-folder`: Path to demo data folder (optional)


## ⚠️ Known Limitations

Based on our development experience, I've experienced the following limitations with BigQuery + Gemini:

### 1. Manual Cache Refresh Issues
- **Problem**: Manual cache refresh for object tables doesn't work as expected
- **Impact**: May require waiting for automatic cache refresh cycles
- **Workaround**: Use automatic cache refresh with appropriate `max_staleness` settings

### 2. ML.GENERATE_TEXT with Object Tables
- **Problem**: Direct use of `ML.GENERATE_TEXT` with object tables encounters issues with both global and regional endpoints
- **Impact**: Limits direct video analysis capabilities
- **Current Status**: Under investigation, may require alternative approaches

### 3. Object Table as Standard Table Treatment
- **Problem**: Treating object tables as standard tables in `ML.GENERATE_TEXT` queries fails
- **Impact**: Requires specific handling for video content analysis
- **Workaround**: Use object table-specific functions and configurations

For detailed technical information about these limitations, see `limitations.ipynb`.

## 🤝 Contributing

This project was developed as a submission for the BigQuery AI Hackathon. While the core functionality demonstrates the integration possibilities, there are several areas for future enhancement:

1. **Advanced Video Analytics**: Implement more sophisticated video processing algorithms
2. **Real-time Processing**: Add streaming capabilities for live video analysis
3. **Machine Learning Pipeline**: Develop custom ML models for person identification
4. **Mobile Application**: Create companion mobile app for field officers
5. **Integration APIs**: Develop REST APIs for integration with existing law enforcement systems

## 📄 License

This project is developed as a proof-of-concept for the BigQuery AI Hackathon. Please see individual component licenses for third-party dependencies.

---

**Built with ❤️ for the [BigQuery AI Hackathon](https://www.kaggle.com/competitions/bigquery-ai-hackathon)**

For questions or support, please raise an issue in the project repository.