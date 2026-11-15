from app.services.nasa_download_service import download_nasa_file
from fastapi import APIRouter, HTTPException, Query

from app.services.nasa_service import (
    get_terratwin_dataset_catalogue,
    get_planet_dataset_catalogue,
    search_earthdata_collections,
    get_relevant_planetary_products,
    get_planetary_product_files
)

router = APIRouter(
    prefix="/datasets",
    tags=["NASA Datasets"]
)


@router.get("/")
def get_all_nasa_datasets():
    return get_terratwin_dataset_catalogue()


@router.get("/earth/search")
def search_earth_datasets(
    keyword: str = Query(..., min_length=2),
    page_size: int = Query(10, ge=1, le=50)
):
    try:
        return search_earthdata_collections(keyword, page_size)
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))


@router.get("/planetary/{target}/products")
def get_planetary_products(target: str):
    try:
        if target.lower() not in ["moon", "mars"]:
            raise ValueError("Target must be Moon or Mars")

        return {
            "status": "success",
            "target": target.lower(),
            "data": get_relevant_planetary_products(target)
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))


@router.get("/{planet}")
def get_datasets_for_planet(planet: str):
    try:
        return get_planet_dataset_catalogue(planet)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/planetary/{target}/product-files")
def get_nasa_product_files(
    target: str,
    instrument_host_id: str,
    instrument_id: str,
    product_type: str,
    dataset_id: str,
    limit: int = Query(5, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    try:
        return get_planetary_product_files(
            target=target,
            instrument_host_id=instrument_host_id,
            instrument_id=instrument_id,
            product_type=product_type,
            dataset_id=dataset_id,
            limit=limit,
            offset=offset
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=str(error)
        )    

 
@router.post("/planetary/{target}/download")
def download_planetary_dataset(
    target: str,
    product_id: str,
    instrument_host_id: str,
    instrument_id: str,
    product_type: str,
    dataset_id: str
):
    try:
        # Retrieve product metadata from NASA ODE
        result = get_planetary_product_files(
            target=target,
            instrument_host_id=instrument_host_id,
            instrument_id=instrument_id,
            product_type=product_type,
            dataset_id=dataset_id,
            limit=50,
            offset=0
        )

        # Find the requested product
        selected_product = next(
            (
                product for product in result["products"]
                if product.get("product_id", "").lower()
                == product_id.lower()
            ),
            None
        )

        if not selected_product:
            raise HTTPException(
                status_code=404,
                detail="NASA product ID not found"
            )

        data_file = selected_product.get("data_file")

        if not data_file or not data_file.get("download_url"):
            raise HTTPException(
                status_code=404,
                detail="NASA raster download URL not available"
            )

        # Download and cache the raster
        return download_nasa_file(
            download_url=data_file["download_url"],
            filename=data_file["filename"]
        )

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=str(error)
        )
   