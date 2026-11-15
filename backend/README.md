
# TerraTwin Backend API

## 1. Project Overview

TerraTwin is an Earth Analog Discovery Platform.

The backend provides REST APIs for:
- Retrieving planetary information.
- Retrieving planetary location information.
- Creating analysis requests.
- Tracking analysis request status.
- Retrieving analysis request details.

The backend is developed using Python and FastAPI.

## 2. Technologies Used

- Python 3
- FastAPI
- Uvicorn
- Pydantic
- JSON
- HTTP REST APIs

## 3. Backend Folder Structure

```text
backend/
├── app/
│   ├── main.py
│   ├── routes/
│   │   ├── planets.py
│   │   ├── locations.py
│   │   └── analysis.py
│   └── services/
│       └── analysis_service.py
├── tests/
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## 4. Installation and Setup

### Step 1: Open the backend directory

```bash
cd backend
```

### Step 2: Activate the virtual environment

Windows CMD:

```cmd
venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Start the backend server

```bash
python -m uvicorn app.main:app --reload
```

Backend URL:

http://127.0.0.1:8000


### A. Home API

Method: GET

Endpoint:
`/`

Purpose: Checks whether the TerraTwin backend is running.

Sample response:

```json
{
  "status": "success",
  "message": "TerraTwin backend is running",
  "data": {
    "project": "TerraTwin",
    "service": "Backend API",
    "version": "1.0.0"
  }
}
```


## 6. Available API Endpoints

### A. Home API

Method: GET

Endpoint:

```text
/
```

Purpose: Checks whether the backend is running.


### B. Health Check API

Method: GET

Endpoint:
`/health`

Purpose: Checks the health of the backend service.

Sample response:

```json
{
  "status": "success",
  "message": "Backend service is healthy",
  "data": {
    "service": "TerraTwin Backend",
    "health": "healthy"
  }
}
```


Purpose: Checks backend service health.


### C. Planet APIs

**Get all planets**

Method: GET

Endpoint:

`/api/planets/`

Purpose: Retrieves all available planetary bodies.

Sample response:

```json
{
  "status": "success",
  "message": "Planetary bodies retrieved successfully",
  "total": 3,
  "data": [
    {
      "id": "earth",
      "name": "Earth",
      "type": "Planet",
      "description": "Our home planet",
      "role": "Earth analog search destination"
    }
  ]
}
```

**Get a planet by ID**

Method: GET

Endpoint:

`/api/planets/{planet_id}`

Purpose: Retrieves information about a specific planetary body.

Supported sample IDs:
- earth
- moon
- mars

Successful response includes:
- status
- message
- data



### D. Location APIs

**Get all locations**

Method: GET

Endpoint:

`/api/locations/`

Purpose: Retrieves all available planetary locations.

**Get location by ID**

Method: GET

Endpoint:

`/api/locations/{location_id}`

Purpose: Retrieves a specific location using its unique ID.

**Get locations by planet**

Method: GET

Endpoint:

`/api/locations/planet/{planet_name}`

Purpose: Retrieves locations belonging to a particular planet.

Current sample locations:

| Location ID | Planet | Location |
|---|---|---|
| mars_001 | Mars | Jezero Crater |
| moon_001 | Moon | Shackleton Crater |
| earth_001 | Earth | Atacama Desert |

Successful response format:

```json
{
  "status": "success",
  "message": "Locations retrieved successfully",
  "total": 3,
  "data": []
}
```

Note: The current location records are sample data.


### E. Analysis APIs

**Create an analysis request**

Method: POST

Endpoint:

`/api/analyze/`

Purpose: Creates a new analysis request for a supported target planet and location.

Sample JSON request:

```json
{
  "target_planet": "mars",
  "target_location": "Jezero Crater"
}
```

Sample successful response:

```json
{
  "status": "accepted",
  "message": "Analysis request created successfully",
  "data": {
    "analysis_id": "generated-unique-id",
    "target_planet": "mars",
    "target_location": "Jezero Crater",
    "status": "pending",
    "results": [],
    "created_at": "timestamp"
  }
}
```

**Get all analysis requests**

Method: GET

Endpoint:

`/api/analyze/`

Purpose: Retrieves all previously created analysis requests.

**Get analysis request by ID**

Method: GET

Endpoint:

`/api/analyze/{analysis_id}`

Purpose: Retrieves an individual analysis request using its unique ID.

### Analysis Validation Rules

- Target planet must be Moon or Mars.
- Target location must contain at least 2 characters.
- Target location cannot exceed 150 characters.

### Analysis Workflow

1. Client submits an analysis request.
2. Backend validates the request.
3. Backend generates a unique analysis ID.
4. Request details are stored temporarily.
5. Backend returns the request ID and pending status.
6. Client can retrieve the request using its ID.

The `/api/analyze/` route creates a pending request. The `/api/analyze/compare` route runs the available terrain-shape comparison synchronously and stores the completed result in temporary in-memory storage.



## 7. Analysis Request Workflow

1. Client sends an analysis request.
2. Backend validates the input.
3. Backend generates a unique analysis ID.
4. Request details are stored temporarily.
5. Backend returns the analysis ID and pending status.
6. Client can retrieve the request using its analysis ID.

Example response:

```json
{
  "status": "accepted",
  "message": "Analysis request created successfully",
  "data": {
    "analysis_id": "generated-unique-id",
    "target_planet": "mars",
    "target_location": "Jezero Crater",
    "status": "pending",
    "results": [],
    "created_at": "timestamp"
  }
}
```

## 8. Input Validation and Error Handling

The backend validates incoming analysis requests.

Current validation rules:
- Target planet must be Moon or Mars.
- Target location must contain at least 2 characters.
- Target location cannot exceed 150 characters.

Common HTTP response codes:

| Code | Meaning |
|------|---------|
| 200 | Successful request |
| 404 | Resource not found |
| 422 | Input validation error |


## 9. Current Implementation Status

### Completed

- FastAPI backend setup.
- Planet APIs.
- Location APIs using sample data.
- Analysis request creation and retrieval.
- Input validation and error handling.
- Standardized JSON response structures.
- Backend request and error logging.
- API documentation.
- Terrain-shape analog ranking backed by cached Moon, Mars and Earth feature files.
- Earth candidate inventory endpoint at `/api/analyze/earth-candidates`.
- 16 automated tests passing.

### Current Limitations

- Location API records are sample data.
- Analysis requests use temporary in-memory storage and are cleared when the process restarts.
- Similarity scores use a prototype comparison of dimensionless elevation-shape features. They are preliminary and do not account for every environmental property.
- Six cached Earth regions are currently ranked: Atacama Desert, Salar de Atacama, Bioko Island, Pico Basilé, Moka Highlands and Gran Caldera de Luba. Rankings are not a global analog survey.
- NASA catalogue requests depend on external NASA services being reachable.


## 10. Team Integration

The backend uses JSON request and response formats.

Other project modules can communicate with the backend through REST API endpoints.

The GIS feature services, similarity ranking and AI assistant communicate through JSON and HTTP interfaces.

## 11. Developer

Project: TerraTwin

Module: Backend and API Development

Framework: FastAPI


## 12. Logging and Monitoring

The backend includes a logging system to monitor application activity.

Features:
- Backend startup logging.
- API request logging.
- HTTP response status logging.
- Request processing time logging.
- Unexpected exception logging.

Log file location:

backend/logs/terratwin.log

The logging system helps developers monitor API activity and identify errors during development.
