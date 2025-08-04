#!/bin/bash
# backend/init-db.sh
# Database initialization script for Docker container

set -e

echo "🚀 Initializing EIR Database..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until pg_isready -h db -p 5432 -U postgres; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "✅ PostgreSQL is ready!"

# Create the main schema
echo "📋 Creating main database schema..."
PGPASSWORD=postgres psql -h db -U postgres -d imei_db -f /app/schema_postgres.sql

# Insert test data
echo "📊 Inserting test data..."
PGPASSWORD=postgres psql -h db -U postgres -d imei_db -f /app/test_data.sql

echo "✅ Database initialization completed!"
echo ""
echo "🔑 Test Users (password: admin123):"
echo "   👑 admin@eir-project.com (Admin)"
echo "   👤 user@example.com (Regular User)"
echo "   🏢 insurance@company.com (Insurance)"
echo "   👮 police@agency.gov (Police)"
echo "   🏭 manufacturer@techcorp.com (Manufacturer)"
echo ""
echo "🌐 API Documentation: http://localhost:8000/docs"
