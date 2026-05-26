"""Service layer for anomaly operations."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.anomaly import Anomaly, AnomalySeverity
from app.schemas.anomaly import AnomalyCreate, AnomalySummary


class AnomalyService:
    """Service for managing detected anomalies."""

    def __init__(self, db: Session):
        self.db = db

    def create_anomaly(self, anomaly_data: AnomalyCreate) -> Anomaly:
        """Create a new anomaly record."""
        anomaly = Anomaly(**anomaly_data.model_dump())
        self.db.add(anomaly)
        self.db.commit()
        self.db.refresh(anomaly)
        return anomaly

    def get_anomaly(self, anomaly_id: int) -> Optional[Anomaly]:
        """Get an anomaly by ID."""
        return self.db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()

    def list_anomalies(
        self,
        skip: int = 0,
        limit: int = 100,
        asset_id: Optional[int] = None,
        severity: Optional[AnomalySeverity] = None,
        is_resolved: Optional[bool] = None,
    ) -> List[Anomaly]:
        """List anomalies with optional filters."""
        query = self.db.query(Anomaly)
        if asset_id:
            query = query.filter(Anomaly.asset_id == asset_id)
        if severity:
            query = query.filter(Anomaly.severity == severity)
        if is_resolved is not None:
            query = query.filter(Anomaly.is_resolved == is_resolved)
        return query.order_by(Anomaly.detected_at.desc()).offset(skip).limit(limit).all()

    def resolve_anomaly(self, anomaly_id: int) -> Optional[Anomaly]:
        """Mark an anomaly as resolved."""
        from datetime import datetime

        anomaly = self.get_anomaly(anomaly_id)
        if not anomaly:
            return None
        anomaly.is_resolved = True
        anomaly.resolved_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(anomaly)
        return anomaly

    def get_summary(self) -> AnomalySummary:
        """Get anomaly summary statistics."""
        total = self.db.query(func.count(Anomaly.id)).scalar() or 0
        active = (
            self.db.query(func.count(Anomaly.id))
            .filter(Anomaly.is_resolved == False)
            .scalar() or 0
        )
        resolved = (
            self.db.query(func.count(Anomaly.id))
            .filter(Anomaly.is_resolved == True)
            .scalar() or 0
        )
        critical = (
            self.db.query(func.count(Anomaly.id))
            .filter(Anomaly.severity == AnomalySeverity.CRITICAL, Anomaly.is_resolved == False)
            .scalar() or 0
        )
        high = (
            self.db.query(func.count(Anomaly.id))
            .filter(Anomaly.severity == AnomalySeverity.HIGH, Anomaly.is_resolved == False)
            .scalar() or 0
        )
        medium = (
            self.db.query(func.count(Anomaly.id))
            .filter(Anomaly.severity == AnomalySeverity.MEDIUM, Anomaly.is_resolved == False)
            .scalar() or 0
        )
        low = (
            self.db.query(func.count(Anomaly.id))
            .filter(Anomaly.severity == AnomalySeverity.LOW, Anomaly.is_resolved == False)
            .scalar() or 0
        )
        total_waste = (
            self.db.query(func.sum(Anomaly.energy_waste_kwh))
            .filter(Anomaly.is_resolved == False)
            .scalar() or 0.0
        )
        total_cost = (
            self.db.query(func.sum(Anomaly.cost_impact_usd))
            .filter(Anomaly.is_resolved == False)
            .scalar() or 0.0
        )

        return AnomalySummary(
            total_anomalies=total,
            active_anomalies=active,
            resolved_anomalies=resolved,
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            total_energy_waste_kwh=round(total_waste, 2),
            total_cost_impact_usd=round(total_cost, 2),
        )
