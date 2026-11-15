
import httpx

from app.services.dataset_catalogue import (
    get_all_datasets,
    get_datasets_by_planet,
    get_datasets_by_category
)


NASA_CMR_URL = "https://cmr.earthdata.nasa.gov/search/collections.json"

ODE_API_URL = "https://oderest.rsl.wustl.edu/live2/"


# --------------------------------------------------
# NASA EARTHDATA COLLECTION SEARCH
# --------------------------------------------------

def search_earthdata_collections(keyword: str, page_size: int = 10):
    """
    Search NASA Earthdata collection catalogue.
    Returns dataset metadata in JSON format.
    """

    if not keyword or not keyword.strip():
        raise ValueError("Search keyword cannot be empty")

    if not 1 <= page_size <= 100:
        raise ValueError("Page size must be between 1 and 100")

    params = {
        "keyword": keyword.strip(),
        "page_size": page_size
    }

    try:
        response = httpx.get(
            NASA_CMR_URL,
            params=params,
            headers={"Accept": "application/json"},
            timeout=30.0
        )

        response.raise_for_status()
        result = response.json()

        collections = result.get("feed", {}).get("entry", [])

        datasets = []

        for item in collections:
            datasets.append({
                "dataset_id": item.get("id"),
                "title": item.get("title"),
                "short_name": item.get("short_name"),
                "version": item.get("version_id"),
                "provider": item.get("archive_center"),
                "description": item.get("summary"),
                "start_date": item.get("time_start"),
                "end_date": item.get("time_end")
            })

        return {
            "status": "success",
            "source": "NASA Earthdata CMR",
            "keyword": keyword,
            "total_results": len(datasets),
            "datasets": datasets
        }

    except httpx.HTTPStatusError as error:
        raise RuntimeError(
            f"NASA API returned HTTP {error.response.status_code}"
        ) from error

    except httpx.RequestError as error:
        raise RuntimeError(
            f"Could not connect to NASA API: {error}"
        ) from error


# --------------------------------------------------
# NASA PDS ODE INSTRUMENT CATALOGUE
# --------------------------------------------------

def get_planetary_instruments(target: str):
    """
    Retrieve NASA ODE instrument and product-type catalogue
    for Moon or Mars.
    """

    target = target.strip().lower()

    if target not in ["moon", "mars"]:
        raise ValueError("Target must be Moon or Mars")

    params = {
        "query": "iipt",
        "output": "JSON",
        "odemetadb": target
    }

    try:
        response = httpx.get(
            ODE_API_URL,
            params=params,
            headers={"Accept": "application/json"},
            timeout=30.0
        )

        response.raise_for_status()
        result = response.json()

        return {
            "status": "success",
            "source": "NASA PDS Orbital Data Explorer",
            "target": target,
            "catalogue": result
        }

    except httpx.HTTPStatusError as error:
        raise RuntimeError(
            f"NASA ODE returned HTTP {error.response.status_code}"
        ) from error

    except httpx.RequestError as error:
        raise RuntimeError(
            f"Could not connect to NASA ODE: {error}"
        ) from error

    except ValueError as error:
        raise RuntimeError(
            "NASA ODE returned an invalid JSON response"
        ) from error


# --------------------------------------------------
# FILTER RELEVANT MOON AND MARS PRODUCTS
# --------------------------------------------------

def get_relevant_planetary_products(target: str):

    catalogue = get_planetary_instruments(target)

    records = catalogue["catalogue"]["ODEResults"]["IIPTSets"]["IIPTSet"]

    if isinstance(records, dict):
        records = [records]

    keywords = [
        "MOLA", "THEMIS", "TES", "CTX", "HIRISE",
        "LOLA", "DIVINER", "LROC", "LUNAR RECONNAISSANCE"
    ]

    results = []

    for item in records:

        text = " ".join(
            str(value) for value in item.values()
        ).upper()

        if any(keyword in text for keyword in keywords):

            results.append({
                "instrument_id": item.get("IID"),
                "instrument_name": item.get("IName"),
                "instrument_host_id": item.get("IHID"),
                "product_type": item.get("PT"),
                "product_description": item.get("PTName"),
                "dataset_id": item.get("DataSetId"),
                "number_of_products": item.get("NumberProducts")
            })

    return results


# --------------------------------------------------
# TERRATWIN DATASET CATALOGUE
# --------------------------------------------------

