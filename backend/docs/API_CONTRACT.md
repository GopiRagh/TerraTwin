
# TerraTwin API Integration Contract

## 1. Purpose

This document defines how the TerraTwin backend will communicate with the GIS and Similarity modules.

The final data fields will be confirmed after Member 2 and Member 3 complete their modules.

## 2. Communication Format

- Communication format: JSON
- Backend framework: FastAPI
- Communication type: REST API
- Data exchange: HTTP requests and responses

## 3. Module Responsibilities

### Member 2 – GIS Module

Expected responsibility:
- Process planetary geographic data.
- Identify and prepare location information.
- Return GIS processing output in JSON format.

Final JSON structure: Pending confirmation.

### Member 3 – Similarity Module

Expected responsibility:
- Compare planetary environments.
- Calculate similarity values using the agreed algorithm.
- Return ranked results in JSON format.

Final JSON structure: Pending confirmation.

### Member 4 – Backend Module

Responsibilities:
- Receive API requests.
- Validate input data.
- Manage analysis requests.
- Connect GIS and similarity modules.
- Return structured API responses.
- Handle errors.

## 4. Integration Workflow

1. Client submits an analysis request.
2. Backend validates the request.
3. Backend sends the required data to the GIS module.
4. GIS module returns its processed output.
5. Backend passes the agreed input to the similarity module.
6. Similarity module returns comparison results.
7. Backend prepares the final response.
8. Client receives the response.

## 5. Error Handling

Expected HTTP status codes:

- 200 – Successful request
- 400 – Invalid request
- 404 – Resource not found
- 422 – Input validation error
- 500 – Internal server error

## 6. Pending Decisions

- GIS JSON output structure.
- Similarity algorithm input structure.
- Similarity algorithm output structure.
- Coordinate reference system and units.
- Integration function names.
- Final analysis response structure.

These details will be finalized through coordination with Members 2 and 3.

## 7. Current Status

Draft prepared by Member 4.

Actual module integration is pending completion and agreement on data formats.
