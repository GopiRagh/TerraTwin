
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
import logging

from app.services.analysis_service import (
    create_analysis_request,
    get_analysis_request,
    get_all_analysis_requests,
    update_analysis_request
)

from app.services.similarity_service import rank_earth_analogs
from app.services.similarity_service import get_earth_analog_sites

router = APIRouter()
logger = logging.getLogger("TerraTwin")


class AnalysisRequest(BaseModel):
    target_planet: str
    target_location: str = Field(min_length=2, max_length=150)

    @field_validator("target_planet")
    @classmethod
    def validate_planet(cls, value):
        value = value.strip().lower()

        if value not in ["moon", "mars"]:
            raise ValueError("Target planet must be Moon or Mars")

        return value

    @field_validator("target_location")
    @classmethod
    def validate_location(cls, value):
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Location name is too short")

        return value


# Create a new analysis request
@router.post("/")
def analyze_location(request: AnalysisRequest):
    logger.info(
        "Creating analysis request for %s - %s",
        request.target_planet,
        request.target_location
    )

    analysis = create_analysis_request(
        request.target_planet,
        request.target_location
    )

    return {
        "status": "accepted",
        "message": "Analysis request created successfully",
        "data": analysis
    }


# Get all analysis requests
@router.get("/")
def get_analysis_requests():
    logger.info("Fetching all analysis requests")

    requests = get_all_analysis_requests()

    return {
        "status": "success",
        "message": "Analysis requests retrieved successfully",
        "total": len(requests),
        "data": requests
    }


# Compare target planetary location with Earth analogs


@router.post("/compare")
def compare_earth_analogs(request: AnalysisRequest):

    logger.info(
        "Comparing Earth analogs for %s - %s",
        request.target_planet,
        request.target_location
    )

    analysis = create_analysis_request(
        request.target_planet,
        request.target_location
    )

    analysis_id = analysis["analysis_id"]

    try:
        comparison = rank_earth_analogs(
            request.target_planet,
            request.target_location
        )

        update_analysis_request(
            analysis_id,
            "completed",
            comparison["results"]
        )

        return {
            "status": "success",
            "message": "Earth analog comparison completed",
            "analysis_id": analysis_id,
            "data": comparison
        }

    except ValueError as error:
        update_analysis_request(analysis_id, "failed")
        logger.warning("Invalid comparison request: %s", error)

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except FileNotFoundError as error:
        update_analysis_request(analysis_id, "failed")
        logger.error("Feature dataset unavailable: %s", error)

        raise HTTPException(
            status_code=503,
            detail="Required regional feature dataset is unavailable"
        )


@router.get("/earth-candidates")
def get_available_earth_candidates():
    sites = get_earth_analog_sites()
    return {
        "status": "success",
        "message": "Earth analog candidate regions retrieved successfully",
        "total": len(sites),
        "data": sites,
    }


# Get individual analysis request status
@router.get("/{analysis_id}")
def get_analysis_status(analysis_id: str):
    logger.info("Fetching analysis request: %s", analysis_id)

    analysis = get_analysis_request(analysis_id)

    if analysis is None:
        logger.warning("Analysis request not found: %s", analysis_id)

        raise HTTPException(
            status_code=404,
            detail="Analysis request not found"
        )

    return {
        "status": "success",
        "message": "Analysis request retrieved successfully",
        "data": analysis
    }
