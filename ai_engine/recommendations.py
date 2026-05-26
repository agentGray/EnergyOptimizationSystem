"""Recommendation engine that combines anomaly and optimization results.

Generates actionable recommendations with SCADA commands
for operator approval and automated execution.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

from ai_engine.anomaly_detection import AnomalyResult
from ai_engine.energy_optimizer import OptimizationResult
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ActionableRecommendation:
    """A recommendation ready for operator approval."""
    title: str
    description: str
    category: str
    priority: str
    asset_id: int
    estimated_savings_kwh: float
    estimated_savings_usd: float
    estimated_co2_reduction_kg: float
    confidence: float
    action_command: str
    action_parameters: Dict
    requires_approval: bool
    risk_level: str
    expires_in_hours: int



class RecommendationEngine:
    """
    Generates actionable recommendations from AI analysis.

    Combines anomaly detection results and optimization results
    into prioritized, actionable recommendations with SCADA commands.
    """

    def __init__(self):
        self.min_confidence = 0.7
        self.min_savings_usd = 1.0

    def generate_from_anomalies(
        self, anomalies: List[AnomalyResult], asset_id: int
    ) -> List[ActionableRecommendation]:
        """Generate recommendations from detected anomalies."""
        recommendations = []

        for anomaly in anomalies:
            if anomaly.confidence < self.min_confidence:
                continue

            rec = self._anomaly_to_recommendation(anomaly, asset_id)
            if rec:
                recommendations.append(rec)

        return recommendations

    def generate_from_optimization(
        self, optimizations: List[OptimizationResult]
    ) -> List[ActionableRecommendation]:
        """Generate recommendations from optimization results."""
        recommendations = []

        for opt in optimizations:
            if opt.savings_usd_daily < self.min_savings_usd:
                continue

            rec = ActionableRecommendation(
                title=f"{opt.strategy.replace('_', ' ').title()}: {opt.asset_name}",
                description=(
                    f"Reduce power from {opt.current_power_kw:.1f} kW to "
                    f"{opt.optimized_power_kw:.1f} kW using {opt.strategy} strategy. "
                    f"Expected daily savings: ${opt.savings_usd_daily:.2f}"
                ),
                category=opt.strategy,
                priority=self._determine_priority(opt.savings_usd_daily),
                asset_id=opt.asset_id,
                estimated_savings_kwh=opt.savings_kwh_daily,
                estimated_savings_usd=opt.savings_usd_daily,
                estimated_co2_reduction_kg=opt.co2_reduction_kg,
                confidence=opt.confidence,
                action_command=opt.action,
                action_parameters=opt.parameters,
                requires_approval=opt.risk_level != "low",
                risk_level=opt.risk_level,
                expires_in_hours=24,
            )
            recommendations.append(rec)

        return recommendations

    def _anomaly_to_recommendation(
        self, anomaly: AnomalyResult, asset_id: int
    ) -> Optional[ActionableRecommendation]:
        """Convert an anomaly into an actionable recommendation."""
        action_map = {
            "phantom_load": {
                "command": "schedule_shutdown",
                "params": {"mode": "standby", "verify_idle": True},
                "category": "equipment_scheduling",
            },
            "hvac_overcooling": {
                "command": "adjust_setpoint",
                "params": {"target_temp": 22.0, "mode": "auto"},
                "category": "setpoint_adjustment",
            },
            "air_leak": {
                "command": "flag_maintenance",
                "params": {"type": "air_leak_repair", "priority": "high"},
                "category": "maintenance",
            },
            "voltage_imbalance": {
                "command": "flag_maintenance",
                "params": {"type": "electrical_inspection"},
                "category": "maintenance",
            },
            "power_spike": {
                "command": "reduce_load",
                "params": {"reduce_by_percent": 20},
                "category": "process_optimization",
            },
            "motor_overload": {
                "command": "reduce_load",
                "params": {"reduce_by_percent": 15, "check_mechanical": True},
                "category": "maintenance",
            },
        }

        action_info = action_map.get(anomaly.anomaly_type, {
            "command": "investigate",
            "params": {"anomaly_type": anomaly.anomaly_type},
            "category": "process_optimization",
        })

        return ActionableRecommendation(
            title=f"Fix {anomaly.anomaly_type.replace('_', ' ').title()}",
            description=(
                f"{anomaly.description}. Root cause: {anomaly.root_cause}. "
                f"Estimated waste: {anomaly.estimated_waste_kwh:.2f} kWh/day"
            ),
            category=action_info["category"],
            priority=self._severity_to_priority(anomaly.severity),
            asset_id=asset_id,
            estimated_savings_kwh=anomaly.estimated_waste_kwh,
            estimated_savings_usd=anomaly.estimated_cost_usd,
            estimated_co2_reduction_kg=anomaly.estimated_waste_kwh * 0.4,
            confidence=anomaly.confidence,
            action_command=action_info["command"],
            action_parameters=action_info["params"],
            requires_approval=anomaly.severity in ["high", "critical"],
            risk_level="medium" if anomaly.severity in ["high", "critical"] else "low",
            expires_in_hours=48 if anomaly.severity == "low" else 12,
        )

    def _determine_priority(self, savings_usd: float) -> str:
        """Determine priority based on savings potential."""
        if savings_usd > 100:
            return "urgent"
        elif savings_usd > 50:
            return "high"
        elif savings_usd > 10:
            return "medium"
        return "low"

    def _severity_to_priority(self, severity: str) -> str:
        """Map anomaly severity to recommendation priority."""
        mapping = {
            "critical": "urgent",
            "high": "high",
            "medium": "medium",
            "low": "low",
        }
        return mapping.get(severity, "medium")
