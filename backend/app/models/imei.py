# models/imei.py

from sqlalchemy import Column, Integer, String
from ..core.database import Base

class IMEI(Base):
    __tablename__ = "imeis"

    id = Column(Integer, primary_key=True, index=True)
    imei_number = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="unknown")
