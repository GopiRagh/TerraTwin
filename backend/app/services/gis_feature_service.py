
import rasterio
from rasterio.warp import transform
import json
from pathlib import Path

import numpy as np
import rasterio


CACHE_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "nasa_cache"
)


# Metadata files corresponding to our downloaded elevation rasters
DATASET_METADATA = {
    "Copernicus_DSM_COG_10_N03_00_E008_00_DEM.tif":
        "copernicus_glo30_metadata.json",

    "ldem_16.tif":
        "lola_ldem16_metadata.json",

    "DTEEC_034934_2155_034499_2155_A01.tif":
        "hirise_dtm_metadata.json"
}


def extract_elevation_features(filename: str):

    raster_path = CACHE_DIR / filename

    if not raster_path.exists():
        raise FileNotFoundError(
            f"Raster not found: {filename}"
        )

    metadata_filename = DATASET_METADATA.get(filename)

    if not metadata_filename:
        raise ValueError(
            f"No metadata mapping found for: {filename}"
        )

    metadata_path = CACHE_DIR / metadata_filename

    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {metadata_filename}"
        )

    with open(metadata_path, "r", encoding="utf-8") as file:
        source_metadata = json.load(file)

    valid_count = 0
    total_sum = 0.0
    total_sum_squares = 0.0
    minimum = float("inf")
    maximum = float("-inf")
    total_pixels = 0

    # Process raster block by block to reduce memory usage
    with rasterio.open(raster_path) as dataset:

        if dataset.count < 1:
            raise ValueError("Raster contains no bands")

        total_pixels = dataset.width * dataset.height
        nodata_value = dataset.nodata

        for _, window in dataset.block_windows(1):

            values = dataset.read(
                1,
                window=window,
                masked=False
            )

            valid_mask = np.isfinite(values)

            if nodata_value is not None:
                valid_mask &= values != nodata_value

            valid_values = values[valid_mask].astype(
                np.float64
            )

            if valid_values.size == 0:
                continue

            valid_count += int(valid_values.size)

            total_sum += float(
                np.sum(valid_values, dtype=np.float64)
            )

            total_sum_squares += float(
                np.sum(valid_values ** 2, dtype=np.float64)
            )

            minimum = min(
                minimum,
                float(np.min(valid_values))
            )

            maximum = max(
                maximum,
                float(np.max(valid_values))
            )

        if valid_count == 0:
            raise ValueError(
                "Raster contains no valid elevation pixels"
            )

        mean = total_sum / valid_count

        variance = max(
            0.0,
            (total_sum_squares / valid_count) - mean ** 2
        )

        standard_deviation = float(np.sqrt(variance))

        nodata_count = total_pixels - valid_count

        return {
            "dataset_id": source_metadata["dataset_id"],
            "dataset_name": source_metadata["dataset_name"],
            "planet": source_metadata["planet"],
            "source": source_metadata["source"],

            "raster": {
                "filename": filename,
                "width": dataset.width,
                "height": dataset.height,
                "bands": dataset.count,
                "data_type": dataset.dtypes[0],
                "crs": str(dataset.crs),
                "bounds": {
                    "left": dataset.bounds.left,
                    "bottom": dataset.bounds.bottom,
                    "right": dataset.bounds.right,
                    "top": dataset.bounds.top
                },
                "resolution": {
                    "x": dataset.res[0],
                    "y": dataset.res[1]
                }
            },

            "elevation_features": {
                "unit": source_metadata.get(
                    "elevation_unit", "meters"
                ),
                "minimum": minimum,
                "maximum": maximum,
                "mean": mean,
                "standard_deviation": standard_deviation
            },

            "data_quality": {
                "total_pixels": total_pixels,
                "valid_pixels": valid_count,
                "nodata_pixels": nodata_count,
                "valid_percentage": (
                    valid_count / total_pixels
                ) * 100,
                "nodata_percentage": (
                    nodata_count / total_pixels
                ) * 100
            },

            "processing": {
                "method": "Block-wise raster statistics",
                "status": "success"
            }
        }


