# Getting Started with Wall TV Maps

This guide will help you get up and running with the Wall TV Maps project.

## Prerequisites

- **Docker and Docker Compose** - For running the containerized environment
- **Make** - For running build commands
- **~10GB free disk space** - For geodata storage
- **Internet connection** - For downloading geodata

## Quick Start

### 1. Set up the environment

```bash
# Build and start the Docker environment
make setup
```

This will:
- Build the Docker image with all required GIS tools
- Start the PostGIS database
- Set up the project structure

### 2. Download geodata

```bash
# Download all required geodata (this will take a while)
make download-data

# Or download Spain-only data to get started faster
make download-data ARGS="--spain-only"
```

### 3. Process the data

```bash
# Process raw data into usable formats
make process-data
```

### 4. Generate your first map

```bash
# Generate a Spanish regions map
make map-spain
```

This will create a high-resolution PNG in the `output/` directory.

## Understanding the Project Structure

```
wall-tv-maps/
├── config/              # Map configuration files (YAML)
├── data/               # Geodata (gitignored)
│   ├── raw/           # Downloaded raw data
│   └── processed/     # Processed data ready for mapping
├── docker/            # Docker configuration
├── output/            # Generated maps (gitignored)
├── qgis/              # QGIS project files
├── scripts/           # Python scripts
└── Makefile          # Build automation
```

## Configuration Files

Maps are defined using YAML configuration files in the `config/` directory. Each file specifies:

- **Data layers** - What geodata to use
- **Styling** - Colors, line weights, fonts
- **Labels** - What text to display and where
- **Bounds** - Geographic area to show

### Example Configuration

```yaml
name: "my_map"
title: "My Custom Map"
description: "A sample map configuration"

# Map bounds (Web Mercator coordinates)
bounds:
  west: -1100000
  east: 500000
  south: 4200000
  north: 5500000

# Data layers
layers:
  regions:
    file: "processed/spain_regions.geojson"
    style:
      fill_color: "#e6f3e6"
      stroke_color: "#333333"
      stroke_width: 2
    labels:
      field: "name_es"
      font_size: 36
      font_color: "white"
      font_weight: "bold"
```

## Available Maps

The project includes several pre-configured maps:

### National Scale
- `spain_regions.yaml` - 17 autonomous communities
- `spain_provinces.yaml` - 50 provinces
- `spain_geography.yaml` - Physical features

### Regional Scale (Asturias)
- `asturias_comarcas.yaml` - Administrative divisions
- `asturias_geography.yaml` - Mountains, rivers, coast
- `asturias_cities.yaml` - Major municipalities

### Local Scale (Gijón)
- `gijon_districts.yaml` - City districts and neighborhoods
- `gijon_parks.yaml` - Parks and recreational areas
- `gijon_pois.yaml` - Points of interest

### European Scale
- `europe_west.yaml` - Western European countries
- `iberian_peninsula.yaml` - Spain and Portugal

## Customizing Maps

### 1. Modify Existing Configurations

Edit any `.yaml` file in the `config/` directory to:
- Change colors and styling
- Adjust label positions
- Select different data layers
- Modify geographic bounds

### 2. Create New Maps

Copy an existing configuration file and modify it:

```bash
cp config/spain_regions.yaml config/my_custom_map.yaml
# Edit the new file
# Generate the map
python scripts/generate_map.py --config config/my_custom_map.yaml
```

### 3. Add Custom Data

1. Place your geodata files in `data/processed/`
2. Reference them in your configuration
3. Generate the map

## Interactive Design with QGIS

For advanced label positioning and styling:

```bash
# Launch QGIS
make qgis
```

QGIS allows you to:
- Visually position labels
- Fine-tune styling
- Add custom symbols
- Create print layouts

## Troubleshooting

### Common Issues

**"No module named 'geopandas'"**
- Make sure you're running commands through `make` (which uses Docker)
- Try rebuilding: `make clean-all && make setup`

**"File not found" errors**
- Ensure you've run `make download-data` first
- Check that data files exist in `data/raw/`

**Maps look wrong or empty**
- Verify your configuration file syntax
- Check that coordinate bounds are correct
- Ensure data files contain expected features

**Memory errors**
- Large geodata files can consume significant memory
- Try processing smaller geographic areas first
- Consider using simplified data sources

### Getting Help

1. Check the logs: `make status`
2. Open an interactive shell: `make shell`
3. Test with a simple map first: `make map-spain`

## Next Steps

1. **Experiment with configurations** - Start with `spain_regions.yaml`
2. **Try different scales** - Generate maps for your local area
3. **Customize styling** - Adjust colors and fonts for your display
4. **Add your own data** - Include custom points of interest
5. **Use QGIS** - For fine-tuned interactive design

## Tips for Wall Display

- **Font sizes**: Use large fonts (24+ points) for 5-meter viewing
- **High contrast**: White text on dark backgrounds works well
- **Simplification**: Less is more for distant viewing
- **Test on device**: View generated maps on your actual TV

## Data Sources

The project uses these free, high-quality data sources:

- **Natural Earth** - Administrative boundaries, physical features
- **OpenStreetMap** - Detailed local data
- **IGN España** - Official Spanish geographic data
- **EU Administrative Units** - European boundaries

All data is automatically downloaded and processed by the scripts.
