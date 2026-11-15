# TerraTwin Project Tools Report

**Prepared:** 15 November 2026  
**Project:** TerraTwin — Earth, Moon and Mars analog exploration

## Project overview

TerraTwin is a web application for exploring planetary bodies, viewing a 3D globe, browsing a scientific dataset catalogue and comparing selected lunar or Martian terrain with available Earth regions. The repository contains a React web client, a Python API and a separate Node.js AI assistant service.

## Main tools and technologies

| Area | Tools | Role in the project |
|---|---|---|
| Frontend | JavaScript, React 19, React DOM | Builds the interactive dashboard and manages page state. |
| Frontend development | Vite 8 | Runs the local development server and creates the production bundle. Its development proxy forwards API and health requests to FastAPI. |
| 3D visualization | Three.js | Renders textured Earth, Moon and Mars spheres with lighting, rotation and orbit controls. |
| Styling | CSS | Provides the dashboard layout, responsive behavior, visual states and interaction styling. |
| Backend API | Python, FastAPI, Pydantic | Exposes planetary, location, dataset and analysis endpoints, and validates API request data. |
| Backend server | Uvicorn | Runs the FastAPI application locally or in deployment. |
| HTTP clients | HTTPX (Python), Fetch API (browser), `fetch` (Node.js) | Connect the services to each other and to external data APIs. |
| Geospatial processing | Rasterio and NumPy | Reads raster elevation data, works with coordinate reference systems, and derives terrain statistics and regional features. |
| Similarity analysis | Python standard library (`math`, `json`, `pathlib`) | Loads prepared feature records and ranks Earth candidates using dimensionless terrain-shape features. |
| AI service | Node.js, Express 5, Google GenAI SDK | Provides the chat API and sends prompts and comparison context to the configured Gemini model. |
| Configuration and cross-origin access | `dotenv`, CORS middleware | Loads environment configuration and permits browser or service requests across configured origins. |
| Code quality and checks | ESLint, `eslint-plugin-react-hooks`, pytest | Frontend linting and backend test framework. |

## Data sources and integrations

- **NASA Earthdata CMR** supplies Earth science collection search results.
- **NASA PDS Orbital Data Explorer (ODE)** supplies Moon and Mars instrument and product information and product file metadata.
- **NASA PDS and mission products**, including LOLA, MOLA and HiRISE data, are represented in the local raster and feature cache.
- **Copernicus DEM GLO-30** provides Earth elevation data used in the terrain comparison workflow.
- The **Google Gemini API** powers the separate AI chat service. The API key is read from `GEMINI_API_KEY`; it is not included in the source report.

## How the services work together

1. The React client requests planets, locations and dataset records from the FastAPI routes under `/api`.
2. The user can submit a Moon or Mars site to `/api/analyze/compare`.
3. FastAPI loads the prepared target and Earth feature JSON files, computes terrain-shape similarity scores and returns the ranked candidates.
4. The Node.js assistant can call the same comparison endpoint, then provide those returned results as context to Gemini.

During local development, Vite proxies `/api/*` and `/health` to the Python service at `http://127.0.0.1:8000`. The AI assistant runs separately and defaults to port `5001`.

## Dependencies present but not currently central to the UI

The frontend manifest also declares Leaflet, React Leaflet, Recharts and Lucide React. They are available as project dependencies but are not imported by the current dashboard source. The backend requirements declare pandas, SQLAlchemy and `python-multipart`; the current code does not show an active database model or persistence layer, and the analysis request store is in memory.

## Setup and dependency notes

- Install frontend dependencies from `frontend/package.json` using `npm install`.
- Install Python dependencies from `backend/requirements.txt` using `python -m pip install -r requirements.txt`.
- The geospatial services import **Rasterio**, but Rasterio is not currently listed in `backend/requirements.txt`. Add or install a compatible Rasterio build in environments that need to run raster processing.
- The Gemini service requires a valid `GEMINI_API_KEY` in the AI assistant environment.
- Earth analog comparison is limited to the locations and Earth candidate regions represented by the checked-in feature data. The similarity service itself describes these scores as preliminary.

## Source references

- `frontend/package.json`
- `frontend/vite.config.js`
- `frontend/src/pages/PlanetShowcase.jsx`
- `frontend/src/components/Planet3D.jsx`
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/routes/`
- `backend/app/services/nasa_service.py`
- `backend/app/services/gis_feature_service.py`
- `backend/app/services/similarity_service.py`
- `ai-assistant/package.json`
- `ai-assistant/src/server.js`
- `ai-assistant/src/config/gemini.js`
