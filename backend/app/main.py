
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from time import perf_counter

from app.routes.analysis import router as analysis_router
from app.routes.locations import router as locations_router
from app.routes.planets import router as planets_router
from app.logger_config import logger

from app.routes.datasets import router as datasets_router

# Initialize application
app = FastAPI(
    title="TerraTwin API",
    description="Earth Analog Discovery Platform",
    version="1.0.0"
)

logger.info("TerraTwin backend started")


# API Request Logging Middleware
@app.middleware("http")
async def log_api_requests(request: Request, call_next):

    start_time = perf_counter()

    try:
        response = await call_next(request)

        duration = round(
            (perf_counter() - start_time) * 1000, 2
        )

        logger.info(
            "Request: %s %s | Status: %s | Duration: %s ms",
            request.method,
            request.url.path,
            response.status_code,
            duration
        )

        return response

    except Exception:
        logger.exception(
            "Request failed: %s %s",
            request.method,
            request.url.path
        )
        raise


# Frontend communication settings
frontend_origins = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}
frontend_origins.update(
    origin.strip().rstrip("/")
    for origin in os.getenv("TERRATWIN_FRONTEND_ORIGINS", "").split(",")
    if origin.strip()
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(frontend_origins),
    allow_methods=["*"],
    allow_headers=["*"]
)


# Register planetary routes
app.include_router(
    planets_router,
    prefix="/api/planets",
    tags=["Planets"]
)

app.include_router(
    locations_router,
    prefix="/api/locations",
    tags=["Locations"]
)

app.include_router(
    analysis_router,
    prefix="/api/analyze",
    tags=["Analysis"]
)

app.include_router(
    datasets_router,
    prefix="/api",
    tags=["NASA Datasets"]
)

# Home API
@app.get("/")
def home():
    logger.info("Home endpoint accessed")

    return {
        "status": "success",
        "message": "TerraTwin backend is running",
        "data": {
            "project": "TerraTwin",
            "service": "Backend API",
            "version": "1.0.0"
        }
    }


# Health Check API
@app.get("/health")
def health_check():
    logger.info("Health check requested")

    return {
        "status": "success",
        "message": "Backend service is healthy",
        "data": {
            "service": "TerraTwin Backend",
            "health": "healthy"
        }
    }
