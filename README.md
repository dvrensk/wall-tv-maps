# Wall TV Maps Project

A system for generating high-quality non-interactive maps for wall display TV.

## Overview

This project creates 4000x2250px maps for display on a 55" wall-mounted TV, optimized for readability from 5 meters away. Maps cover multiple scales from local (Gijón/Somió) to national (Spain) and potentially European levels.

## Features

- **Multi-scale mapping**: City, county, region, country, and Europe
- **Selective labeling**: Choose specific features to label (rivers, counties, etc.)
- **Spanish localization**: Custom Spanish labels with regional variants
- **High-resolution output**: 4000x2250px PNG optimized for large displays
- **Interactive design**: QGIS integration for label positioning
- **Reproducible builds**: Docker + Make for consistent environments

## Quick Start

```bash
# Build the Docker environment
make setup

# Download base data
make download-data

# Generate all maps
make all-maps

# Or generate specific maps
make map-gijon
make map-asturias
make map-spain-regions
```

## Project Structure

```
├── data/               # Raw geodata (gitignored)
├── scripts/           # Python data processing scripts
├── qgis/              # QGIS project files
├── config/            # Map configuration files
├── output/            # Generated maps (gitignored)
├── docker/            # Docker configuration
└── Makefile          # Build automation
```

## Requirements

- Docker and Docker Compose
- Make
- ~10GB disk space for geodata

## Maps Planned

### Local Scale
- **Gijón Districts**: City districts with major roads and landmarks
- **Gijón Parks**: Parks, beaches, and recreational areas
- **Gijón POIs**: Points of interest and transportation

### Regional Scale
- **Asturias Comarcas**: Administrative divisions
- **Asturias Geography**: Mountains, rivers, coastal features
- **Asturias Cities**: Major municipalities

### National Scale
- **Spain Regions**: 17 autonomous communities
- **Spain Provinces**: 50 provinces
- **Spain Geography**: Major rivers, mountain ranges

### European Scale
- **Western Europe**: Countries with major cities
- **Iberian Peninsula**: Spain and Portugal detailed

## Data Sources

- **OpenStreetMap**: Street data, buildings, POIs
- **Natural Earth**: Administrative boundaries, physical features
- **IGN España**: Official Spanish geographic data
- **EU Administrative Units**: European boundaries

## Technology Stack

- **Python**: Data processing with GeoPandas, Shapely
- **QGIS**: Interactive map design and label positioning
- **PostGIS**: Spatial database for data management
- **Docker**: Reproducible environment
- **Make**: Build automation
