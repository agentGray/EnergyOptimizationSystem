"""API routes for sensor management and data ingestion."""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.sensor import (
    SensorCreate,
    SensorUpdate,
    SensorResponse,
    SensorReadingCreate,
    SensorReadingBatch,
    SensorReadingResponse,
)
from app.services.sensor_service import SensorService

router = APIRouter(prefix="/sensors", tags=["Sensors"])


@router.post("/", response_model=SensorResponse, status_code=201)
def create_sensor(sensor_data: SensorCreate, db: Session = Depends(get_db)):
    """Register a new sensor."""
    service = SensorService(db)
    existing = service.get_sensor_by_sensor_id(sensor_data.sensor_id)
    if existing:
        raise HTTPException(status_code=400, detail="Sensor ID already exists")
    return service.create_sensor(sensor_data)


@router.get("/", response_model=List[SensorResponse])
def list_sensors(
    skip: int = 0,
    limit: int = 100,
    asset_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List all sensors with optional filters."""
    service = SensorService(db)
    return service.list_sensors(skip=skip, limit=limit, asset_id=asset_id)


@router.get("/{sensor_id}", response_model=SensorResponse)
def get_sensor(sensor_id: int, db: Session = Depends(get_db)):
    """Get a specific sensor by ID."""
    service = SensorService(db)
    sensor = service.get_sensor(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


@router.put("/{sensor_id}", response_model=SensorResponse)
def update_sensor(sensor_id: int, sensor_data: SensorUpdate, db: Session = Depends(get_db)):
    """Update a sensor."""
    service = SensorService(db)
    sensor = service.update_sensor(sensor_id, sensor_data)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


@router.delete("/{sensor_id}", status_code=204)
def delete_sensor(sensor_id: int, db: Session = Depends(get_db)):
    """Delete a sensor."""
    service = SensorService(db)
    if not service.delete_sensor(sensor_id):
        raise HTTPException(status_code=404, detail="Sensor not found")


# --- Sensor Readings ---


@router.post("/readings", response_model=SensorReadingResponse, status_code=201)
def ingest_reading(reading_data: SensorReadingCreate, db: Session = Depends(get_db)):
    """Ingest a single sensor reading."""
    service = SensorService(db)
    return service.ingest_reading(reading_data)


@router.post("/readings/batch", status_code=201)
def ingest_batch(batch: SensorReadingBatch, db: Session = Depends(get_db)):
    """Ingest a batch of sensor readings."""
    service = SensorService(db)
    count = service.ingest_batch(batch.readings)
    return {"message": f"Successfully ingested {count} readings", "count": count}


@router.get("/readings/{sensor_id}", response_model=List[SensorReadingResponse])
def get_readings(
    sensor_id: int,
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    limit: int = Query(1000, le=10000),
    db: Session = Depends(get_db),
):
    """Get sensor readings within a time range."""
    service = SensorService(db)
    return service.get_readings(sensor_id, start_time, end_time, limit)


@router.get("/readings/{sensor_id}/latest", response_model=SensorReadingResponse)
def get_latest_reading(sensor_id: int, db: Session = Depends(get_db)):
    """Get the most recent reading for a sensor."""
    service = SensorService(db)
    reading = service.get_latest_reading(sensor_id)
    if not reading:
        raise HTTPException(status_code=404, detail="No readings found for this sensor")
    return reading


@router.get("/readings/{sensor_id}/stats")
def get_sensor_stats(
    sensor_id: int,
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    db: Session = Depends(get_db),
):
    """Get statistical summary of sensor readings."""
    service = SensorService(db)
    return service.get_sensor_stats(sensor_id, start_time, end_time)
