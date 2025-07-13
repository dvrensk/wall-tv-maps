#!/usr/bin/env python3
"""
Process geodata for Wall TV Maps project.
Clean, transform, and prepare data for map generation.
"""

import os
import sys
import logging
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
import click

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

def process_spanish_regions():
    """Process Spanish regions data with proper Spanish names."""
    logger.info("Processing Spanish regions data")

    input_path = RAW_DIR / "ne_10m_admin_1_states_provinces" / "ne_10m_admin_1_states_provinces.shp"

    if not input_path.exists():
        logger.warning(f"Spanish regions file not found: {input_path}")
        return

    # Read the data
    gdf = gpd.read_file(input_path)

    # Filter for Spain
    spain_regions = gdf[gdf['admin'] == 'Spain'].copy()

    # Add Spanish names and corrections
    spanish_names = {
        'Galicia': 'Galicia',
        'Asturias': 'Asturias',
        'Cantabria': 'Cantabria',
        'Basque Country': 'País Vasco',
        'Navarre': 'Navarra',
        'La Rioja': 'La Rioja',
        'Aragon': 'Aragón',
        'Catalonia': 'Cataluña',
        'Castile and León': 'Castilla y León',
        'Madrid': 'Madrid',
        'Castile-La Mancha': 'Castilla-La Mancha',
        'Valencian Community': 'Comunidad Valenciana',
        'Extremadura': 'Extremadura',
        'Andalusia': 'Andalucía',
        'Murcia': 'Murcia',
        'Balearic Islands': 'Islas Baleares',
        'Canary Islands': 'Canarias'
    }

    # Add Spanish names
    spain_regions['name_es'] = spain_regions['name'].map(spanish_names)
    spain_regions['name_es'] = spain_regions['name_es'].fillna(spain_regions['name'])

    # Save processed data
    output_path = PROCESSED_DIR / "spain_regions.geojson"
    spain_regions.to_file(output_path, driver='GeoJSON')
    logger.info(f"Processed Spanish regions saved to: {output_path}")

def process_spanish_provinces():
    """Process Spanish provinces data."""
    logger.info("Processing Spanish provinces data")

    # This would process province-level data
    # For now, we'll create a placeholder
    logger.info("Spanish provinces processing - placeholder")

def process_asturias_detailed():
    """Process detailed Asturias data."""
    logger.info("Processing detailed Asturias data")

    # Create detailed Asturias municipalities
    municipalities = {
        'Gijón': {'coords': [[-5.75, 43.45], [-5.55, 43.45], [-5.55, 43.60], [-5.75, 43.60], [-5.75, 43.45]],
                  'name_ast': 'Xixón', 'population': 273422},
        'Oviedo': {'coords': [[-5.90, 43.30], [-5.80, 43.30], [-5.80, 43.40], [-5.90, 43.40], [-5.90, 43.30]],
                   'name_ast': 'Uviéu', 'population': 219686},
        'Avilés': {'coords': [[-5.95, 43.50], [-5.85, 43.50], [-5.85, 43.60], [-5.95, 43.60], [-5.95, 43.50]],
                   'name_ast': 'Avilés', 'population': 77690},
        'Mieres': {'coords': [[-5.80, 43.20], [-5.70, 43.20], [-5.70, 43.30], [-5.80, 43.30], [-5.80, 43.20]],
                   'name_ast': 'Mieres', 'population': 38278},
        'Langreo': {'coords': [[-5.70, 43.20], [-5.60, 43.20], [-5.60, 43.30], [-5.70, 43.30], [-5.70, 43.20]],
                    'name_ast': 'Langreo', 'population': 39392}
    }

    # Create GeoDataFrame
    data = []
    for name, info in municipalities.items():
        polygon = Polygon(info['coords'])
        data.append({
            'name': name,
            'name_es': name,
            'name_ast': info['name_ast'],
            'population': info['population'],
            'type': 'municipality',
            'geometry': polygon
        })

    gdf = gpd.GeoDataFrame(data, crs='EPSG:4326')

    # Save
    output_path = PROCESSED_DIR / "asturias_municipalities.geojson"
    gdf.to_file(output_path, driver='GeoJSON')
    logger.info(f"Processed Asturias municipalities saved to: {output_path}")

