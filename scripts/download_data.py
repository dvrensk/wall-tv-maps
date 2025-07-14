#!/usr/bin/env python3
"""
Download geodata for Wall TV Maps project.
Fetches data from OSM, Natural Earth, and Spanish IGN sources.
"""

import os
import sys
import requests
import zipfile
import geopandas as gpd
from pathlib import Path
import logging
from tqdm import tqdm
import click

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Create directories
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url, filename, description=""):
    """Download a file with progress bar."""
    filepath = RAW_DIR / filename

    if filepath.exists():
        logger.info(f"File {filename} already exists, skipping download")
        return filepath

    logger.info(f"Downloading {description or filename}")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))

    with open(filepath, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

    logger.info(f"Downloaded {filename}")
    return filepath

def extract_zip(zip_path, extract_to=None):
    """Extract a zip file."""
    if extract_to is None:
        extract_to = RAW_DIR

    logger.info(f"Extracting {zip_path.name}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    logger.info(f"Extracted {zip_path.name}")

def download_natural_earth_data():
    """Download Natural Earth data."""
    logger.info("Downloading Natural Earth data")

    base_url = "https://naciscdn.org/naturalearth"

    datasets = [
        # Physical data
        ("10m/physical/ne_10m_coastline.zip", "ne_10m_coastline.zip", "Coastlines"),
        ("10m/physical/ne_10m_land.zip", "ne_10m_land.zip", "Land polygons"),
        ("10m/physical/ne_10m_ocean.zip", "ne_10m_ocean.zip", "Ocean polygons"),
        ("10m/physical/ne_10m_rivers_lake_centerlines.zip", "ne_10m_rivers.zip", "Rivers"),
        ("10m/physical/ne_10m_lakes.zip", "ne_10m_lakes.zip", "Lakes"),

        # Cultural data
        ("10m/cultural/ne_10m_admin_0_countries.zip", "ne_10m_countries.zip", "Countries"),
        ("10m/cultural/ne_10m_admin_1_states_provinces.zip", "ne_10m_admin1.zip", "States/Provinces"),
        ("10m/cultural/ne_10m_populated_places.zip", "ne_10m_cities.zip", "Cities"),

        # 50m scale for overview maps
        ("50m/cultural/ne_50m_admin_0_countries.zip", "ne_50m_countries.zip", "Countries (50m)"),
        ("50m/cultural/ne_50m_admin_1_states_provinces.zip", "ne_50m_admin1.zip", "States/Provinces (50m)"),
    ]

    for dataset_path, filename, description in datasets:
        url = f"{base_url}/{dataset_path}"
        zip_path = download_file(url, filename, description)
        extract_zip(zip_path)

def download_spanish_admin_data():
    """Download Spanish administrative boundaries."""
    logger.info("Downloading Spanish administrative data")

    # IGN Spain administrative boundaries
    # This URL provides Spanish provinces and autonomous communities
    urls = [
        {
            "url": "https://www.ign.es/resources/cartografiaEnsenanza/flash/mi_am_esp_e_4_divisiones_admin/divisiones_administrativas.zip",
            "filename": "spain_admin.zip",
            "description": "Spanish administrative divisions"
        }
    ]

    for item in urls:
        try:
            zip_path = download_file(item["url"], item["filename"], item["description"])
            extract_zip(zip_path)
        except Exception as e:
            logger.warning(f"Failed to download {item['description']}: {e}")
            logger.info("Will use alternative data sources")

def download_osm_data():
    """Download OpenStreetMap data for Spain and Asturias."""
    logger.info("Downloading OpenStreetMap data")

    # Using Geofabrik for OSM data
    base_url = "https://download.geofabrik.de"

    datasets = [
        ("europe/spain-latest.osm.pbf", "spain.osm.pbf", "Spain OSM data"),
        ("europe/spain/asturias-latest.osm.pbf", "asturias.osm.pbf", "Asturias OSM data"),
    ]

    for dataset_path, filename, description in datasets:
        url = f"{base_url}/{dataset_path}"
        try:
            download_file(url, filename, description)
        except Exception as e:
            logger.warning(f"Failed to download {description}: {e}")

def create_asturias_boundaries():
    """Create Asturias administrative boundaries from available data."""
    logger.info("Creating Asturias administrative boundaries")

    # This is a simplified version - in practice you'd use official IGN data
    # For now, we'll create a placeholder that can be replaced with official data

    # Asturias approximate boundaries (simplified)
    asturias_coords = [
        [-7.2, 43.8], [-6.0, 43.8], [-4.5, 43.6], [-4.0, 43.0],
        [-5.0, 42.8], [-6.5, 42.9], [-7.2, 43.2], [-7.2, 43.8]
    ]

    # Create a simple polygon for Asturias
    from shapely.geometry import Polygon
    import pandas as pd

    asturias_polygon = Polygon(asturias_coords)

    gdf = gpd.GeoDataFrame({
        'name': ['Asturias'],
        'name_es': ['Asturias'],
        'name_ast': ['Asturies'],
        'type': ['autonomous_community']
    }, geometry=[asturias_polygon], crs='EPSG:4326')

    output_path = PROCESSED_DIR / "asturias_boundary.geojson"
    gdf.to_file(output_path, driver='GeoJSON')
    logger.info(f"Created Asturias boundary file: {output_path}")

def create_gijon_boundaries():
    """Create Gijón city boundaries and districts."""
    logger.info("Creating Gijón boundaries")

    # Gijón approximate center and boundary
    gijon_center = [-5.6615, 43.5322]

    # Simple bounding box for Gijón (this would be replaced with official data)
    from shapely.geometry import box
    import pandas as pd

    # Approximate bounding box for Gijón
    bbox = box(-5.75, 43.45, -5.55, 43.60)

    gdf = gpd.GeoDataFrame({
        'name': ['Gijón'],
        'name_es': ['Gijón'],
        'name_ast': ['Xixón'],
        'type': ['municipality'],
        'population': [273422]  # Approximate
    }, geometry=[bbox], crs='EPSG:4326')

    output_path = PROCESSED_DIR / "gijon_boundary.geojson"
    gdf.to_file(output_path, driver='GeoJSON')
    logger.info(f"Created Gijón boundary file: {output_path}")

@click.command()
@click.option('--skip-osm', is_flag=True, help='Skip OSM data download (large files)')
@click.option('--spain-only', is_flag=True, help='Download only Spain-related data')
def main(skip_osm, spain_only):
    """Download all required geodata for the Wall TV Maps project."""

    logger.info("Starting data download")

    try:
        if not spain_only:
            download_natural_earth_data()

        download_spanish_admin_data()

        if not skip_osm:
            download_osm_data()

        # Create basic boundaries for local areas
        create_asturias_boundaries()
        create_gijon_boundaries()

        logger.info("Data download complete!")
        logger.info(f"Raw data stored in: {RAW_DIR}")
        logger.info(f"Processed data stored in: {PROCESSED_DIR}")

    except Exception as e:
        logger.error(f"Error during data download: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
