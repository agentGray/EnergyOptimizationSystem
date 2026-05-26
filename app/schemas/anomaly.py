"""Pydantic schemas for Anomaly endpoints."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.anomaly import AnomalyType, AnomalySeverity


class AnomalyCreate(BaseModel):
    asset_id: int
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    energy_waste_kwh: Optional[float] = None
    cost_impact_usd: Optional[float] = None
    root_cause: Optional[str] = None
    affected_sensors: Optional[str] = None
    baseline_value: Optional[float] = None
    actual_value: Optional[float] = None
    deviation_percent: Optional[float] = None


class AnomalyResponse(BaseModel):
    id: int
    asset_id: int
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    title: str
    description: Optional[str]
    confidence_score: float
    detected_at: datetime
    resolved_at: Optional[datetime]
    is_resolved: bool
    energy_waste_kwh: Optional[float]
    cost_impact_usd: Optional[float]
    root_cause: Optional[str]
    affected_sensors: Optional[str]
    baseline_value: Optional[float]
    actual_value: Optional[float]
    deviation_percent: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class AnomalySummary(BaseModel):
    total_anomalies: int
    active_anomalies: int
    resolved_anomalies: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    total_energy_waste_kwh: float
    total_cost_impact_usd: float
