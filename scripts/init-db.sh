#!/bin/bash
# Wait for PostgreSQL to be ready
until pg_isready -h db -p 5432 -U postgres; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Execute the schema
PGPASSWORD=postgres psql -h db -U postgres -d imei_db -f /docker-entrypoint-initdb.d/schema_postgres.sql

echo "Database schema initialized successfully"
