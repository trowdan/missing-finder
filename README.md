
# Homeward: Missing persons finder

## 1. Introduction

### 1.1. Project Overview

The **"Homeward"** is a specialized software application designed to assist law enforcement agencies and governmental bodies in the critical task of locating missing individuals. This system leverages Artificial Intelligence (AI), specifically Large Language Models (LLMs) like Google's Gemini, to analyze vast amounts of unstructured data such as video surveillance footage and photographs. By integrating with **Google BigQuery** AI capabilities, the solution aims to accelerate the search process, improve accuracy, and enhance collaboration among the different entities involved in a missing person case.

### 1.2. Goals and Objectives

The primary goals and objectives of the Homeward application are:

* **Accelerate Search Operations**: Significantly reduce the time required to find a missing person by automating the analysis of video footage and other data sources.
* **Improve Investigation Accuracy**: Leverage AI to identify potential sightings and connections that might be missed by human operators.
* **Centralize Case Information**: Provide a single, unified platform for registering missing persons, logging sightings, and managing all related case data.
* **Enhance Collaboration**: Facilitate seamless information sharing and coordinated efforts among different police departments and government agencies.
* **Provide Actionable Intelligence**: Offer data-driven suggestions, such as optimal search radii based on last known locations and sighting patterns, to guide investigation efforts.

### 1.3. Target Audience

The primary users of this application are:

* **Law Enforcement Officers**: Police officers and detectives directly responsible for investigating missing person cases.
* **Government Agency Personnel**: Staff from national or regional centers for missing persons who are involved in the coordination and management of these cases.
* **Data Analysts**: Specialists who support investigations by analyzing system-generated data and the insights produced by the AI models.

---

## 2. System Architecture and Data Flow

The system is built upon a **serverless, event-driven architecture** on the Google Cloud Platform (GCP), designed for scalability and the efficient processing of large video files. The data flows through the following distinct stages:

### 2.1. Video Ingestion and Enrichment

1.  **Upload to Ingestion Bucket**: Video files are uploaded to a dedicated Google Cloud Storage (GCS) bucket named `[Project-ID]-video-ingestion`.
    * **Strict Naming Convention**: File uploads must adhere to the following naming convention to provide initial metadata: `CameraID_YYYYMMDDHHMMSS_LATITUDE_LONGITUDE_CAMERATYPE_RESOLUTION.mp4`.
2.  **Event-Driven Trigger**: Google Eventarc is configured to monitor the ingestion bucket. When a new video is successfully uploaded, Eventarc triggers a Cloud Function to begin processing.
3.  **Metadata Enrichment (Cloud Function)**: A Python-based Cloud Function is executed to enrich the file's metadata.
    * The function parses the filename to extract the `CameraID`, `Timestamp`, and other static details.
    * It adds a comprehensive set of metadata to the video file object, including:
        * `gps_coordinates` (Latitude, Longitude)
        * `camera_type` (e.g., Fixed, PTZ, Dome)
        * `camera_address` (e.g., "Via Roma 10, Milan, Italy")
        * `video_resolution` (e.g., "1920x1080")
    * Finally, the function moves the enriched video file to a separate, processed GCS bucket: `[Project-ID]-video-processed`.

### 2.2. Data Warehousing with BigQuery

The processed GCS bucket serves as a direct data source for Google BigQuery.

* An **external table** is created in a BigQuery dataset. This table directly references the video files located in the `[Project-ID]-video-processed` GCS bucket.
* The table schema is designed to include columns for all the enriched metadata, along with a URI that points to the specific video file in GCS.

### 2.3. AI-Powered Analysis with Gemini

The core video analysis is performed using Google's powerful multimodal models (Gemini).

* When a user initiates a search from the application, the backend constructs a detailed query for the model.
* This query includes the URIs of the relevant video files (selected from the BigQuery external table based on location and time) and a detailed text prompt derived from the missing person's case file (e.g., "Find a person matching this description: male, approximately 180cm tall, wearing a red jacket and blue jeans").
* The Gemini model processes the video(s) against the text prompt and returns potential matches, including precise timestamps and confidence scores for each sighting.

### 2.4. Application Layer

The **Homeward application**, built with Python and the NiceGUI library, serves as the primary user interface. It connects securely to Google BigQuery to perform the following actions:

* Perform full **CRUD (Create, Read, Update, Delete)** operations on case and sighting information.
* Query the video external table to populate the map interface with camera locations and to filter videos for analysis.
* Receive and display the analysis results generated by the AI model in a user-friendly format.

---

## 3. Core Functionalities

### 3.1. Missing Person Case Management

#### 3.1.1. Register New Missing Person

This module allows users to create a new case file for a missing individual through a comprehensive form.

