# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Homeward** is a missing persons finder application designed for law enforcement agencies. It leverages Google Cloud Platform services, AI/LLM capabilities (specifically Google's Gemini), and BigQuery to analyze video surveillance footage and photographs to locate missing individuals.

## Architecture

The system uses a **serverless, event-driven architecture** on Google Cloud Platform:

### Core Components
- **Video Ingestion**: GCS bucket (`[Project-ID]-video-ingestion`) with strict naming convention for uploads
- **Event Processing**: Google Eventarc triggers Cloud Functions for video processing
- **Data Warehousing**: BigQuery with external tables referencing processed video files
- **AI Analysis**: Google Gemini multimodal models for video content analysis
- **Application Layer**: Python application built with NiceGUI library

### Data Flow
1. Videos uploaded to ingestion bucket with naming convention: `CameraID_YYYYMMDDHHMMSS_LATITUDE_LONGITUDE_CAMERATYPE_RESOLUTION.mp4`
2. Eventarc triggers Cloud Function for metadata enrichment
3. Processed videos moved to `[Project-ID]-video-processed` bucket
4. BigQuery external table references processed videos
5. Application queries BigQuery and sends analysis requests to Gemini

## Key Features

### Missing Person Case Management
- Register new missing person cases with comprehensive forms
- CRUD operations on case files stored in BigQuery
- Photo uploads and metadata management

### Sighting Management
- Manual sighting registration and linking to cases
- Automatic sighting generation from AI analysis results

### AI-Powered Video Analysis
- Geographic and temporal filtering of surveillance footage
- Gemini-based person detection and matching
- Confidence scoring and result management

### Match Sightings
- Link unassociated sightings to existing cases
- Semantic matching and timeline integration

## Technology Stack

- **Backend**: Python with NiceGUI framework
- **Cloud Platform**: Google Cloud Platform
- **Database**: Google BigQuery
- **Storage**: Google Cloud Storage
- **AI/ML**: Google Gemini multimodal models
- **Event Processing**: Google Eventarc and Cloud Functions

## Demo Structure

The `demo/` directory contains sample data:
- `reports/missings/` - Sample missing person reports
- `reports/sightings/` - Sample sighting reports  
- `videos/` - Sample surveillance footage

## Development Notes

This appears to be a proof-of-concept or demonstration project for a BigQuery hackathon, focusing on AI-powered video analysis for missing person cases. The repository currently contains primarily documentation and demo structure rather than implementation code.

## Best practices
- Run all the tests everytime you modify the code.
- Every time tests are working add a Git Commit.
- Commit message must start with the commit type. [FEAT], [FIX], [STYLE], etc.
- Be sure to be compliant with Ruff linter.