"""API routes for anomaly management."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.anomaly import AnomalySeverity
from app.schemas.anomaly import AnomalyCreate, AnomalyResponse, AnomalySummary
from app.services.anomaly_service import AnomalyService

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])


@router.post("/", response_model=AnomalyResponse, status_code=201)
def create_anomaly(anomaly_data: AnomalyCreate, db: Session = Depends(get_db)):
    """Create a new anomaly record (typically called by AI engine)."""
    service = AnomalyService(db)
    return service.create_anomaly(anomaly_data)


@router.get("/", response_model=List[AnomalyResponse])
def list_anomalies(
    skip: int = 0,
    limit: int = 100,
    asset_id: Optional[int] = None,
    severity: Optional[AnomalySeverity] = None,
    is_resolved: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List anomalies with optional filters."""
    service = AnomalyService(db)
    return service.list_anomalies(
        skip=skip, limit=limit, asset_id=asset_id, severity=severity, is_resolved=is_resolved
    )


@router.get("/summary", response_model=AnomalySummary)
def get_anomaly_summary(db: Session = Depends(get_db)):
    """Get anomaly summary statistics."""
    service = AnomalyService(db)
    return service.get_summary()


@router.get("/{anomaly_id}", response_model=AnomalyResponse)
def get_anomaly(anomaly_id: int, db: Session = Depends(get_db)):
    """Get a specific anomaly by ID."""
    service = AnomalyService(db)
    anomaly = service.get_anomaly(anomaly_id)
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return anomaly


@router.post("/{anomaly_id}/resolve", response_model=AnomalyResponse)
def resolve_anomaly(anomaly_id: int, db: Session = Depends(get_db)):
    """Mark an anomaly as resolved."""
    service = AnomalyService(db)
    anomaly = service.resolve_anomaly(anomaly_id)
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return anomaly
