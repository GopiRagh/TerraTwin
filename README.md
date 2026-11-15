# TerraTwin

Earth–Moon–Mars analog exploration platform. The React dashboard consumes the FastAPI service for planetary information, locations, NASA dataset records and Earth analog comparisons.

## Run the application locally

Use three terminals. Start the data API first:

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Start the AI assistant in a second terminal. Copy `ai-assistant/.env.example` to `.env`, add a Google Gemini API key, then run:

```bash
cd ai-assistant
npm install
npm start
```

Start the frontend in a third terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the frontend terminal (normally `http://localhost:5173`). Its development proxy forwards `/api/*` and `/health` to the data API at `http://127.0.0.1:8000`, and `/assistant-api/*` to the AI service at `http://127.0.0.1:5001`. The AI assistant needs a valid `GEMINI_API_KEY`; the comparison API works independently.

## Deployment configuration

For a separately hosted frontend, set `VITE_API_BASE_URL` to the FastAPI origin and `VITE_ASSISTANT_API_URL` to the AI service origin including its `/api` path (for example, `https://assistant.example.com/api`) when building the frontend. Set `TERRATWIN_FRONTEND_ORIGINS` on the backend to a comma-separated list of allowed frontend origins, such as `https://terratwin.example.com`. Local Vite origins remain enabled by default.

The interactive analog comparison uses `/api/analyze/compare`. Current Earth reference regions include Atacama Desert, Salar de Atacama, Bioko Island, Pico Basilé, Moka Highlands and Gran Caldera de Luba. The site inventory is available at `/api/analyze/earth-candidates`; rankings compare prepared terrain-shape features and remain preliminary. Raster-processing workflows require Rasterio, NumPy and the source rasters in `backend/data/nasa_cache`.