def get_terratwin_dataset_catalogue():

    return {
        "status": "success",
        "source": "TerraTwin NASA Dataset Catalogue",
        "total": len(get_all_datasets()),
        "data": get_all_datasets()
    }


def get_planet_dataset_catalogue(planet: str):

    datasets = get_datasets_by_planet(planet)

    return {
        "status": "success",
        "planet": planet.lower(),
        "total": len(datasets),
        "data": datasets
    }


# --------------------------------------------------
# NASA INDIVIDUAL PRODUCT METADATA AND FILES
# --------------------------------------------------


def get_planetary_product_files(
    target: str,
    instrument_host_id: str,
    instrument_id: str,
    product_type: str,
    dataset_id: str,
    limit: int = 5,
    offset: int = 0
):
    """
    Retrieve NASA planetary products and return
    a simplified JSON response for TerraTwin.
    """

    target = target.strip().lower()

    if target not in ["moon", "mars"]:
        raise ValueError("Target must be Moon or Mars")

    if not all([
        instrument_host_id,
        instrument_id,
        product_type,
        dataset_id
    ]):
        raise ValueError("All dataset parameters are required")

    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    if offset < 0:
        raise ValueError("Offset cannot be negative")

    params = {
        "query": "product",
        "target": target,
        "ihid": instrument_host_id.strip(),
        "iid": instrument_id.strip(),
        "pt": product_type.strip(),
        "dsid": dataset_id.strip(),
        "results": "opfm",
        "output": "JSON",
        "limit": limit,
        "offset": offset
    }

    try:
        response = httpx.get(
            ODE_API_URL,
            params=params,
            headers={"Accept": "application/json"},
            timeout=60.0
        )

        response.raise_for_status()
        result = response.json()

        ode_results = result.get("ODEResults", {})

        if str(ode_results.get("Status", "")).upper() == "ERROR":
            raise RuntimeError(
                str(ode_results.get("Error", "NASA ODE query failed"))
            )

        products = (
            ode_results
            .get("Products", {})
            .get("Product", [])
        )

        if isinstance(products, dict):
            products = [products]

        clean_products = []

        for product in products:

            product_files = (
                product.get("Product_files", {})
                .get("Product_file", [])
            )

            if isinstance(product_files, dict):
                product_files = [product_files]

            data_file = None
            label_file = None

            for file in product_files:

                description = str(
                    file.get("Description", "")
                ).upper()

                file_type = str(
                    file.get("Type", "")
                ).upper()

                if (
                    "PRODUCT DATA FILE" in description
                    and file_type == "PRODUCT"
                ):
                    data_file = {
                        "filename": file.get("FileName"),
                        "download_url": file.get("URL"),
                        "size_kb": file.get("KBytes")
                    }

                if (
                    "LABEL FILE" in description
                    and file_type == "PRODUCT"
                ):
                    label_file = {
                        "filename": file.get("FileName"),
                        "download_url": file.get("URL")
                    }

            clean_products.append({
                "product_id": product.get("pdsid"),
                "product_name": product.get("Product_name"),
                "product_title": product.get("Product_title"),
                "planet": product.get("Target_name"),
                "instrument": product.get("iid"),
                "product_type": product.get("pt"),

                "latitude": {
                    "minimum": product.get("Minimum_latitude"),
                    "maximum": product.get("Maximum_latitude")
                },

                "longitude": {
                    "westernmost": product.get("Westernmost_longitude"),
                    "easternmost": product.get("Easternmost_longitude")
                },

                "resolution_m_per_pixel": product.get("Map_resolution"),

                "data_file": data_file,
                "label_file": label_file,

                "product_details_url": product.get("ProductURL")
            })

        return {
            "status": "success",
            "source": "NASA PDS Orbital Data Explorer",
            "target": target,
            "dataset_id": dataset_id,
            "instrument": instrument_id,
            "product_type": product_type,
            "total_returned": len(clean_products),
            "limit": limit,
            "offset": offset,
            "products": clean_products
        }

    except httpx.HTTPStatusError as error:
        raise RuntimeError(
            f"NASA ODE returned HTTP {error.response.status_code}"
        ) from error

    except httpx.RequestError as error:
        raise RuntimeError(
            f"Could not connect to NASA ODE: {error}"
        ) from error

    except ValueError as error:
        raise RuntimeError(
            "NASA ODE returned an invalid JSON response"
        ) from error
