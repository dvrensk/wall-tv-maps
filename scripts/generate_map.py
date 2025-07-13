#!/usr/bin/env python3
"""
Generate maps for Wall TV Maps project.
Takes YAML configuration files and produces high-resolution PNG maps.
"""

import os
import sys
import yaml
import click
import logging
from pathlib import Path
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import patheffects
import numpy as np
from shapely.geometry import Point, Polygon
import contextily as ctx
from PIL import Image, ImageDraw, ImageFont
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Directories
DATA_DIR = Path("data")
CONFIG_DIR = Path("config")
OUTPUT_DIR = Path("output")
QGIS_DIR = Path("qgis")

# Output specifications
OUTPUT_WIDTH = 4000
OUTPUT_HEIGHT = 2250
DPI = 300

class MapGenerator:
    """Main class for generating maps."""

    def __init__(self, config_file):
        """Initialize with configuration file."""
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.output_file = OUTPUT_DIR / f"{self.config['name']}.png"

        # Create output directory
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def load_config(self):
        """Load configuration from YAML file."""
        logger.info(f"Loading configuration from {self.config_file}")

        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return config

    def load_data(self):
        """Load geodata based on configuration."""
        logger.info("Loading geodata")

        self.data = {}

        for layer_name, layer_config in self.config['layers'].items():
            try:
                file_path = Path(layer_config['file'])
                if not file_path.is_absolute():
                    file_path = DATA_DIR / file_path

                logger.info(f"Loading layer: {layer_name} from {file_path}")

                if file_path.suffix.lower() == '.geojson':
                    gdf = gpd.read_file(file_path)
                elif file_path.suffix.lower() in ['.shp', '.gpkg']:
                    gdf = gpd.read_file(file_path)
                else:
                    logger.warning(f"Unsupported file format: {file_path}")
                    continue

                # Apply filters if specified
                if 'filter' in layer_config:
                    filter_expr = layer_config['filter']
                    gdf = gdf.query(filter_expr)
                    logger.info(f"Applied filter: {filter_expr}")

                # Reproject to Web Mercator for visualization
                if gdf.crs != 'EPSG:3857':
                    gdf = gdf.to_crs('EPSG:3857')

                self.data[layer_name] = gdf

            except Exception as e:
                logger.error(f"Error loading layer {layer_name}: {e}")
                continue

    def setup_map(self):
        """Set up the matplotlib figure and axis."""
        logger.info("Setting up map canvas")

        # Calculate figure size based on output dimensions
        fig_width = OUTPUT_WIDTH / DPI
        fig_height = OUTPUT_HEIGHT / DPI

        self.fig, self.ax = plt.subplots(
            figsize=(fig_width, fig_height),
            dpi=DPI,
            facecolor=self.config.get('background_color', 'white')
        )

        # Remove axes and margins
        self.ax.set_axis_off()
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

        # Set bounds if specified
        if 'bounds' in self.config:
            bounds = self.config['bounds']
            self.ax.set_xlim(bounds['west'], bounds['east'])
            self.ax.set_ylim(bounds['south'], bounds['north'])
        else:
            # Calculate bounds from data
            self.calculate_bounds()

    def calculate_bounds(self):
        """Calculate map bounds from loaded data."""
        logger.info("Calculating map bounds")

        all_bounds = []

        for layer_name, gdf in self.data.items():
            if not gdf.empty:
                bounds = gdf.total_bounds
                all_bounds.append(bounds)

        if all_bounds:
            # Find overall bounds
            min_x = min(bounds[0] for bounds in all_bounds)
            min_y = min(bounds[1] for bounds in all_bounds)
            max_x = max(bounds[2] for bounds in all_bounds)
            max_y = max(bounds[3] for bounds in all_bounds)

            # Add padding
            padding = 0.05  # 5% padding
            width = max_x - min_x
            height = max_y - min_y

            self.ax.set_xlim(min_x - width * padding, max_x + width * padding)
            self.ax.set_ylim(min_y - height * padding, max_y + height * padding)

    def render_layers(self):
        """Render all map layers."""
        logger.info("Rendering map layers")

        for layer_name, layer_config in self.config['layers'].items():
            if layer_name not in self.data:
                continue

            gdf = self.data[layer_name]
            if gdf.empty:
                continue

            logger.info(f"Rendering layer: {layer_name}")

            # Get styling options
            style = layer_config.get('style', {})

            # Plot the layer
            gdf.plot(
                ax=self.ax,
                color=style.get('fill_color', 'lightblue'),
                edgecolor=style.get('stroke_color', 'black'),
                linewidth=style.get('stroke_width', 1),
                alpha=style.get('opacity', 1.0),
                zorder=style.get('zorder', 1)
            )

    def add_labels(self):
        """Add labels to the map."""
        logger.info("Adding labels")

        for layer_name, layer_config in self.config['layers'].items():
            if layer_name not in self.data:
                continue

            if 'labels' not in layer_config:
                continue

            gdf = self.data[layer_name]
            if gdf.empty:
                continue

            label_config = layer_config['labels']

            # Get label field
            label_field = label_config.get('field', 'name')
            if label_field not in gdf.columns:
                logger.warning(f"Label field '{label_field}' not found in {layer_name}")
                continue

            # Font settings
            font_size = label_config.get('font_size', 12)
            font_color = label_config.get('font_color', 'black')
            font_weight = label_config.get('font_weight', 'normal')

            # Add labels
            for idx, row in gdf.iterrows():
                if pd.isna(row[label_field]):
                    continue

                # Get label position
                if row.geometry.geom_type == 'Point':
                    x, y = row.geometry.x, row.geometry.y
                else:
                    # Use centroid for polygons/lines
                    centroid = row.geometry.centroid
                    x, y = centroid.x, centroid.y

                # Add text with outline for better visibility
                text = self.ax.text(
                    x, y, row[label_field],
                    fontsize=font_size,
                    color=font_color,
                    weight=font_weight,
                    ha='center',
                    va='center',
                    zorder=10
                )

                # Add outline effect
                text.set_path_effects([
                    patheffects.withStroke(linewidth=3, foreground='white')
                ])

    def add_basemap(self):
        """Add a basemap if specified."""
        if 'basemap' in self.config:
            basemap_config = self.config['basemap']

            try:
                logger.info(f"Adding basemap: {basemap_config['source']}")

                # Add contextily basemap
                ctx.add_basemap(
                    self.ax,
                    crs=self.data[list(self.data.keys())[0]].crs,
                    source=basemap_config['source'],
                    alpha=basemap_config.get('alpha', 1.0),
                    zoom=basemap_config.get('zoom', 'auto')
                )

            except Exception as e:
                logger.warning(f"Failed to add basemap: {e}")

    def save_map(self):
        """Save the map to file."""
        logger.info(f"Saving map to {self.output_file}")

        # Save with high DPI
        self.fig.savefig(
            self.output_file,
            dpi=DPI,
            bbox_inches='tight',
            pad_inches=0,
            facecolor=self.config.get('background_color', 'white'),
            edgecolor='none'
        )

        # Close the figure to free memory
        plt.close(self.fig)

        logger.info(f"Map saved successfully: {self.output_file}")

    def generate(self):
        """Generate the complete map."""
        logger.info(f"Generating map: {self.config['name']}")

        try:
            self.load_data()
            self.setup_map()
            self.add_basemap()
            self.render_layers()
            self.add_labels()
            self.save_map()

            logger.info(f"Map generation complete: {self.config['name']}")

        except Exception as e:
            logger.error(f"Error generating map: {e}")
            raise

@click.command()
@click.option('--config', '-c', required=True, help='Path to configuration file')
@click.option('--output', '-o', help='Output file path (overrides config)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose logging')
def main(config, output, verbose):
    """Generate a map from configuration file."""

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        generator = MapGenerator(config)

        if output:
            generator.output_file = Path(output)

        generator.generate()

    except Exception as e:
        logger.error(f"Failed to generate map: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
