FROM ubuntu:22.04

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
    # GDAL and spatial libraries
    gdal-bin \
    python3-gdal \
    libgdal-dev \
    # PostGIS and PostgreSQL
    postgresql-14 \
    postgresql-14-postgis-3 \
    postgresql-client-14 \
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

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

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
