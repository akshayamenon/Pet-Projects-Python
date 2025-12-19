# app/models.py
from sqlalchemy import Column, DateTime, String, Text
from app.db import Base


class Device(Base):
    __tablename__ = "devices"

    device_id = Column(String(64), primary_key=True, index=True)  # unique by PK
    vendor = Column(String(32), nullable=False)
    ip = Column(String(64), nullable=False)
    config = Column(Text, nullable=False)

    last_validation_status = Column(String(16), nullable=True)  # PASSED/FAILED
    last_validation_at = Column(DateTime(timezone=True), nullable=True)