def save_elevation_features(filename: str):

    features = extract_elevation_features(filename)

    output_name = (
        Path(filename).stem + "_features.json"
    )

    output_path = CACHE_DIR / output_name

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(features, file, indent=4)

    return {
        "status": "success",
        "output_file": output_name,
        "local_path": str(output_path),
        "features": features
    }



def check_raster_coverage(filename: str, longitude: float, latitude: float):

    raster_path = CACHE_DIR / filename

    if not raster_path.exists():
        raise FileNotFoundError(
            f"Raster not found: {filename}"
        )

    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90")

    if not -360 <= longitude <= 360:
        raise ValueError("Longitude must be between -360 and 360")

    with rasterio.open(raster_path) as dataset:

        if dataset.crs is None:
            raise ValueError("Raster CRS is missing")

        bounds = dataset.bounds

        if dataset.crs.is_geographic:

            # Convert negative longitude to 0–360
            # when the raster uses positive east longitudes.
            raster_longitude = longitude

            if bounds.left >= 0 and bounds.right > 180:
                raster_longitude = longitude % 360

            x = raster_longitude
            y = latitude

        else:

            # Transform planetary longitude/latitude
            # into the raster's projected coordinate system.
            source_crs = dataset.crs.geodetic_crs

            if source_crs is None:
                raise ValueError(
                    "Could not identify raster geographic CRS"
                )

            transformed_x, transformed_y = transform(
                source_crs,
                dataset.crs,
                [longitude],
                [latitude]
            )

            x = transformed_x[0]
            y = transformed_y[0]

        inside = (
            bounds.left <= x <= bounds.right
            and bounds.bottom <= y <= bounds.top
        )

        return {
            "filename": filename,
            "longitude": longitude,
            "latitude": latitude,
            "raster_x": x,
            "raster_y": y,
            "coverage_status": (
                "coverage_available"
                if inside
                else "coverage_unavailable"
            ),
            "inside_raster": inside,
            "raster_bounds": {
                "left": bounds.left,
                "bottom": bounds.bottom,
                "right": bounds.right,
                "top": bounds.top
            }
        }



def extract_lunar_region(
    longitude: float = 129.78,
    latitude: float = -89.67,
    radius_km: float = 10.0
):
    import numpy as np

    filename = "ldem_16.tif"
    raster_path = CACHE_DIR / filename

    if not raster_path.exists():
        raise FileNotFoundError("LOLA raster not found")

    if not -90 <= latitude <= 90:
        raise ValueError("Invalid latitude")

    if not 0 <= longitude <= 360:
        raise ValueError("Longitude must be between 0 and 360")

    if radius_km <= 0:
        raise ValueError("Radius must be positive")

    # Lunar reference radius in metres
    moon_radius = 1737400.0
    radius_m = radius_km * 1000

    elevation_samples = []

    with rasterio.open(raster_path) as dataset:

        if dataset.crs is None:
            raise ValueError("Lunar CRS is missing")

        if not dataset.crs.is_geographic:
            raise ValueError("Expected geographic lunar raster")

        if dataset.width != 5760 or dataset.height != 2880:
            raise ValueError("Unexpected LOLA raster dimensions")

        # Pixel-centre coordinates
        longitudes = (
            dataset.bounds.left
            + (np.arange(dataset.width) + 0.5) * dataset.res[0]
        )

        # Calculate each pixel's great-circle distance
        for row in range(dataset.height):

            row_latitude = (
                dataset.bounds.top
                - (row + 0.5) * abs(dataset.res[1])
            )

            values = dataset.read(
                1,
                window=((row, row + 1), (0, dataset.width))
            )[0].astype(np.float64)

            lat1 = np.radians(latitude)
            lat2 = np.radians(row_latitude)

            delta_lat = lat2 - lat1
            delta_lon = np.radians(longitudes - longitude)

            haversine = (
                np.sin(delta_lat / 2) ** 2
                + np.cos(lat1) * np.cos(lat2)
                * np.sin(delta_lon / 2) ** 2
            )

            haversine = np.clip(haversine, 0.0, 1.0)

            distance = (
                2 * moon_radius
                * np.arcsin(np.sqrt(haversine))
            )

            region_mask = distance <= radius_m

            # No explicit NoData value is assigned to this GeoTIFF.
            # Exclude non-finite values, but retain this limitation.
            valid_mask = region_mask & np.isfinite(values)

            if np.any(valid_mask):
                elevation_samples.extend(
                    values[valid_mask].tolist()
                )

        if not elevation_samples:
            raise ValueError(
                "No valid elevation pixels found in requested region"
            )

    samples = np.asarray(elevation_samples, dtype=np.float64)

    result = {
        "dataset_id": "LRO-L-LOLA-4-GDR-V1.0",
        "dataset_name": "LOLA Global Elevation DEM",
        "planet": "Moon",
        "location": "Shackleton Crater",

        "region": {
            "center_longitude": longitude,
            "center_latitude": latitude,
            "radius_km": radius_km,
            "distance_method": "Great-circle distance",
            "reference_radius_m": moon_radius
        },

        "elevation_features": {
            "unit": "meters",
            "minimum": float(np.min(samples)),
            "maximum": float(np.max(samples)),
            "mean": float(np.mean(samples)),
            "standard_deviation": float(np.std(samples))
        },

        "data_quality": {
            "valid_pixels": int(samples.size),
            "nodata_policy": (
                "No explicit NoData value assigned; "
                "non-finite values excluded"
            )
        },

        "source": {
            "raster": filename,
            "resolution_degrees": dataset.res,
            "nominal_resolution_m": 1895.21
        },

        "processing": {
            "status": "success",
            "method": "Regional spherical distance extraction"
        }
    }

    return result


