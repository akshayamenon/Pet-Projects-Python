# app/main.py
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List
import os
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import get_session, init_db
from app.models import Device
from app.schemas import DeviceCreate, DeviceOut, ValidateRequest, ValidateResponse
from app.validators import run_validation
from fastapi.responses import RedirectResponse

# Group endpoints in Swagger by tag
tags_metadata = [
    {"name": "Devices", "description": "Register devices and fetch stored device info."},
    {"name": "Validation", "description": "Validate config asynchronously and store result."},
    {"name": "Summary", "description": "Pandas-based metrics."},
]

app = FastAPI(
    title="Device Configuration Validation Service",
    version="1.0.0",
    description="Register devices, validate configs asynchronously, store last validation result, and provide summary metrics.",
    openapi_tags=tags_metadata,
)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.get("/",include_in_schema = False)
def get():
    return RedirectResponse(url = "/docs")
@app.post(
    "/devices",
    response_model=DeviceOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Devices"],
    summary="Register a device",
    responses={
        201: {"description": "Device created"},
        409: {
            "description": "Device already exists",
            "content": {"application/json": {"example": {"detail": "Device 'R1' already exists."}}},
        },
    },
)
async def register_device(payload: DeviceCreate, session: AsyncSession = Depends(get_session)) -> DeviceOut:
    device = Device(
        device_id=payload.device_id,
        vendor=payload.vendor,
        ip=payload.ip,
        config=payload.config,
        last_validation_status=None,
        last_validation_at=None,
    )
    session.add(device)

    try:
        await session.commit()
        await session.refresh(device)
        return device
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Device '{payload.device_id}' already exists.",
        )


@app.get(
    "/devices/{device_id}",
    response_model=DeviceOut,
    tags=["Devices"],
    summary="Get device details",
    responses={
        200: {"description": "Device found"},
        404: {
            "description": "Device not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Device 'R99' does not exist. Create it first using POST /devices."}
                }
            },
        },
    },
)
async def get_device(device_id: str, session: AsyncSession = Depends(get_session)) -> DeviceOut:
    device = await session.get(Device, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_id}' does not exist. Create it first using POST /devices.",
        )
    return device


@app.post(
    "/validate",
    response_model=ValidateResponse,
    tags=["Validation"],
    summary="Validate device configuration (async)",
    description="Simulates a non-blocking delay and applies required validation rules.",
    responses={
        200: {"description": "Validation completed"},
        404: {
            "description": "Device not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Device 'R99' does not exist. Create it first using POST /devices."}
                }
            },
        },
    },
)
async def validate_device(payload: ValidateRequest, session: AsyncSession = Depends(get_session)) -> ValidateResponse:
    device = await session.get(Device, payload.device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{payload.device_id}' does not exist. Create it first using POST /devices.",
        )

    await asyncio.sleep(2)  # non-blocking simulated delay

    status_value, errors = run_validation(device.vendor, device.ip, device.config)

    now = datetime.now(timezone.utc)
    device.last_validation_status = status_value
    device.last_validation_at = now

    session.add(device)
    await session.commit()

    return ValidateResponse(
        device_id=device.device_id,
        status=status_value,
        errors=errors,
        validated_at=now,
    )


@app.get(
    "/summary",
    tags=["Summary"],
    summary="Get summary metrics (Pandas)",
    responses={200: {"description": "Summary returned"}},
)
async def summary(session: AsyncSession = Depends(get_session)) -> Dict[str, Any]:
    result = await session.execute(select(Device))
    devices: List[Device] = list(result.scalars().all())

    rows = [{"device_id": d.device_id, "last_validation_status": d.last_validation_status} for d in devices]
    df = pd.DataFrame(rows)

    total = int(len(df))
    if total == 0:
        return {"total_devices": 0, "passed_validations": 0, "failed_validations": 0}

    passed = int((df["last_validation_status"] == "PASSED").sum())
    failed = int((df["last_validation_status"] == "FAILED").sum())

    return {"total_devices": total, "passed_validations": passed, "failed_validations": failed}