def process_gijon_detailed():
    """Process detailed Gijón data with districts."""
    logger.info("Processing detailed Gijón data")

    # Gijón districts/neighborhoods
    districts = {
        'Centro': {'coords': [[-5.67, 43.53], [-5.65, 43.53], [-5.65, 43.55], [-5.67, 43.55], [-5.67, 43.53]]},
        'Cimadevilla': {'coords': [[-5.66, 43.54], [-5.64, 43.54], [-5.64, 43.56], [-5.66, 43.56], [-5.66, 43.54]]},
        'El Llano': {'coords': [[-5.68, 43.52], [-5.66, 43.52], [-5.66, 43.54], [-5.68, 43.54], [-5.68, 43.52]]},
        'Somió': {'coords': [[-5.63, 43.55], [-5.61, 43.55], [-5.61, 43.57], [-5.63, 43.57], [-5.63, 43.55]]},
        'Tremañes': {'coords': [[-5.65, 43.51], [-5.63, 43.51], [-5.63, 43.53], [-5.65, 43.53], [-5.65, 43.51]]},
        'El Natahoyo': {'coords': [[-5.70, 43.54], [-5.68, 43.54], [-5.68, 43.56], [-5.70, 43.56], [-5.70, 43.54]]},
        'Jove': {'coords': [[-5.62, 43.54], [-5.60, 43.54], [-5.60, 43.56], [-5.62, 43.56], [-5.62, 43.54]]},
        'Montevil': {'coords': [[-5.72, 43.52], [-5.70, 43.52], [-5.70, 43.54], [-5.72, 43.54], [-5.72, 43.52]]},
        'Contrueces': {'coords': [[-5.72, 43.50], [-5.70, 43.50], [-5.70, 43.52], [-5.72, 43.52], [-5.72, 43.50]]},
        'Pumarín': {'coords': [[-5.74, 43.53], [-5.72, 43.53], [-5.72, 43.55], [-5.74, 43.55], [-5.74, 43.53]]}
    }

    # Create GeoDataFrame
    data = []
    for name, info in districts.items():
        polygon = Polygon(info['coords'])
        data.append({
            'name': name,
            'name_es': name,
            'type': 'district',
            'geometry': polygon
        })

    gdf = gpd.GeoDataFrame(data, crs='EPSG:4326')

    # Save
    output_path = PROCESSED_DIR / "gijon_districts.geojson"
    gdf.to_file(output_path, driver='GeoJSON')
    logger.info(f"Processed Gijón districts saved to: {output_path}")

def create_placeholder_files():
    """Create placeholder files to ensure directories exist."""
    directories = [DATA_DIR, RAW_DIR, PROCESSED_DIR]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        gitkeep = directory / ".gitkeep"
        gitkeep.touch()

@click.command()
@click.option('--all', 'process_all', is_flag=True, help='Process all data')
@click.option('--regions', is_flag=True, help='Process Spanish regions')
@click.option('--provinces', is_flag=True, help='Process Spanish provinces')
@click.option('--asturias', is_flag=True, help='Process Asturias data')
@click.option('--gijon', is_flag=True, help='Process Gijón data')
def main(process_all, regions, provinces, asturias, gijon):
    """Process geodata for the Wall TV Maps project."""

    logger.info("Starting data processing")

    # Ensure directories exist
    create_placeholder_files()

    try:
        if process_all or regions:
            process_spanish_regions()

        if process_all or provinces:
            process_spanish_provinces()

        if process_all or asturias:
            process_asturias_detailed()

        if process_all or gijon:
            process_gijon_detailed()

        if not any([process_all, regions, provinces, asturias, gijon]):
            logger.info("No processing options specified. Use --help for options.")
            return

        logger.info("Data processing complete!")

    except Exception as e:
        logger.error(f"Error during data processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
