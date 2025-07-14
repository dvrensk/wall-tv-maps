#!/usr/bin/env python3
"""
Utility script to find good bounding boxes for map regions.
Helps determine appropriate bounds for mainland areas, excluding islands.
"""

import click
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path("data")

def load_spain_data():
    """Load Spain country and administrative data."""
    countries_file = DATA_DIR / "raw" / "ne_10m_admin_0_countries.shp"
    provinces_file = DATA_DIR / "raw" / "ne_10m_admin_1_states_provinces.shp"
    
    # Load Spain country boundary
    countries = gpd.read_file(countries_file)
    spain_country = countries[countries['NAME'] == 'Spain'].copy()
    
    # Load Spanish provinces/regions  
    provinces = gpd.read_file(provinces_file)
    spain_provinces = provinces[provinces['admin'] == 'Spain'].copy()
    
    # Convert to Web Mercator (EPSG:3857) for proper distance calculations
    spain_country = spain_country.to_crs('EPSG:3857')
    spain_provinces = spain_provinces.to_crs('EPSG:3857')
    
    return spain_country, spain_provinces

def analyze_bounds(gdf, name):
    """Analyze and print bounds information for a geodataframe."""
    if gdf.empty:
        print(f"\n=== {name} ===")
        print("No data found!")
        return None
        
    bounds = gdf.total_bounds
    minx, miny, maxx, maxy = bounds
    
    width = maxx - minx
    height = maxy - miny
    center_x = (minx + maxx) / 2
    center_y = (miny + maxy) / 2
    
    print(f"\n=== {name} ===")
    print(f"Bounds: [{minx:.0f}, {miny:.0f}, {maxx:.0f}, {maxy:.0f}]")
    print(f"Width: {width:.0f}m, Height: {height:.0f}m")
    print(f"Center: [{center_x:.0f}, {center_y:.0f}]")
    print(f"Aspect ratio: {width/height:.2f}")
    
    # Suggest padded bounds
    padding = 0.05
    padded_minx = minx - width * padding
    padded_miny = miny - height * padding
    padded_maxx = maxx + width * padding
    padded_maxy = maxy + height * padding
    
    print(f"Suggested bounds (5% padding):")
    print(f"  west: {padded_minx:.0f}")
    print(f"  east: {padded_maxx:.0f}")
    print(f"  south: {padded_miny:.0f}")
    print(f"  north: {padded_maxy:.0f}")
    
    return bounds

def filter_mainland_spain(gdf):
    """Filter Spanish regions to exclude Canary Islands and other distant territories."""
    if gdf.empty:
        return gdf
        
    # Get centroids for filtering
    centroids = gdf.geometry.centroid
    
    # In Web Mercator, mainland Spain (including Balearics) is roughly:
    # West: -1,100,000 (western Portugal) to East: 450,000 (eastern Spain)
    # South: 4,200,000 (southern Spain) to North: 5,500,000 (northern Spain)
    # Canary Islands are around: west: -2,000,000, south: 3,200,000
    
    mainland_mask = (
        (centroids.x > -1200000) &  # Exclude Canary Islands (far west)
        (centroids.x < 500000) &    # Eastern Spain boundary
        (centroids.y > 4100000)     # Exclude Canary Islands (far south)
    )
    
    mainland = gdf[mainland_mask].copy()
    excluded = gdf[~mainland_mask].copy()
    
    print(f"\nFiltering results:")
    print(f"Total regions: {len(gdf)}")
    print(f"Mainland regions: {len(mainland)}")
    print(f"Excluded regions: {len(excluded)}")
    
    if len(excluded) > 0:
        print("Excluded regions:")
        for idx, row in excluded.iterrows():
            if 'name' in row:
                print(f"  - {row['name']}")
            elif 'NAME' in row:
                print(f"  - {row['NAME']}")
    
    return mainland

def visualize_bounds(spain_country, spain_provinces, mainland_provinces):
    """Create a visualization showing the bounds."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Full Spain (including islands)
    spain_country.plot(ax=ax1, color='lightblue', edgecolor='black', alpha=0.7)
    spain_provinces.plot(ax=ax1, color='lightgreen', edgecolor='gray', alpha=0.5)
    ax1.set_title('Full Spain (including islands)')
    ax1.set_aspect('equal')
    
    # Plot 2: Mainland Spain only
    if not mainland_provinces.empty:
        mainland_provinces.plot(ax=ax2, color='lightgreen', edgecolor='gray', alpha=0.7)
    ax2.set_title('Mainland Spain (filtered)')
    ax2.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('output/spain_bounds_comparison.png', dpi=150, bbox_inches='tight')
    print(f"\nSaved visualization to: output/spain_bounds_comparison.png")

@click.command()
@click.option('--country', default='spain', help='Country to analyze (currently only spain supported)')
@click.option('--visualize', is_flag=True, help='Create visualization of bounds')
@click.option('--mainland-only', is_flag=True, help='Filter to mainland areas only')
def main(country, visualize, mainland_only):
    """Find good bounding boxes for map regions."""
    
    if country.lower() == 'spain':
        print("Analyzing Spain geodata...")
        
        try:
            spain_country, spain_provinces = load_spain_data()
            
            # Analyze full Spain
            analyze_bounds(spain_country, "Full Spain (all territories)")
            analyze_bounds(spain_provinces, "All Spanish Provinces/Regions")
            
            if mainland_only:
                print("\n" + "="*50)
                print("MAINLAND SPAIN ANALYSIS")
                print("="*50)
                
                mainland_provinces = filter_mainland_spain(spain_provinces)
                mainland_bounds = analyze_bounds(mainland_provinces, "Mainland Spain Provinces (excluding islands)")
                
                # Also filter country boundary
                mainland_country = filter_mainland_spain(spain_country)
                analyze_bounds(mainland_country, "Mainland Spain Country Boundary")
                
                if visualize:
                    visualize_bounds(spain_country, spain_provinces, mainland_provinces)
                
                # Provide specific recommendations
                if mainland_bounds is not None:
                    minx, miny, maxx, maxy = mainland_bounds
                    padding = 0.03  # 3% padding for mainland
                    width = maxx - minx
                    height = maxy - miny
                    
                    west = int(minx - width * padding)
                    east = int(maxx + width * padding)
                    south = int(miny - height * padding)
                    north = int(maxy + height * padding)
                    
                    print(f"\n" + "="*50)
                    print("RECOMMENDED CONFIG FOR MAINLAND SPAIN:")
                    print("="*50)
                    print(f"bounds:")
                    print(f"  west: {west}")
                    print(f"  east: {east}")
                    print(f"  south: {south}")
                    print(f"  north: {north}")
                    print(f"\n# This excludes Canary Islands but includes Balearic Islands")
                    print(f"# Aspect ratio: {width/height:.2f} (good for 16:9 displays)")
            
        except FileNotFoundError as e:
            logger.error(f"Data file not found: {e}")
            logger.error("Make sure you've run 'make download-data' first")
            
    else:
        print(f"Country '{country}' not supported yet. Currently supports: spain")

if __name__ == '__main__':
    main() 