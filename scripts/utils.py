#!/usr/bin/env python3
"""
Utility functions for Wall TV Maps project.
"""

import logging
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon, box
import requests
import yaml

logger = logging.getLogger(__name__)

def load_config(config_file):
    """Load configuration from YAML file."""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def get_spain_bounds():
    """Get bounds for Spain in Web Mercator coordinates."""
    return {
        'west': -1100000,
        'east': 500000,
        'south': 4200000,
        'north': 5500000
    }

def get_asturias_bounds():
    """Get bounds for Asturias region."""
    return {
        'west': -800000,
        'east': -500000,
        'south': 4800000,
        'north': 4950000
    }

def get_gijon_bounds():
    """Get bounds for Gijón city."""
    return {
        'west': -635000,
        'east': -580000,
        'south': 4885000,
        'north': 4910000
    }

def create_spain_regions_data():
    """Create Spanish regions data with proper names."""
    regions_data = {
        'Galicia': {
            'coords': [[-9.5, 42.0], [-6.5, 42.0], [-6.5, 43.8], [-9.5, 43.8], [-9.5, 42.0]],
            'capital': 'Santiago de Compostela',
            'population': 2701743
        },
        'Asturias': {
            'coords': [[-7.2, 43.0], [-4.5, 43.0], [-4.5, 43.8], [-7.2, 43.8], [-7.2, 43.0]],
            'capital': 'Oviedo',
            'population': 1018784
        },
        'Cantabria': {
            'coords': [[-5.0, 43.0], [-3.0, 43.0], [-3.0, 43.8], [-5.0, 43.8], [-5.0, 43.0]],
            'capital': 'Santander',
            'population': 582905
        },
        'País Vasco': {
            'coords': [[-3.5, 43.0], [-1.5, 43.0], [-1.5, 43.8], [-3.5, 43.8], [-3.5, 43.0]],
            'capital': 'Vitoria-Gasteiz',
            'population': 2207776
        },
        'Navarra': {
            'coords': [[-2.5, 42.0], [-0.5, 42.0], [-0.5, 43.5], [-2.5, 43.5], [-2.5, 42.0]],
            'capital': 'Pamplona',
            'population': 661197
        },
        'La Rioja': {
            'coords': [[-3.0, 42.0], [-1.5, 42.0], [-1.5, 43.0], [-3.0, 43.0], [-3.0, 42.0]],
            'capital': 'Logroño',
            'population': 319914
        },
        'Aragón': {
            'coords': [[-2.0, 40.0], [1.0, 40.0], [1.0, 43.0], [-2.0, 43.0], [-2.0, 40.0]],
            'capital': 'Zaragoza',
            'population': 1329391
        },
        'Cataluña': {
            'coords': [[0.0, 40.5], [3.5, 40.5], [3.5, 42.8], [0.0, 42.8], [0.0, 40.5]],
            'capital': 'Barcelona',
            'population': 7675217
        },
        'Castilla y León': {
            'coords': [[-7.0, 40.0], [-2.0, 40.0], [-2.0, 43.0], [-7.0, 43.0], [-7.0, 40.0]],
            'capital': 'Valladolid',
            'population': 2383139
        },
        'Madrid': {
            'coords': [[-4.5, 40.0], [-3.0, 40.0], [-3.0, 41.0], [-4.5, 41.0], [-4.5, 40.0]],
            'capital': 'Madrid',
            'population': 6663394
        },
        'Castilla-La Mancha': {
            'coords': [[-5.5, 38.0], [-1.0, 38.0], [-1.0, 41.0], [-5.5, 41.0], [-5.5, 38.0]],
            'capital': 'Toledo',
            'population': 2045221
        },
        'Comunidad Valenciana': {
            'coords': [[-1.5, 38.0], [1.0, 38.0], [1.0, 41.0], [-1.5, 41.0], [-1.5, 38.0]],
            'capital': 'Valencia',
            'population': 5003769
        },
        'Extremadura': {
            'coords': [[-7.5, 38.0], [-4.5, 38.0], [-4.5, 41.0], [-7.5, 41.0], [-7.5, 38.0]],
            'capital': 'Mérida',
            'population': 1067710
        },
        'Andalucía': {
            'coords': [[-7.5, 36.0], [-1.5, 36.0], [-1.5, 39.0], [-7.5, 39.0], [-7.5, 36.0]],
            'capital': 'Sevilla',
            'population': 8472407
        },
        'Murcia': {
            'coords': [[-2.5, 37.0], [-0.5, 37.0], [-0.5, 39.0], [-2.5, 39.0], [-2.5, 37.0]],
            'capital': 'Murcia',
            'population': 1511251
        },
        'Islas Baleares': {
            'coords': [[1.0, 38.5], [4.5, 38.5], [4.5, 40.5], [1.0, 40.5], [1.0, 38.5]],
            'capital': 'Palma',
            'population': 1173008
        },
        'Canarias': {
            'coords': [[-18.5, 27.0], [-13.0, 27.0], [-13.0, 29.5], [-18.5, 29.5], [-18.5, 27.0]],
            'capital': 'Las Palmas / Santa Cruz',
            'population': 2172944
        }
    }

    return regions_data

