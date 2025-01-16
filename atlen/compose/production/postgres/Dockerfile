FROM postgis/postgis:16-3.4

# Add bullseye repo for libicu67
RUN echo "deb http://deb.debian.org/debian bullseye main" > /etc/apt/sources.list.d/bullseye.list

# Install specific ICU version
RUN apt-get update && apt-get install -y --no-install-recommends \
    libicu67/bullseye \
    && rm -rf /var/lib/apt/lists/*

# Create a script to create PostGIS extension
RUN echo 'CREATE EXTENSION IF NOT EXISTS postgis;' > /docker-entrypoint-initdb.d/10_postgis.sql

COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance