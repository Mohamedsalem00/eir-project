"""
Database initialization script for production deployment
This script creates tables and initial data when the app starts
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
import time

def wait_for_db(database_url, max_retries=30):
    """Wait for database to be available"""
    print("⏳ Waiting for database to be ready...")
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(database_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database is ready!")
            return engine
        except OperationalError as e:
            print(f"🔄 Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(2)
    
    raise Exception("❌ Database connection failed after maximum retries")

def load_sql_file(file_path):
    """Load SQL from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"⚠️  SQL file not found: {file_path}")
        return None

def run_sql_script(engine, sql_content, script_name):
    """Execute SQL script"""
    if not sql_content:
        print(f"⚠️  Skipping {script_name} - file not found")
        return
    
    print(f"📋 Executing {script_name}...")
    try:
        with engine.connect() as conn:
            # Split by statements and execute each one
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            for stmt in statements:
                if stmt:
                    conn.execute(text(stmt))
            conn.commit()
        print(f"✅ {script_name} completed successfully")
    except Exception as e:
        print(f"⚠️  {script_name} execution error (might be expected): {e}")

def init_database():
    """Initialize database with schema and test data"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("⚠️  DATABASE_URL not found, skipping database initialization")
        return
    
    print("🚀 Starting database initialization...")
    
    try:
        # Wait for database and get engine
        engine = wait_for_db(database_url)
        
        # Load and execute schema
        schema_sql = load_sql_file('/app/schema_postgres.sql')
        run_sql_script(engine, schema_sql, "Database Schema")
        
        # Load and execute test data
        test_data_sql = load_sql_file('/app/test_data.sql')
        run_sql_script(engine, test_data_sql, "Test Data")
        
        print("✅ Database initialization completed!")
        print("")
        print("🔑 Test Users Available (password: admin123):")
        print("   👑 admin@eir-project.com (Admin)")
        print("   👤 user@example.com (Regular User)")
        print("   🏢 insurance@company.com (Insurance)")
        print("   👮 police@agency.gov (Police)")
        print("   🏭 manufacturer@techcorp.com (Manufacturer)")
        print("")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Don't exit - let the app start anyway
        print("🔄 App will continue starting...")

if __name__ == "__main__":
    init_database()