def validate_coordinates(coords):
    """Validate coordinate bounds."""
    if not coords or len(coords) != 4:
        return False

    west, south, east, north = coords

    # Basic validation
    if west >= east or south >= north:
        return False

    # Reasonable bounds for Spain area
    if west < -20 or east > 5 or south < 27 or north > 45:
        return False

    return True

def degrees_to_web_mercator(lon, lat):
    """Convert degrees to Web Mercator coordinates."""
    import math

    x = lon * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y = y * 20037508.34 / 180

    return x, y

def web_mercator_to_degrees(x, y):
    """Convert Web Mercator coordinates to degrees."""
    import math

    lon = x * 180 / 20037508.34
    lat = math.atan(math.exp(y * math.pi / 20037508.34)) * 360 / math.pi - 90

    return lon, lat

def get_optimal_font_size(text, max_width, max_height):
    """Calculate optimal font size for given text and space."""
    # Simple heuristic - in practice you'd measure text with actual fonts
    char_width_ratio = 0.6  # Approximate character width to height ratio

    # Calculate based on width
    width_font_size = max_width / (len(text) * char_width_ratio)

    # Calculate based on height
    height_font_size = max_height

    # Use the smaller one
    return min(width_font_size, height_font_size)

def create_color_palette(theme='default'):
    """Create color palettes for different map themes."""
    palettes = {
        'default': {
            'land': '#e6f3e6',
            'water': '#e6f3ff',
            'borders': '#333333',
            'cities': '#ff4444',
            'text': 'white',
            'background': '#f0f8ff'
        },
        'dark': {
            'land': '#2d3e2d',
            'water': '#1a2a3a',
            'borders': '#cccccc',
            'cities': '#ff6666',
            'text': 'white',
            'background': '#1a1a1a'
        },
        'high_contrast': {
            'land': '#ffffff',
            'water': '#000000',
            'borders': '#000000',
            'cities': '#ff0000',
            'text': 'black',
            'background': '#ffffff'
        }
    }

    return palettes.get(theme, palettes['default'])

def ensure_directory(path):
    """Ensure directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)

def get_file_size_mb(file_path):
    """Get file size in MB."""
    return Path(file_path).stat().st_size / (1024 * 1024)

def log_system_info():
    """Log system information for debugging."""
    import platform
    import psutil

    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Operating system: {platform.system()} {platform.release()}")
    logger.info(f"Available memory: {psutil.virtual_memory().available / (1024**3):.1f} GB")
    logger.info(f"Available disk space: {psutil.disk_usage('.').free / (1024**3):.1f} GB")
