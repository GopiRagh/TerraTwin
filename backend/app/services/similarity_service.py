
import json
import math
from pathlib import Path

CACHE_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "nasa_cache"
)

def load_feature_file(filename):
    """Load regional terrain features from a JSON file."""

    filepath = CACHE_DIR / filename

    if not filepath.exists():
        raise FileNotFoundError(
            f"Feature file not found: {filepath}"
        )

    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_shape_features(data):
    """Calculate dimensionless terrain-shape features."""

    elevation = data["elevation_features"]

    minimum = float(elevation["minimum"])
    maximum = float(elevation["maximum"])
    mean = float(elevation["area_weighted_mean"])
    std_dev = float(
        elevation["area_weighted_standard_deviation"]
    )

    elevation_range = maximum - minimum

    if elevation_range <= 0:
        raise ValueError("Invalid elevation range")

    if not all(
        math.isfinite(value)
        for value in [minimum, maximum, mean, std_dev]
    ):
        raise ValueError("Non-finite elevation feature")

    if std_dev < 0:
        raise ValueError("Standard deviation cannot be negative")

    return {
        "relative_roughness": std_dev / elevation_range,
        "relative_mean_position": (
            mean - minimum
        ) / elevation_range
    }


def calculate_similarity(target_features, candidate_features):
    """Calculate a provisional similarity score."""

    differences = [
        abs(
            target_features[key]
            - candidate_features[key]
        )
        for key in target_features
    ]

    distance = math.sqrt(
        sum(value ** 2 for value in differences)
    )

    maximum_distance = math.sqrt(2)

    score = max(
        0.0,
        100.0 * (1 - distance / maximum_distance)
    )

    return round(score, 2)


def get_earth_analog_sites():
    """List the Earth regions with cached feature data for comparison."""

    sites = []

    for filepath in sorted(CACHE_DIR.glob("*_weighted_features.json")):
        candidate = load_feature_file(filepath.name)

        if candidate.get("planet", "").lower() != "earth":
            continue

        sites.append({
            "location": candidate["location"],
            "region_type": candidate.get("region_type"),
            "coordinates": candidate.get("coordinates"),
            "radius_km": candidate.get("radius_km"),
            "source": candidate.get("data_quality", {}).get("source"),
            "data_quality": candidate.get("data_quality", {}),
        })

    return sites


def rank_earth_analogs(target_planet, target_location):
    """Rank available Earth regions against a target region."""

    planet = target_planet.strip().lower()

    if planet not in {"moon", "mars"}:
        raise ValueError("Target planet must be Moon or Mars")

    target = None
    for filepath in sorted(CACHE_DIR.glob("*_weighted_features.json")):
        candidate = load_feature_file(filepath.name)
        if (
            candidate.get("planet", "").lower() == planet
            and candidate.get("location", "").lower()
            == target_location.strip().lower()
        ):
            target = candidate
            break

    if target is None:
        raise ValueError(
            f"Location not found: {target_location}"
        )

    target_features = calculate_shape_features(target)

    earth_files = sorted(CACHE_DIR.glob("*_weighted_features.json"))

    results = []

    for filepath in earth_files:
        candidate = load_feature_file(filepath)

        if candidate.get("planet", "").lower() != "earth":
            continue

        candidate_features = calculate_shape_features(candidate)

        score = calculate_similarity(
            target_features,
            candidate_features
        )

        results.append({
            "location": candidate["location"],
            "region_type": candidate.get("region_type"),
            "coordinates": candidate.get("coordinates"),
            "similarity_score": score,
            "comparison_features": candidate_features,
            "data_quality": candidate.get("data_quality", {}),
            "warnings": [
                "Prototype score uses only two dimensionless elevation-shape features; it is not a measure of climate, habitability, or full geological similarity.",
                "Earth and target planetary raster resolutions differ.",
                "Different elevation datums prevent direct absolute-elevation comparison."
            ]
        })

    results.sort(
        key=lambda item: item["similarity_score"],
        reverse=True
    )

    for rank, result in enumerate(results, start=1):
        result["rank"] = rank
        result["warnings"].append(
            f"Ranked against {len(results)} currently cached Earth regions; "
            "the list is preliminary and does not represent a global survey."
        )

    return {
        "target_planet": planet,
        "target_location": target_location,
        "algorithm": "Dimensionless Elevation Shape Comparison",
        "candidate_count": len(results),
        "results": results
    }
