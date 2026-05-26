"""Operator approval model for human-in-the-loop decisions."""

import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from app.core.database import Base


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class OperatorApproval(Base):
    """Human approval record for AI recommendations before SCADA execution."""

    __tablename__ = "operator_approvals"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=False)
    requested_by = Column(String(100), default="ai_engine")
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, index=True)
    reason = Column(Text)  # Operator's reason for approval/rejection
    risk_level = Column(String(50))
    safety_check_passed = Column(String(10), default="pending")  # yes, no, pending
    requested_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    execution_result = Column(Text)  # Result after SCADA execution
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"<OperatorApproval(id={self.id}, "
            f"recommendation_id={self.recommendation_id}, status='{self.status}')>"
        )
