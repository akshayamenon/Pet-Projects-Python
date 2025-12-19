# app/schemas.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DeviceCreate(BaseModel):
    device_id: str = Field(..., examples=["R1"])
    vendor: str = Field(..., examples=["Juniper"])
    ip: str = Field(..., examples=["192.168.1.10"])
    config: str = Field(..., examples=["set system host-name R1"])


class DeviceOut(BaseModel):
    device_id: str
    vendor: str
    ip: str
    config: str
    last_validation_status: Optional[str] = None
    last_validation_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ValidateRequest(BaseModel):
    device_id: str = Field(..., examples=["R1"])


class ValidateResponse(BaseModel):
    device_id: str
    status: str
    errors: List[str] = []
    validated_at: datetime
