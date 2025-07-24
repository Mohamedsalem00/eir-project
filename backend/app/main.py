from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .core.database import SessionLocal, engine, Base
from .models.imei import IMEI

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EIR Project API", version="1.0.0")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "EIR Project API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/imei/{imei}")
def check_imei(imei: str, db: Session = Depends(get_db)):
    imei_record = db.query(IMEI).filter(IMEI.imei_number == imei).first()
    if imei_record:
        return {"imei": imei, "status": imei_record.status}
    return {"imei": imei, "status": "not_found"}