def save_lunar_region_features():

    result = extract_lunar_region()

    output_path = (
        CACHE_DIR / "shackleton_crater_features.json"
    )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4)

    return {
        "status": "success",
        "output_file": output_path.name,
        "features": result
    }



def extract_lunar_region_weighted(
    longitude=129.78,
    latitude=-89.67,
    radius_km=10.0,
    location_name="Shackleton Crater"
):
    import numpy as np

    raster_path = CACHE_DIR / "ldem_16.tif"
    moon_radius = 1737400.0

    if not raster_path.exists():
        raise FileNotFoundError("LOLA raster not found")

    if radius_km <= 0:
        raise ValueError("Radius must be positive")

    if not -90 <= latitude <= 90:
        raise ValueError("Invalid latitude")

    if not 0 <= longitude <= 360:
        raise ValueError("Longitude must be between 0 and 360")

    weighted_sum = 0.0
    weighted_sum_squares = 0.0
    total_weight = 0.0
    valid_count = 0
    minimum = float("inf")
    maximum = float("-inf")

    radius_m = radius_km * 1000

    with rasterio.open(raster_path) as dataset:

        for row in range(dataset.height):

            row_lat = (
                dataset.bounds.top
                - (row + 0.5) * abs(dataset.res[1])
            )

            values = dataset.read(
                1,
                window=((row, row + 1), (0, dataset.width))
            )[0].astype(np.float64)

            longitudes = (
                dataset.bounds.left
                + (np.arange(dataset.width) + 0.5)
                * dataset.res[0]
            )

            lat1 = np.radians(latitude)
            lat2 = np.radians(row_lat)
            delta_lon = np.radians(longitudes - longitude)

            haversine = (
                np.sin((lat2 - lat1) / 2) ** 2
                + np.cos(lat1) * np.cos(lat2)
                * np.sin(delta_lon / 2) ** 2
            )

            distance = (
                2 * moon_radius
                * np.arcsin(np.sqrt(np.clip(haversine, 0, 1)))
            )

            mask = (distance <= radius_m) & np.isfinite(values)

            selected = values[mask]

            if selected.size == 0:
                continue

            # Equal angular pixels have area proportional
            # to cosine of their centre latitude.
            weight = float(np.cos(lat2))

            weighted_sum += float(np.sum(selected)) * weight
            weighted_sum_squares += (
                float(np.sum(selected ** 2)) * weight
            )
            total_weight += selected.size * weight

            valid_count += int(selected.size)

            minimum = min(minimum, float(selected.min()))
            maximum = max(maximum, float(selected.max()))

        if valid_count == 0 or total_weight <= 0:
            raise ValueError("No valid regional pixels found")

    mean = weighted_sum / total_weight

    variance = max(
        0.0,
        weighted_sum_squares / total_weight - mean ** 2
    )

    return {
        "planet": "Moon",
        "location": location_name,
        "coordinates": {
            "longitude": longitude,
            "latitude": latitude
        },
        "radius_km": radius_km,
        "elevation_features": {
            "unit": "meters",
            "minimum": minimum,
            "maximum": maximum,
            "area_weighted_mean": mean,
            "area_weighted_standard_deviation": float(
                np.sqrt(variance)
            )
        },
        "data_quality": {
            "selected_pixels": valid_count,
            "weighting": "Cosine of pixel-centre latitude",
            "nodata_limitation": (
                "No explicit NoData constant identified "
                "in the supplied PDS label"
            )
        }
    }



