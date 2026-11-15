
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin


CACHE_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "nasa_cache"
)


def convert_mola_to_geotiff():

    image_path = CACHE_DIR / "megt00n000hb.img"

    output_path = CACHE_DIR / "megt00n000hb.tif"

    if not image_path.exists():
        raise FileNotFoundError("NASA MOLA image not found")

    rows = 5632
    columns = 11520

    expected_size = rows * columns * 2

    if image_path.stat().st_size != expected_size:
        raise ValueError("Raster file size does not match NASA label")

    elevation = np.fromfile(
        image_path,
        dtype=">i2"
    ).reshape((rows, columns))

    # Geographic coverage from NASA label
    west = 0.0
    east = 90.0
    north = 0.0
    south = -44.0

    pixel_width = (east - west) / columns
    pixel_height = (north - south) / rows

    transform = from_origin(
        west,
        north,
        pixel_width,
        pixel_height
    )

    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=rows,
        width=columns,
        count=1,
        dtype="int16",
        crs="+proj=longlat +a=3396000 +b=3396000 +no_defs +type=crs",
        transform=transform,
        compress="deflate"
    ) as destination:

        destination.write(
            elevation.astype("int16"),
            1
        )

    return {
        "status": "success",
        "filename": output_path.name,
        "local_path": str(output_path),
        "width": columns,
        "height": rows,
        "data_type": "int16",
        "unit": "meters",
        "bounds": {
            "west": west,
            "east": east,
            "south": south,
            "north": north
        },
        "pixel_resolution_degrees": {
            "longitude": pixel_width,
            "latitude": pixel_height
        }
    }