* **View: New Missing Person Form**
    * **Personal Details Section**:
        * `Name`: Text Field, **Mandatory**.
        * `Surname`: Text Field, **Mandatory**.
        * `Date of Birth`: Date Picker, **Mandatory**.
        * `Gender`: Dropdown (Options: Male, Female, Other), **Mandatory**.
        * `Height (cm)`: Numeric Field.
        * `Weight (kg)`: Numeric Field.
        * `Distinguishing Features`: Text Area (for details like scars, tattoos, glasses).
    * **Photographs Section**:
        * `Photo Upload`: File Uploader that allows multiple images (formats: JPEG, PNG). At least one clear, recent photo is **Mandatory**. The system should allow for tagging photos (e.g., "Most Recent," "Side Profile").
    * **Last Sighting Information Section**:
        * `Date of Last Sighting`: Date and Time Picker, **Mandatory**.
        * `Location of Last Sighting`: Text Field with map integration (e.g., Google Maps API) to pinpoint coordinates, **Mandatory**.
        * `Description of Clothing`: Text Area, **Mandatory**.
        * `Circumstances of Disappearance`: Text Area, providing context for the disappearance.
    * **Contact Information Section**:
        * `Reporting Person's Name`: Text Field.
        * `Reporting Person's Contact`: Text Field (for Phone/Email).
* **Actions**:
    * `Save Case` Button: Validates the form and saves the information to the appropriate BigQuery table. On success, the user is redirected to the Case Dashboard.
    * `Cancel` Button: Discards all input and returns the user to the main dashboard.

#### 3.1.2. View/Edit Existing Case

Users can access and modify the details of an existing missing person case.

* **View: Case Details Page**
    * Displays all information entered during registration in a read-only format.
    * An **`Edit`** button allows authorized users to modify the case details, which opens the same form as in the registration process, pre-filled with the existing data.
    * Includes a timeline view of all associated sightings and system-generated alerts.

### 3.2. Sighting Management

#### 3.2.1. Register New Sighting

This feature allows users to manually log a potential sighting of a missing person, which can then be linked to an existing case.

* **View: New Sighting Form**
    * `Date and Time of Sighting`: Date and Time Picker, **Mandatory**.
    * `Location of Sighting`: Text Field with map integration, **Mandatory**.
    * `Description of Sighting`: Text Area for a detailed description of the person seen, their clothing, and behavior.
    * `Source of Information`: Text Field (e.g., "Citizen report," "CCTV footage").
    * `Upload Media`: File Uploader for photos or short video clips related to the sighting.
* **Actions**:
    * `Save Sighting` Button: Saves the sighting information to BigQuery.
    * `Link to Missing Person Case`: A search/dropdown field to associate this sighting with an existing missing person record.

### 3.3. AI-Powered Video Analysis

This is the core intelligent feature of the system. Once a case is created, the system can automatically or manually trigger an analysis of video feeds from registered cameras.

* **View: Video Analysis Dashboard**
    * **Analysis Configuration Section**:
        * `Select Missing Person`: Dropdown menu to choose the case to analyze.
        * `Timeframe for Analysis`: Date/Time Range Picker (with options like "Last 24 hours" or a "Custom Range").
        * `Geographic Area`: An interactive map displaying registered camera locations. The system will automatically suggest a search radius based on the last sighting location, which the user can manually adjust by drawing a circle or polygon on the map.
    * **Analysis Parameters (derived from case file)**:
        * The system will automatically use the missing person's description (height, clothing, features) to create a detailed search query for the LLM.
* **Actions**:
    * `Start Analysis` Button: Initiates the backend process to query BigQuery for relevant video URIs and sends the analysis request to the Gemini model.
* **Results Section**:
    * A list or gallery of potential matches will be displayed. Each result will include:
        * A thumbnail/snapshot from the video.
        * Camera ID/Location.
        * Timestamp of the potential sighting.
        * **Confidence Score (%)**: An AI-generated score indicating the likelihood of a match.
    * Users can click on a result to view the video clip and either **confirm** or **dismiss** the match. Confirmed matches will automatically generate a new sighting record and link it to the case.

### 3.4. Match Sightings

This functionality allows users to review and link unassociated sightings to existing missing person cases.

* **View: Match Sightings Page**
    * **Layout**: A single-panel interface that displays a list of unassigned sightings, showing key details like Date, Location, a Brief Description, and any associated media.
* **Workflow**:
    1.  The system automatically searches for and suggests relevant missing person cases based on the similarity of descriptions between the unassigned sighting and the case files.
    2.  The user reviews the suggested matches and selects the most appropriate case.
    3.  A **`Link`** button confirms the association between the sighting and the selected case.
    4.  The system then semantically links the two records, officially adding the sighting to the case's historical timeline.