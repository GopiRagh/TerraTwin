
from pathlib import Path
import rasterio

CACHE_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "nasa_cache"
)


def inspect_nasa_raster(filename: str):

    file_path = CACHE_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Raster file not found: {filename}"
        )

    with rasterio.open(file_path) as dataset:

        return {
            "filename": filename,
            "is_valid": True,
            "driver": dataset.driver,
            "width": dataset.width,
            "height": dataset.height,
            "band_count": dataset.count,
            "data_type": dataset.dtypes,
            "crs": str(dataset.crs),
            "bounds": {
                "left": dataset.bounds.left,
                "bottom": dataset.bounds.bottom,
                "right": dataset.bounds.right,
                "top": dataset.bounds.top
            },
            "resolution": dataset.res,
            "nodata": dataset.nodata
        }
