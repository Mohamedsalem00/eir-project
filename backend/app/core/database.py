from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Validate DATABASE_URL
if not DATABASE_URL:
    # Default development database URL
    DEFAULT_DB_URL = "postgresql://postgres:password@localhost:5432/imei_db"
    print(f"⚠️  DATABASE_URL not found in environment variables!")
    print(f"⚠️  Using default development database: {DEFAULT_DB_URL}")
    DATABASE_URL = DEFAULT_DB_URL

# Add support for UUID and better connection handling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
