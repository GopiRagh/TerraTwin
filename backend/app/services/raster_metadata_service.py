
import json
from pathlib import Path

import rasterio


CACHE_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "nasa_cache"
)


def generate_raster_metadata():

    raster_path = CACHE_DIR / "megt00n000hb.tif"
    output_path = CACHE_DIR / "megt00n000hb_metadata.json"

    if not raster_path.exists():
        raise FileNotFoundError("MOLA GeoTIFF not found")

    with rasterio.open(raster_path) as dataset:

        metadata = {
            "dataset_id": "MARS_MOLA_MEGDR_001",
            "dataset_name": "Mars MOLA MEGDR Topography",
            "source": "NASA PDS Geosciences Node",
            "planet": "Mars",
            "instrument": "MOLA",
            "product_type": "Elevation DEM",

            "files": {
                "raster": raster_path.name,
                "label": "megt00n000hb.lbl",
                "original_image": "megt00n000hb.img"
            },

            "format": "GeoTIFF",
            "width": dataset.width,
            "height": dataset.height,
            "bands": dataset.count,
            "data_type": dataset.dtypes[0],
            "elevation_unit": "meters",

            "spatial_reference": {
                "coordinate_system": "Planetocentric",
                "projection": "Simple Cylindrical",
                "planetary_radius_m": 3396000,
                "crs_wkt": dataset.crs.to_wkt()
            },

            "geographic_bounds": {
                "west": dataset.bounds.left,
                "south": dataset.bounds.bottom,
                "east": dataset.bounds.right,
                "north": dataset.bounds.top
            },

            "resolution_degrees": {
                "longitude": dataset.res[0],
                "latitude": abs(dataset.res[1])
            },

            "elevation_statistics": {
                "minimum_m": -8208,
                "maximum_m": 4686,
                "mean_m": 130.77
            },

            "status": "processed"
        }

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

    return {
        "status": "success",
        "metadata_file": output_path.name,
        "local_path": str(output_path)
    }
