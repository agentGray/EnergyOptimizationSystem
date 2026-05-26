"""Recommendation model for AI-generated optimization suggestions."""

import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text, Boolean
from app.core.database import Base


class RecommendationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"
    EXPIRED = "expired"


class RecommendationPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecommendationCategory(str, enum.Enum):
    LOAD_SHIFTING = "load_shifting"
    SETPOINT_ADJUSTMENT = "setpoint_adjustment"
    EQUIPMENT_SCHEDULING = "equipment_scheduling"
    MAINTENANCE = "maintenance"
    REPLACEMENT = "replacement"
    BEHAVIORAL = "behavioral"
    PROCESS_OPTIMIZATION = "process_optimization"


class Recommendation(Base):
    """AI-generated optimization recommendation."""

    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    anomaly_id = Column(Integer, ForeignKey("anomalies.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(RecommendationCategory), nullable=False)
    priority = Column(Enum(RecommendationPriority), default=RecommendationPriority.MEDIUM)
    status = Column(Enum(RecommendationStatus), default=RecommendationStatus.PENDING, index=True)
    estimated_savings_kwh = Column(Float)
    estimated_savings_usd = Column(Float)
    estimated_co2_reduction_kg = Column(Float)
    confidence_score = Column(Float)
    action_command = Column(Text)  # SCADA command to execute
    action_parameters = Column(Text)  # JSON parameters for the command
    requires_approval = Column(Boolean, default=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return (
            f"<Recommendation(id={self.id}, title='{self.title}', "
            f"status='{self.status}', savings=${self.estimated_savings_usd})>"
        )
