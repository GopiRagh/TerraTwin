
from fastapi import APIRouter, HTTPException
import logging

router = APIRouter()
logger = logging.getLogger("TerraTwin")


PLANETS = {
    "earth": {
        "id": "earth",
        "name": "Earth",
        "type": "Planet",
        "description": "Our home planet",
        "role": "Earth analog search destination"
    },
    "moon": {
        "id": "moon",
        "name": "Moon",
        "type": "Natural Satellite",
        "description": "Earth's natural satellite",
        "role": "Lunar reference environment"
    },
    "mars": {
        "id": "mars",
        "name": "Mars",
        "type": "Planet",
        "description": "The Red Planet",
        "role": "Martian reference environment"
    }
}


@router.get("/")
def get_all_planets():
    logger.info("Fetching all planetary bodies")

    return {
        "status": "success",
        "message": "Planetary bodies retrieved successfully",
        "total": len(PLANETS),
        "data": list(PLANETS.values())
    }


@router.get("/{planet_id}")
def get_planet(planet_id: str):
    logger.info("Fetching planet: %s", planet_id)

    planet = PLANETS.get(planet_id.lower())

    if not planet:
        logger.warning("Planet not found: %s", planet_id)

        raise HTTPException(
            status_code=404,
            detail="Planetary body not found"
        )

    return {
        "status": "success",
        "message": "Planet retrieved successfully",
        "data": planet
    }
