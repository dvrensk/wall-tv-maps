# Wall TV Maps - Makefile

# Configuration
DOCKER_COMPOSE = docker-compose -f docker/docker-compose.yml
PYTHON = $(DOCKER_COMPOSE) exec maps python3
PYTHON_RUN = $(DOCKER_COMPOSE) run --rm maps python3
DATA_DIR = data
OUTPUT_DIR = output

# Default target
.PHONY: help
help:
	@echo "Wall TV Maps - Available targets:"
	@echo "  setup          - Build Docker environment"
	@echo "  download-data  - Download all required geodata"
	@echo "  create-autonomous-communities - Create autonomous communities from provinces"
	@echo "  create-provinces - Create optimized mainland Spain provinces file"
	@echo "  all-maps       - Generate all maps"
	@echo "  clean          - Clean generated files"
	@echo "  shell          - Open interactive shell"
	@echo ""
	@echo "Cache management:"
	@echo "  cache-info     - Show basemap cache information"
	@echo "  cache-clear    - Clear basemap cache (forces fresh download)"
	@echo ""
	@echo "Validation:"
	@echo "  test-env       - Test Docker environment"
	@echo "  test-python    - Test Python packages"
	@echo "  test-scripts   - Test script functionality"
	@echo ""
	@echo "Individual maps:"
	@echo "  generate CONFIG=file - Generate map from config file"
	@echo "  map-gijon      - Generate Gijón maps"
	@echo "  map-asturias   - Generate Asturias maps"
	@echo "  map-spain      - Generate Spain maps"
	@echo "  map-europe     - Generate Europe maps"

# Setup and environment
.PHONY: setup
setup:
	$(DOCKER_COMPOSE) build
	$(DOCKER_COMPOSE) up -d postgres
	@echo "Environment ready. Run 'make download-data' next."

# Validation targets
.PHONY: test-env
test-env:
	@echo "=== Testing Docker Environment ==="
	$(DOCKER_COMPOSE) run --rm maps ls -la
	@echo ""
	@echo "=== Testing Python ==="
	$(DOCKER_COMPOSE) run --rm maps python3 --version

.PHONY: test-python
test-python:
	@echo "=== Testing GeoPandas ==="
	$(DOCKER_COMPOSE) run --rm maps python3 -c "import geopandas; print('✓ GeoPandas:', geopandas.__version__)" 2>/dev/null || echo "✗ GeoPandas failed"
	@echo "=== Testing Matplotlib ==="
	$(DOCKER_COMPOSE) run --rm maps python3 -c "import matplotlib; print('✓ Matplotlib:', matplotlib.__version__)" 2>/dev/null || echo "✗ Matplotlib failed"
	@echo "=== Testing requests ==="
	$(DOCKER_COMPOSE) run --rm maps python3 -c "import requests; print('✓ Requests:', requests.__version__)" 2>/dev/null || echo "✗ Requests failed"

.PHONY: test-scripts
test-scripts:
	@echo "=== Testing download script ==="
	$(PYTHON_RUN) scripts/download_data.py --help | head -5
	@echo ""
	@echo "=== Testing generate script ==="
	$(PYTHON_RUN) scripts/generate_map.py --help | head -5 2>/dev/null || echo "generate_map.py needs to be created"

.PHONY: shell
shell:
	$(DOCKER_COMPOSE) run --rm maps bash

# Data management
.PHONY: download-data
download-data: setup
	$(PYTHON_RUN) scripts/download_data.py
	@echo "Data download complete."

.PHONY: process-data
process-data:
	$(PYTHON_RUN) scripts/process_data.py
	@echo "Data processing complete."

# Cache management
.PHONY: cache-info
cache-info:
	@echo "=== Basemap Cache Information ==="
	$(PYTHON_RUN) scripts/generate_map.py --cache-info

.PHONY: cache-clear
cache-clear:
	@echo "=== Clearing Basemap Cache ==="
	$(PYTHON_RUN) scripts/generate_map.py --clear-cache
	@echo "Cache cleared. Next map generation will download fresh tiles."

.PHONY: create-autonomous-communities
create-autonomous-communities:
	@echo "=== Creating Autonomous Communities from Provinces ===" 
	$(PYTHON_RUN) scripts/create_autonomous_communities.py
	@echo "Autonomous communities file created at data/processed/mainland_spain_autonomous_communities.geojson"

.PHONY: create-provinces
create-provinces:
	@echo "=== Creating Optimized Mainland Spain Provinces File ==="
	$(PYTHON_RUN) scripts/create_provinces.py
	@echo "Provinces file created at data/processed/mainland_spain_provinces.geojson"

# Map generation
.PHONY: all-maps
all-maps: map-gijon map-asturias map-spain map-europe

.PHONY: generate
generate:
	@if [ -z "$(CONFIG)" ]; then \
		echo "Usage: make generate CONFIG=config/your-config.yaml"; \
		echo "Available configs:"; \
		ls config/*.yaml; \
		exit 1; \
	fi
	$(PYTHON_RUN) scripts/generate_map.py --config $(CONFIG)

.PHONY: map-gijon
map-gijon:
	$(PYTHON_RUN) scripts/generate_map.py --config config/gijon_districts.yaml
	$(PYTHON_RUN) scripts/generate_map.py --config config/gijon_parks.yaml
	$(PYTHON_RUN) scripts/generate_map.py --config config/gijon_pois.yaml

.PHONY: map-asturias
map-asturias:
	$(PYTHON_RUN) scripts/generate_map.py --config config/asturias_comarcas.yaml
	$(PYTHON_RUN) scripts/generate_map.py --config config/asturias_geography.yaml
	$(PYTHON_RUN) scripts/generate_map.py --config config/asturias_cities.yaml

.PHONY: map-mainland-spain
map-mainland-spain:
	$(PYTHON_RUN) scripts/generate_map.py --config config/mainland_spain_regions.yaml
	$(PYTHON_RUN) scripts/generate_map.py --config config/mainland_spain_provinces.yaml

.PHONY: map-europe
map-europe:
	$(PYTHON_RUN) scripts/generate_map.py --config config/europe_west.yaml
	$(PYTHON_RUN) scripts/generate_map.py --config config/iberian_peninsula.yaml

# Utility targets
.PHONY: clean
clean:
	rm -rf $(OUTPUT_DIR)/*
	rm -rf $(DATA_DIR)/processed/*

.PHONY: clean-all
clean-all: clean
	rm -rf $(DATA_DIR)/*
	$(DOCKER_COMPOSE) down -v

.PHONY: status
status:
	@echo "=== Docker Status ==="
	$(DOCKER_COMPOSE) ps
	@echo ""
	@echo "=== Data Directory ==="
	@ls -la $(DATA_DIR)/
	@echo ""
	@echo "=== Output Directory ==="
	@ls -la $(OUTPUT_DIR)/

.PHONY: test
test:
	$(PYTHON_RUN) -m pytest scripts/tests/

# Development helpers
.PHONY: format
format:
	$(DOCKER_COMPOSE) run --rm maps black scripts/
	$(DOCKER_COMPOSE) run --rm maps isort scripts/

.PHONY: lint
lint:
	$(DOCKER_COMPOSE) run --rm maps flake8 scripts/
