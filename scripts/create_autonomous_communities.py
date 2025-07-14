#!/usr/bin/env python3
"""
Create autonomous communities data by dissolving province boundaries.
This generates proper region-level boundaries for Spain's 17+2 autonomous communities.
"""

import click
import geopandas as gpd
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

def create_autonomous_communities():
    """Create autonomous communities by dissolving province boundaries."""
    
    # Load Spanish provinces data
    provinces_file = RAW_DIR / "ne_10m_admin_1_states_provinces.shp"
    logger.info(f"Loading provinces from: {provinces_file}")
    
    gdf = gpd.read_file(provinces_file)
    spain_provinces = gdf[gdf['admin'] == 'Spain'].copy()
    
    logger.info(f"Found {len(spain_provinces)} Spanish provinces")
    
    # Show the regions we'll be dissolving
    regions = spain_provinces['region'].value_counts().sort_index()
    logger.info(f"Will create {len(regions)} autonomous communities:")
    for region, count in regions.items():
        logger.info(f"  {region}: {count} provinces")
    
    # Dissolve by region to create autonomous communities
    logger.info("Dissolving province boundaries by autonomous community...")
    autonomous_communities = spain_provinces.dissolve(
        by='region', 
        aggfunc={
            'name': 'first',           # Keep first province name as reference
            'region_cod': 'first',     # Keep region code
            'admin': 'first',          # Keep admin (Spain)
            'type_en': 'first',        # Keep type
            'area_sqkm': 'sum',        # Sum the areas
            'name_es': 'first'         # Keep Spanish name if available
        }
    ).reset_index()
    
    # Clean up the data
    autonomous_communities['name'] = autonomous_communities['region']  # Use region name as the primary name
    autonomous_communities['type_en'] = 'Autonomous Community'        # Standardize type
    
    # Manual corrections for special cases
    autonomous_communities.loc[autonomous_communities['region'] == 'Ceuta', 'type_en'] = 'Autonomous City'
    autonomous_communities.loc[autonomous_communities['region'] == 'Melilla', 'type_en'] = 'Autonomous City'
    
    # Reorder columns
    column_order = ['region', 'name', 'region_cod', 'type_en', 'admin', 'area_sqkm', 'geometry']
    autonomous_communities = autonomous_communities[[col for col in column_order if col in autonomous_communities.columns]]
    
    logger.info(f"Created {len(autonomous_communities)} autonomous communities")
    
    # Show what we created
    print("\n=== Created Autonomous Communities ===")
    for idx, row in autonomous_communities.iterrows():
        area_km2 = row['area_sqkm'] if 'area_sqkm' in row else 'N/A'
        print(f"{row['region']}: {area_km2:.0f} km²" if area_km2 != 'N/A' else f"{row['region']}")
    
    # Save the result
    output_file = PROCESSED_DIR / "spain_autonomous_communities.geojson"
    PROCESSED_DIR.mkdir(exist_ok=True)
    
    autonomous_communities.to_file(output_file, driver='GeoJSON')
    logger.info(f"Saved autonomous communities to: {output_file}")
    
    return autonomous_communities

def filter_mainland_communities(gdf):
    """Filter to mainland autonomous communities (exclude Canary Islands)."""
    # Convert to Web Mercator for filtering
    gdf_mercator = gdf.to_crs('EPSG:3857')
    centroids = gdf_mercator.geometry.centroid
    
    # Filter out Canary Islands
    mainland_mask = (
        (centroids.x > -1200000) &  # Exclude Canary Islands (far west)
        (centroids.y > 4100000)     # Exclude Canary Islands (far south)
    )
    
    mainland = gdf[mainland_mask].copy()
    excluded = gdf[~mainland_mask].copy()
    
    logger.info(f"Mainland communities: {len(mainland)}")
    logger.info(f"Excluded (islands): {len(excluded)}")
    
    if len(excluded) > 0:
        logger.info("Excluded communities:")
        for idx, row in excluded.iterrows():
            logger.info(f"  - {row['region']}")
    
    # Save mainland version
    output_file = PROCESSED_DIR / "mainland_spain_autonomous_communities.geojson"
    mainland.to_file(output_file, driver='GeoJSON')
    logger.info(f"Saved mainland communities to: {output_file}")
    
    return mainland

@click.command()
@click.option('--mainland-only', is_flag=True, help='Also create mainland-only version')
def main(mainland_only):
    """Create autonomous communities by dissolving Spanish provinces."""
    
    try:
        # Create full autonomous communities
        communities = create_autonomous_communities()
        
        if mainland_only:
            # Also create mainland-only version
            logger.info("\nCreating mainland-only version...")
            filter_mainland_communities(communities)
        
        print(f"\n✅ Success! Created autonomous communities data.")
        print(f"Now you can update your regions config to use:")
        print(f"  file: \"processed/spain_autonomous_communities.geojson\"")
        if mainland_only:
            print(f"Or for mainland only:")
            print(f"  file: \"processed/mainland_spain_autonomous_communities.geojson\"")
        
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        logger.error("Make sure you've run 'make download-data' first")

if __name__ == '__main__':
    main() 