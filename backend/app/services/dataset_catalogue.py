
"""
TerraTwin NASA Dataset Catalogue

Contains verified dataset catalogue entries identified
through NASA Earthdata CMR and NASA PDS ODE.
"""

DATASET_CATALOGUE = [

    # ================= EARTH =================

    {
        "dataset_id": "C1711961296-LPCLOUD",
        "name": "ASTER Global Digital Elevation Model V003",
        "planet": "earth",
        "category": "elevation",
        "instrument": "ASTER",
        "product_type": "DEM",
        "provider": "NASA LP DAAC",
        "resolution": "Approximately 30 metres",
        "source": "NASA Earthdata CMR",
        "purpose": "Earth elevation and terrain comparison",
        "catalogue_status": "identified"
    },

    {
        "dataset_id": "SRTMGL1.003",
        "name": "NASA SRTM Global 1 Arc-Second Elevation",
        "planet": "earth",
        "category": "elevation",
        "instrument": "Shuttle Radar Topography Mission",
        "product_type": "Global DEM",
        "provider": "NASA LP DAAC",
        "resolution": "1 arc-second (approximately 30 metres)",
        "source": "NASA Earthdata / LP DAAC",
        "purpose": "Global elevation reference for comparing Earth analog terrain",
        "catalogue_status": "identified"
    },

    {
        "dataset_id": "EARTH_COPERNICUS_GLO30_001",
        "name": "Copernicus DEM GLO-30",
        "planet": "earth",
        "category": "elevation",
        "instrument": "Not applicable",
        "product_type": "DSM",
        "provider": "ESA Copernicus",
        "resolution": "Approximately 30 metres",
        "source": "Copernicus DEM AWS Public Archive",
        "purpose": "Earth elevation and terrain comparison",
        "catalogue_status": "downloaded"
    },

    {
        "dataset_id": "COPERNICUS_GLO30_ATACAMA_SALAR_001",
        "name": "Copernicus GLO-30 — Salar de Atacama tile",
        "planet": "earth",
        "category": "elevation",
        "instrument": "Not applicable",
        "product_type": "Digital Surface Model (DSM)",
        "provider": "ESA Copernicus",
        "resolution": "Approximately 30 metres",
        "source": "Copernicus GLO-30 local raster",
        "purpose": "Elevation data for the Salar de Atacama Earth analog region",
        "catalogue_status": "downloaded",
        "local_files": ["Copernicus_DSM_COG_10_S24_00_W069_00_DEM.tif"]
    },

    {
        "dataset_id": "COPERNICUS_GLO30_BIOKO_001",
        "name": "Copernicus GLO-30 — Bioko Island tile",
        "planet": "earth",
        "category": "elevation",
        "instrument": "Not applicable",
        "product_type": "Digital Surface Model (DSM)",
        "provider": "ESA Copernicus",
        "resolution": "Approximately 30 metres",
        "source": "Copernicus GLO-30 local raster",
        "purpose": "Elevation data for volcanic terrain at Pico Basilé, an Earth analog region",
        "catalogue_status": "downloaded",
        "local_files": ["Copernicus_DSM_COG_10_N03_00_E008_00_DEM.tif"]
    },

    # ================= MOON =================

    {
        "dataset_id": "lro_lola_rdr-data_gridded",
        "name": "LOLA Gridded Digital Elevation Model",
        "planet": "moon",
        "category": "elevation",
        "instrument": "LOLA",
        "product_type": "GDRDEM",
        "provider": "NASA PDS",
        "resolution": "Approximately 1.9 kilometres per pixel",
        "source": "NASA PDS ODE",
        "purpose": "Lunar elevation and terrain comparison",
        "catalogue_status": "downloaded",
        "local_files": ["ldem_16.tif"]
    },

    {
        "dataset_id": "lro_lola_rdr-data_gridded",
        "name": "LOLA Gridded Slope Map",
        "planet": "moon",
        "category": "slope",
        "instrument": "LOLA",
        "product_type": "GDRDSM",
        "provider": "NASA PDS",
        "resolution": "Approximately 1.9 kilometres per pixel",
        "source": "NASA PDS ODE",
        "purpose": "Lunar slope and surface analysis",
        "catalogue_status": "downloaded",
        "local_files": ["ldsm_16.img"]
    },

    {
        "dataset_id": "lro_diviner_derived_gdr_l3",
        "name": "Diviner Gridded Data Record Level 3",
        "planet": "moon",
        "category": "temperature",
        "instrument": "Diviner",
        "product_type": "GDR_L3",
        "provider": "NASA PDS",
        "source": "NASA PDS ODE",
        "purpose": "Lunar surface thermal comparison",
        "catalogue_status": "downloaded",
        "local_files": ["global_ti_day_2007.img"]
    },

    {
        "dataset_id": "lro-l-lroc-5-rdr",
        "name": "LROC Wide Angle Camera Monthly Global Mosaic",
        "planet": "moon",
        "category": "imagery",
        "instrument": "LROC",
        "product_type": "SDPWMG",
        "provider": "NASA PDS",
        "source": "NASA PDS ODE",
        "purpose": "Lunar surface visual comparison",
        "catalogue_status": "identified"
    },

    {
        "dataset_id": "LRO-L-LOLA-4-GDR-V1.0",
        "name": "LOLA Global Elevation Grid - 64 Pixels per Degree",
        "planet": "moon",
        "category": "elevation",
        "instrument": "LOLA",
        "product_type": "GDR / 64 ppd",
        "provider": "NASA PDS",
        "resolution": "Approximately 0.5 kilometres per pixel at the equator",
        "source": "NASA PDS Geosciences Node",
        "purpose": "Higher-detail lunar elevation reference for regional terrain analysis",
        "catalogue_status": "identified"
    },

    # ================= MARS =================

    {
        "dataset_id": "mgs_mola_topography_derived-data_meg128",
        "name": "MOLA Mission Experiment Gridded Data Record",
        "planet": "mars",
        "category": "elevation",
        "instrument": "MOLA",
        "product_type": "MEGDR",
        "provider": "NASA PDS",
        "source": "NASA PDS ODE",
        "purpose": "Mars elevation and terrain comparison",
        "catalogue_status": "downloaded",
        "local_files": ["megt00n000hb.tif"]
    },

    {
        "dataset_id": "ody.themis.geo_data_irpbt",
        "name": "THEMIS Infrared Projected Brightness Temperature",
        "planet": "mars",
        "category": "temperature",
        "instrument": "THEMIS",
        "product_type": "IRPBT4",
        "provider": "NASA PDS",
        "source": "NASA PDS ODE",
        "purpose": "Mars thermal surface comparison",
        "catalogue_status": "downloaded",
        "local_files": ["I56585002PBT.IMG", "I56585006PBT.IMG"]
    },

    {
        "dataset_id": "MGS-M-TES-5-TIMAP-V1.0",
        "name": "TES Thermal Inertia Map",
        "planet": "mars",
        "category": "thermal_inertia",
        "instrument": "TES",
        "product_type": "TIMAP",
        "provider": "NASA PDS",
        "source": "NASA PDS ODE",
        "purpose": "Mars surface thermal property comparison",
        "catalogue_status": "identified"
    },

    {
        "dataset_id": "MRO-M-HIRISE-5-DTM-V1.0",
        "name": "HiRISE Digital Terrain Model",
        "planet": "mars",
        "category": "elevation",
        "instrument": "HiRISE",
        "product_type": "DTM",
        "provider": "NASA PDS",
        "source": "NASA PDS ODE",
        "purpose": "Detailed local Mars terrain analysis",
        "catalogue_status": "downloaded"
    },

    {
        "dataset_id": "MRO-M-CTX-2-EDR-L0-V1.0",
        "name": "MRO Context Camera Image Archive",
        "planet": "mars",
        "category": "imagery",
        "instrument": "CTX",
        "product_type": "EDR",
        "provider": "NASA PDS",
        "resolution": "Typically approximately 6 metres per pixel; varies by observation",
        "source": "NASA PDS Imaging Node",
        "purpose": "Regional context imagery for inspecting Martian terrain and landforms",
        "catalogue_status": "identified"
    },

    {
        "dataset_id": "MEX-M-HRSC-5-REFDR-MAPPROJECTED-V3.0",
        "name": "Mars Express HRSC Map-Projected Images",
        "planet": "mars",
        "category": "imagery",
        "instrument": "HRSC",
        "product_type": "Map-projected REFDR",
        "provider": "NASA PDS / ESA Mars Express",
        "resolution": "Varies by image and map projection",
        "source": "NASA PDS Geosciences Node",
        "purpose": "Georeferenced Mars imagery for regional surface and morphology review",
        "catalogue_status": "identified"
    }
]


def get_all_datasets():
    return DATASET_CATALOGUE


def get_datasets_by_planet(planet: str):
    planet = planet.strip().lower()

    if planet not in ["earth", "moon", "mars"]:
        raise ValueError("Planet must be Earth, Moon or Mars")

    return [
        dataset for dataset in DATASET_CATALOGUE
        if dataset["planet"] == planet
    ]


def get_datasets_by_category(category: str):
    category = category.strip().lower()

    return [
        dataset for dataset in DATASET_CATALOGUE
        if dataset["category"] == category
    ]
