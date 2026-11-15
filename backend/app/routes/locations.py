
from fastapi import APIRouter, HTTPException
import logging

router = APIRouter()
logger = logging.getLogger("TerraTwin")


LOCATIONS = [
    {
        "id": "mars_001",
        "planet": "mars",
        "name": "Jezero Crater",
        "location_type": "Impact Crater",
        "data_status": "sample"
    },
    {
        "id": "mars_002",
        "planet": "mars",
        "name": "Huygens Crater",
        "location_type": "Impact Crater",
        "data_status": "sample"
    },
    {
        "id": "mars_003",
        "planet": "mars",
        "name": "Hellas Planitia",
        "location_type": "Impact Basin",
        "data_status": "sample"
    },
    {
        "id": "moon_001",
        "planet": "moon",
        "name": "Shackleton Crater",
        "location_type": "Impact Crater",
        "data_status": "sample"
    },
    {
        "id": "moon_002",
        "planet": "moon",
        "name": "Tycho Crater",
        "location_type": "Impact Crater",
        "data_status": "sample"
    },
    {
        "id": "moon_003",
        "planet": "moon",
        "name": "Copernicus Crater",
        "location_type": "Impact Crater",
        "data_status": "sample"
    },
    {
        "id": "earth_001",
        "planet": "earth",
        "name": "Atacama Desert",
        "location_type": "Desert",
        "data_status": "sample"
    }
]


@router.get("/")
def get_all_locations():
    logger.info("Fetching all locations")

    return {
        "status": "success",
        "message": "Locations retrieved successfully",
        "total": len(LOCATIONS),
        "data": LOCATIONS
    }


@router.get("/{location_id}")
def get_location(location_id: str):
    logger.info("Fetching location: %s", location_id)

    for location in LOCATIONS:
        if location["id"] == location_id:
            return {
                "status": "success",
                "message": "Location retrieved successfully",
                "data": location
            }

    logger.warning("Location not found: %s", location_id)

    raise HTTPException(
        status_code=404,
        detail="Location not found"
    )


@router.get("/planet/{planet_name}")
def get_locations_by_planet(planet_name: str):
    logger.info("Fetching locations for planet: %s", planet_name)

    results = [
        location for location in LOCATIONS
        if location["planet"] == planet_name.lower()
    ]

    return {
        "status": "success",
        "message": "Planet locations retrieved successfully",
        "total": len(results),
        "data": results
    }