def extract_mars_region_weighted(
    longitude=77.69,
    latitude=18.41,
    radius_km=10.0,
    location_name="Jezero Crater"
):
    import numpy as np

    raster_path = CACHE_DIR / "megt90n000eb.tif"
    mars_radius = 3396000.0

    if not raster_path.exists():
        raise FileNotFoundError("Global MOLA raster not found")

    if radius_km <= 0:
        raise ValueError("Radius must be positive")

    if not -90 <= latitude <= 90:
        raise ValueError("Invalid latitude")

    if not 0 <= longitude <= 360:
        raise ValueError("Longitude must be between 0 and 360")

    weighted_sum = 0.0
    weighted_sum_squares = 0.0
    total_weight = 0.0
    valid_count = 0
    minimum = float("inf")
    maximum = float("-inf")

    radius_m = radius_km * 1000

    with rasterio.open(raster_path) as dataset:

        for row in range(dataset.height):

            y = (
                dataset.transform.f
                + (row + 0.5) * dataset.transform.e
            )

            row_lat = np.degrees(y / mars_radius)

            values = dataset.read(
                1,
                window=((row, row + 1), (0, dataset.width))
            )[0].astype(np.float64)

            x = (
                dataset.transform.c
                + (np.arange(dataset.width) + 0.5)
                * dataset.transform.a
            )

            longitudes = (
                180.0 + np.degrees(x / mars_radius)
            ) % 360.0

            lat1 = np.radians(latitude)
            lat2 = np.radians(row_lat)

            delta_lon = np.radians(
                (longitudes - longitude + 180) % 360 - 180
            )

            haversine = (
                np.sin((lat2 - lat1) / 2) ** 2
                + np.cos(lat1) * np.cos(lat2)
                * np.sin(delta_lon / 2) ** 2
            )

            distance = (
                2 * mars_radius
                * np.arcsin(
                    np.sqrt(np.clip(haversine, 0, 1))
                )
            )

            mask = (
                (distance <= radius_m)
                & np.isfinite(values)
            )

            selected = values[mask]

            if selected.size == 0:
                continue

            weight = float(np.cos(lat2))

            weighted_sum += float(np.sum(selected)) * weight

            weighted_sum_squares += (
                float(np.sum(selected ** 2)) * weight
            )

            total_weight += selected.size * weight
            valid_count += int(selected.size)

            minimum = min(minimum, float(selected.min()))
            maximum = max(maximum, float(selected.max()))

        if valid_count == 0 or total_weight <= 0:
            raise ValueError("No valid regional pixels found")

    mean = weighted_sum / total_weight

    variance = max(
        0.0,
        weighted_sum_squares / total_weight - mean ** 2
    )

    return {
        "planet": "Mars",
        "location": location_name,
        "coordinates": {
            "longitude": longitude,
            "latitude": latitude
        },
        "radius_km": radius_km,
        "elevation_features": {
            "unit": "meters",
            "minimum": minimum,
            "maximum": maximum,
            "area_weighted_mean": mean,
            "area_weighted_standard_deviation": float(
                np.sqrt(variance)
            )
        },
        "data_quality": {
            "selected_pixels": valid_count,
            "weighting": "Cosine of pixel-centre latitude",
            "source": "MGS MOLA MEGDR",
            "limitation": (
                "NASA reports that bins without direct "
                "observations contain interpolated elevations"
            )
        }
    }




