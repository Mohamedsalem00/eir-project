#!/bin/bash

echo "Rebuilding EIR Project Database..."

# Stop containers
echo "Stopping containers..."
sudo docker-compose down

# Remove volumes completely
echo "Removing old data..."
sudo docker volume rm eir-project_db_data 2>/dev/null || true
sudo docker volume prune -f

# Start database
echo "Starting database..."
sudo docker-compose up -d db
sleep 15

# Create database
echo "Creating database..."
sudo docker exec -it eir-project_db_1 psql -U postgres -c "DROP DATABASE IF EXISTS imei_db;"
sudo docker exec -it eir-project_db_1 psql -U postgres -c "CREATE DATABASE imei_db;"

# Apply schema
echo "Applying schema..."
sudo docker cp backend/schema_postgres.sql eir-project_db_1:/tmp/schema_postgres.sql
sudo docker exec -it eir-project_db_1 psql -U postgres -d imei_db -f /tmp/schema_postgres.sql

# Load test data
echo "Loading test data..."
sudo docker cp backend/test_data.sql eir-project_db_1:/tmp/test_data.sql
sudo docker exec -it eir-project_db_1 psql -U postgres -d imei_db -f /tmp/test_data.sql

# Verify
echo "Verifying data..."
sudo docker exec -it eir-project_db_1 psql -U postgres -d imei_db -c "SELECT COUNT(*) as users FROM Utilisateur; SELECT COUNT(*) as devices FROM Appareil; SELECT COUNT(*) as imeis FROM IMEI;"

# Start all services
echo "Starting all services..."
sudo docker-compose build
sudo docker-compose up -d

echo "Database rebuild complete!"
echo "Test with: admin@eir.com / password123"
