FROM ubuntu:24.04

# Avoid timezone prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Madrid

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Basic tools
    curl \
    wget \
    unzip \
    git \
    make \
    # Python and pip
    python3 \
    python3-pip \
    python3-venv \
    # GDAL and spatial libraries (system packages)
    gdal-bin \
    python3-gdal \
    libgdal-dev \
    python3-fiona \
    python3-shapely \
    python3-pyproj \
    python3-rasterio \
    # GIS Python packages from system
    python3-geopandas \
    python3-pandas \
    python3-numpy \
    python3-matplotlib \
    # PostGIS and PostgreSQL
    postgresql-16 \
    postgresql-16-postgis-3 \
    postgresql-client-16 \
    # QGIS (for command line processing)
    qgis \
    python3-qgis \
    # Font support
    fonts-dejavu-core \
    fonts-liberation \
    # Image processing
    imagemagick \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Create virtual environment for additional packages not available as system packages
RUN python3 -m venv --system-site-packages /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install additional packages in virtual environment
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create postgres user and setup PostGIS
RUN service postgresql start && \
    su - postgres -c "createuser -d -r -s docker" && \
    su - postgres -c "createdb -O docker gis" && \
    su - postgres -c "psql -d gis -c 'CREATE EXTENSION postgis;'" && \
    su - postgres -c "psql -d gis -c 'CREATE EXTENSION hstore;'" && \
    service postgresql stop

# Copy application files
COPY . .

# Set up environment
ENV PYTHONPATH=/app/scripts
ENV PGUSER=docker
ENV PGDATABASE=gis

# Default command
CMD ["bash"]