def extract_earth_region_weighted(
    longitude=-69.5,
    latitude=-23.5,
    radius_km=10.0,
    raster_filename="Copernicus_DSM_COG_10_S24_00_W070_00_DEM.tif",
    location_name="Atacama Desert",
    land_only=False
):
    import numpy as np

    raster_path = CACHE_DIR / raster_filename
  
    earth_radius = 6371008.8

    if not raster_path.exists():
        raise FileNotFoundError(
        f"Copernicus raster not found: {raster_filename}"
    )
   
    if radius_km <= 0:
        raise ValueError("Radius must be positive")

    if not -90 <= latitude <= 90:
        raise ValueError("Invalid latitude")

    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180")

    weighted_sum = 0.0
    weighted_sum_squares = 0.0
    total_weight = 0.0
    valid_count = 0
    minimum = float("inf")
    maximum = float("-inf")

    radius_m = radius_km * 1000

    with rasterio.open(raster_path) as dataset:

        for row in range(dataset.height):

            row_lat = (
                dataset.transform.f
                + (row + 0.5) * dataset.transform.e
            )

            values = dataset.read(
                1,
                window=((row, row + 1), (0, dataset.width))
            )[0].astype(np.float64)

            valid_mask = dataset.read_masks(
                1,
                window=((row, row + 1), (0, dataset.width))
            )[0] > 0

            longitudes = (
                dataset.transform.c
                + (np.arange(dataset.width) + 0.5)
                * dataset.transform.a
            )

            lat1 = np.radians(latitude)
            lat2 = np.radians(row_lat)

            delta_lon = np.radians(longitudes - longitude)

            haversine = (
                np.sin((lat2 - lat1) / 2) ** 2
                + np.cos(lat1) * np.cos(lat2)
                * np.sin(delta_lon / 2) ** 2
            )

            distance = (
                2 * earth_radius
                * np.arcsin(
                    np.sqrt(np.clip(haversine, 0, 1))
                )
            )

            mask = (
                (distance <= radius_m)
                & valid_mask
                & np.isfinite(values)
            )

            selected = values[mask]

            if selected.size == 0:
                continue

            weight = float(np.cos(lat2))

            weighted_sum += float(np.sum(selected)) * weight

            weighted_sum_squares += (
                float(np.sum(selected ** 2)) * weight
            )

            total_weight += selected.size * weight
            valid_count += int(selected.size)

            minimum = min(minimum, float(selected.min()))
            maximum = max(maximum, float(selected.max()))

        if valid_count == 0 or total_weight <= 0:
            raise ValueError("No valid regional pixels found")

    mean = weighted_sum / total_weight

    variance = max(
        0.0,
        weighted_sum_squares / total_weight - mean ** 2
    )

    return {
        "planet": "Earth",
        "location": location_name,
        "coordinates": {
            "longitude": longitude,
            "latitude": latitude
        },
        "radius_km": radius_km,
        "elevation_features": {
            "unit": "meters",
            "minimum": minimum,
            "maximum": maximum,
            "area_weighted_mean": mean,
            "area_weighted_standard_deviation": float(
                np.sqrt(variance)
            )
        },
        "data_quality": {
            "selected_pixels": valid_count,
            "weighting": "Cosine of pixel-centre latitude",
            "source": "Copernicus GLO-30",
            "dataset_type": "Digital Surface Model (DSM)",
            "nodata_limitation": (
                "No explicit NoData value assigned in the "
                "GeoTIFF metadata; raster validity mask used"
            )
        }
    }

