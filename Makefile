# Wall TV Maps - Makefile

# Configuration
DOCKER_COMPOSE = docker-compose -f docker/docker-compose.yml
PYTHON = $(DOCKER_COMPOSE) exec maps python3
DATA_DIR = data
OUTPUT_DIR = output
QGIS_DIR = qgis

# Default target
.PHONY: help
help:
	@echo "Wall TV Maps - Available targets:"
	@echo "  setup          - Build Docker environment"
	@echo "  download-data  - Download all required geodata"
	@echo "  all-maps       - Generate all maps"
	@echo "  clean          - Clean generated files"
	@echo "  shell          - Open interactive shell"
	@echo "  qgis           - Launch QGIS"
	@echo ""
	@echo "Individual maps:"
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

.PHONY: shell
shell:
	$(DOCKER_COMPOSE) run --rm maps bash

.PHONY: qgis
qgis:
	$(DOCKER_COMPOSE) run --rm -e DISPLAY=$(DISPLAY) maps qgis

# Data management
.PHONY: download-data
download-data: setup
	$(PYTHON) scripts/download_data.py
	@echo "Data download complete."

.PHONY: process-data
process-data:
	$(PYTHON) scripts/process_data.py
	@echo "Data processing complete."

# Map generation
.PHONY: all-maps
all-maps: map-gijon map-asturias map-spain map-europe

.PHONY: map-gijon
map-gijon:
	$(PYTHON) scripts/generate_map.py --config config/gijon_districts.yaml
	$(PYTHON) scripts/generate_map.py --config config/gijon_parks.yaml
	$(PYTHON) scripts/generate_map.py --config config/gijon_pois.yaml

.PHONY: map-asturias
map-asturias:
	$(PYTHON) scripts/generate_map.py --config config/asturias_comarcas.yaml
	$(PYTHON) scripts/generate_map.py --config config/asturias_geography.yaml
	$(PYTHON) scripts/generate_map.py --config config/asturias_cities.yaml

.PHONY: map-spain
map-spain:
	$(PYTHON) scripts/generate_map.py --config config/spain_regions.yaml
	$(PYTHON) scripts/generate_map.py --config config/spain_provinces.yaml
	$(PYTHON) scripts/generate_map.py --config config/spain_geography.yaml

.PHONY: map-europe
map-europe:
	$(PYTHON) scripts/generate_map.py --config config/europe_west.yaml
	$(PYTHON) scripts/generate_map.py --config config/iberian_peninsula.yaml

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
	$(PYTHON) -m pytest scripts/tests/

# Development helpers
.PHONY: format
format:
	$(DOCKER_COMPOSE) run --rm maps black scripts/
	$(DOCKER_COMPOSE) run --rm maps isort scripts/

.PHONY: lint
lint:
	$(DOCKER_COMPOSE) run --rm maps flake8 scripts/
