#!/usr/bin/env python3
"""
Create a processed provinces file containing only mainland Spanish provinces.
This optimizes map generation by avoiding the need to load global province data.
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Directories
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

def create_mainland_spain_provinces():
    """Extract and save mainland Spanish provinces from global dataset."""
    
    # Ensure processed directory exists
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Input and output files
    input_file = RAW_DIR / "ne_10m_admin_1_states_provinces.shp"
    output_file = PROCESSED_DIR / "mainland_spain_provinces.geojson"
    
    logger.info(f"Loading global provinces data from {input_file}")
    
    # Load the global provinces/states data
    world_provinces = gpd.read_file(input_file)
    
    logger.info(f"Loaded {len(world_provinces)} provinces/states worldwide")
    
    # Filter for Spanish provinces only
    spain_provinces = world_provinces[world_provinces['admin'] == 'Spain'].copy()
    
    logger.info(f"Found {len(spain_provinces)} Spanish provinces")
    
    # Filter out Canary Islands to focus on mainland Spain
    # Canary Islands provinces: "Santa Cruz de Tenerife" and "Las Palmas"
    mainland_provinces = spain_provinces[
        ~spain_provinces['name'].isin(['Santa Cruz de Tenerife', 'Las Palmas'])
    ].copy()
    
    logger.info(f"Filtered to {len(mainland_provinces)} mainland Spanish provinces")
    
    # Clean up the data - keep only essential columns
    essential_columns = ['name', 'admin', 'type_en', 'region', 'geometry']
    
    # Check which columns exist
    available_columns = [col for col in essential_columns if col in mainland_provinces.columns]
    mainland_provinces = mainland_provinces[available_columns]
    
    # Sort by name for consistency
    mainland_provinces = mainland_provinces.sort_values('name')
    
    # Save as GeoJSON
    logger.info(f"Saving to {output_file}")
    mainland_provinces.to_file(output_file, driver='GeoJSON')
    
    # Print summary
    logger.info(f"Successfully created mainland Spain provinces file:")
    logger.info(f"  - Input file: {input_file} ({input_file.stat().st_size / 1024 / 1024:.1f} MB)")
    logger.info(f"  - Output file: {output_file} ({output_file.stat().st_size / 1024:.1f} KB)")
    logger.info(f"  - Provinces included: {len(mainland_provinces)}")
    
    # Print province names for verification
    logger.info("Mainland Spanish provinces:")
    for idx, province in mainland_provinces.iterrows():
        logger.info(f"  - {province['name']}")
    
    return mainland_provinces

if __name__ == "__main__":
    create_mainland_spain_provinces() 