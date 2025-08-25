# backend/Dockerfile
FROM python:3.11

# Install PostgreSQL client for database operations
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install requirements first (for better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy database schema and test data files to accessible location
COPY schema_postgres.sql /app/
COPY test_data.sql /app/


# Copy application code
COPY ./app ./app

# Copy config directory from project root (outside backend) to /app/config
# COPY ../config ./config

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]