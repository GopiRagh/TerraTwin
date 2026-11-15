# TerraTwin frontend

React and Vite client for the TerraTwin FastAPI service.

## Run locally

Start the FastAPI data service from the `backend` directory in one terminal:

```bash
python -m uvicorn app.main:app --reload
```

Start the AI service from `ai-assistant` in a second terminal. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`:

```bash
npm install
npm start
```

Install and start the frontend from `frontend` in a third terminal:

```bash
npm install
npm run dev
```

Vite proxies `/api/*` and `/health` to `http://127.0.0.1:8000` and `/assistant-api/*` to the AI service at `http://127.0.0.1:5001` during development. Set `VITE_API_BASE_URL` and `VITE_ASSISTANT_API_URL` to their service origins when deploying separately.

The dashboard loads planets, locations and the dataset catalogue from the API. The analog form posts to `/api/analyze/compare`. Comparison data is available only for supported sites that have feature files in `backend/data/nasa_cache`.
