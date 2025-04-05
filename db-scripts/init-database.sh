#!/bin/bash
set -e

# Set default psql connection parameters
export PGPASSWORD="$POSTGRES_PASSWORD"

# Use the environment variables defined in the docker-compose file
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    CREATE ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASSWORD';
    CREATE DATABASE $APP_DB;
    ALTER DATABASE $APP_DB OWNER TO $DB_USER;
EOSQL

# Unset the PGPASSWORD environment variable after use
unset PGPASSWORD