"""Operator approval workflow for AI recommendations.

Implements human-in-the-loop approval before SCADA commands
are executed, ensuring safety and operational control.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from dataclasses import dataclass, field

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


@dataclass
class ApprovalRequest:
    """A request for operator approval."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    recommendation_id: int = 0
    asset_id: int = 0
    asset_name: str = ""
    action: str = ""
    description: str = ""
    risk_level: str = "medium"
    estimated_savings_usd: float = 0.0
    parameters: Dict = field(default_factory=dict)
    requested_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=24)
    )
    status: str = "pending"  # pending, approved, rejected, expired
    operator_id: Optional[int] = None
    operator_reason: Optional[str] = None
    responded_at: Optional[datetime] = None


class OperatorApprovalWorkflow:
    """
    Human-in-the-loop approval workflow.

    Ensures that AI-generated recommendations require human
    approval before execution on critical equipment.

    Workflow:
    1. AI Engine generates recommendation
    2. System creates approval request
    3. Operator reviews on dashboard
    4. Operator approves/rejects with reason
    5. If approved, command sent to SCADA write-back
    6. Result logged for audit

    Auto-approval rules:
    - Low risk + high confidence + non-critical asset = auto-approve
    - All others require manual approval
    """

    def __init__(self):
        self._pending_requests: List[ApprovalRequest] = []
        self._history: List[ApprovalRequest] = []
        self.auto_approve_enabled = True
        self.auto_approve_max_risk = "low"
        self.auto_approve_min_confidence = 0.90

    def submit_for_approval(
        self,
        recommendation_id: int,
        asset_id: int,
        asset_name: str,
        action: str,
        description: str,
        risk_level: str,
        estimated_savings_usd: float,
        parameters: Dict,
        confidence: float = 0.0,
        is_critical_asset: bool = False,
        expires_in_hours: int = 24,
    ) -> ApprovalRequest:
        """
        Submit a recommendation for operator approval.

        Returns the approval request (may be auto-approved).
        """
        request = ApprovalRequest(
            recommendation_id=recommendation_id,
            asset_id=asset_id,
            asset_name=asset_name,
            action=action,
            description=description,
            risk_level=risk_level,
            estimated_savings_usd=estimated_savings_usd,
            parameters=parameters,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours),
        )

        # Check auto-approval eligibility
        if self._can_auto_approve(
            risk_level, confidence, is_critical_asset
        ):
            request.status = "approved"
            request.operator_reason = "Auto-approved (low risk, high confidence)"
            request.responded_at = datetime.utcnow()
            self._history.append(request)
            logger.info(
                "Recommendation auto-approved",
                request_id=request.id,
                action=action,
                asset=asset_name,
            )
        else:
            self._pending_requests.append(request)
            logger.info(
                "Recommendation submitted for approval",
                request_id=request.id,
                action=action,
                asset=asset_name,
                risk=risk_level,
            )

        return request

    def approve(
        self,
        request_id: str,
        operator_id: int,
        reason: Optional[str] = None,
    ) -> Optional[ApprovalRequest]:
        """Approve a pending request."""
        request = self._find_pending(request_id)
        if not request:
            return None

        if self._is_expired(request):
            request.status = "expired"
            self._move_to_history(request)
            return None

        request.status = "approved"
        request.operator_id = operator_id
        request.operator_reason = reason or "Approved by operator"
        request.responded_at = datetime.utcnow()

        self._move_to_history(request)

        logger.info(
            "Recommendation approved by operator",
            request_id=request_id,
            operator_id=operator_id,
        )
        return request

    def reject(
        self,
        request_id: str,
        operator_id: int,
        reason: str,
    ) -> Optional[ApprovalRequest]:
        """Reject a pending request."""
        request = self._find_pending(request_id)
        if not request:
            return None

        request.status = "rejected"
        request.operator_id = operator_id
        request.operator_reason = reason
        request.responded_at = datetime.utcnow()

        self._move_to_history(request)

        logger.info(
            "Recommendation rejected by operator",
            request_id=request_id,
            operator_id=operator_id,
            reason=reason,
        )
        return request

    def get_pending_requests(self) -> List[ApprovalRequest]:
        """Get all pending approval requests."""
        # Clean up expired requests
        self._cleanup_expired()
        return [r for r in self._pending_requests if r.status == "pending"]

    def get_history(
        self, limit: int = 50, status: Optional[str] = None
    ) -> List[ApprovalRequest]:
        """Get approval history with optional status filter."""
        history = self._history[-limit:]
        if status:
            history = [r for r in history if r.status == status]
        return history

    def get_stats(self) -> Dict:
        """Get approval workflow statistics."""
        all_requests = self._pending_requests + self._history
        total = len(all_requests)
        approved = sum(1 for r in all_requests if r.status == "approved")
        rejected = sum(1 for r in all_requests if r.status == "rejected")
        expired = sum(1 for r in all_requests if r.status == "expired")
        pending = sum(1 for r in self._pending_requests if r.status == "pending")

        # Average response time
        response_times = [
            (r.responded_at - r.requested_at).total_seconds()
            for r in self._history
            if r.responded_at and r.status in ["approved", "rejected"]
        ]
        avg_response_time = (
            sum(response_times) / len(response_times)
            if response_times
            else 0
        )

        return {
            "total_requests": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "expired": expired,
            "approval_rate": (
                round(approved / max(1, approved + rejected) * 100, 1)
            ),
            "avg_response_time_seconds": round(avg_response_time, 1),
            "auto_approve_enabled": self.auto_approve_enabled,
        }

    def _can_auto_approve(
        self, risk_level: str, confidence: float, is_critical: bool
    ) -> bool:
        """Check if a request can be auto-approved."""
        if not self.auto_approve_enabled:
            return False
        if is_critical:
            return False
        if risk_level != self.auto_approve_max_risk:
            return False
        if confidence < self.auto_approve_min_confidence:
            return False
        return True

    def _find_pending(self, request_id: str) -> Optional[ApprovalRequest]:
        """Find a pending request by ID."""
        for request in self._pending_requests:
            if request.id == request_id:
                return request
        return None

    def _is_expired(self, request: ApprovalRequest) -> bool:
        """Check if a request has expired."""
        return datetime.utcnow() > request.expires_at

    def _move_to_history(self, request: ApprovalRequest):
        """Move a request from pending to history."""
        self._pending_requests = [
            r for r in self._pending_requests if r.id != request.id
        ]
        self._history.append(request)

    def _cleanup_expired(self):
        """Mark expired requests."""
        for request in self._pending_requests:
            if self._is_expired(request):
                request.status = "expired"
                self._move_to_history(request)
