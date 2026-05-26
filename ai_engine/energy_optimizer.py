"""Energy optimization engine for reducing waste and costs.

Implements optimization strategies:
- Load shifting to off-peak hours
- Setpoint optimization
- Equipment scheduling
- Peak demand reduction
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class OptimizationResult:
    """Result of energy optimization analysis."""

    strategy: str
    asset_id: int
    asset_name: str
    current_power_kw: float
    optimized_power_kw: float
    savings_kw: float
    savings_kwh_daily: float
    savings_usd_daily: float
    co2_reduction_kg: float
    action: str
    parameters: Dict
    confidence: float
    risk_level: str  # low, medium, high


class EnergyOptimizer:
    """
    AI-powered energy optimization engine.

    Strategies:
    1. Load Shifting - Move flexible loads to off-peak periods
    2. Setpoint Optimization - Adjust HVAC/process setpoints
    3. Equipment Scheduling - Optimize start/stop times
    4. Peak Shaving - Reduce peak demand charges
    5. Efficiency Optimization - Improve equipment efficiency
    """

    def __init__(self):
        self.cost_per_kwh = 0.12
        self.peak_cost_multiplier = 2.5
        self.co2_factor = 0.4  # kg CO2 per kWh
        self.peak_hours = list(range(14, 20))  # 2 PM - 8 PM
        self.off_peak_hours = list(range(22, 6))  # 10 PM - 6 AM

    def optimize(
        self,
        assets: List[Dict],
        current_hour: int = None,
        demand_limit_kw: float = None,
    ) -> List[OptimizationResult]:
        """
        Run optimization across all assets.

        Args:
            assets: List of asset data with current readings
            current_hour: Current hour of day (0-23)
            demand_limit_kw: Maximum demand limit

        Returns:
            List of optimization recommendations
        """
        if current_hour is None:
            current_hour = datetime.utcnow().hour

        results = []

        # Strategy 1: Load Shifting
        results.extend(self._load_shifting(assets, current_hour))

        # Strategy 2: Setpoint Optimization
        results.extend(self._setpoint_optimization(assets))

        # Strategy 3: Equipment Scheduling
        results.extend(self._equipment_scheduling(assets, current_hour))

        # Strategy 4: Peak Demand Reduction
        if demand_limit_kw:
            results.extend(self._peak_shaving(assets, demand_limit_kw))

        # Sort by savings potential
        results.sort(key=lambda x: x.savings_usd_daily, reverse=True)

        return results

    def _load_shifting(
        self, assets: List[Dict], current_hour: int
    ) -> List[OptimizationResult]:
        """Identify loads that can be shifted to off-peak hours."""
        results = []

        # Only suggest load shifting during peak hours
        if current_hour not in self.peak_hours:
            return results

        flexible_types = ["compressor", "pump", "chiller"]

        for asset in assets:
            if asset.get("asset_type") in flexible_types and asset.get("is_critical") is False:
                current_power = asset.get("current_power_kw", 0)
                if current_power > 0:
                    savings_kw = current_power * 0.3  # Shift 30% of load
                    savings_kwh = savings_kw * 6  # Peak period hours
                    cost_savings = savings_kwh * self.cost_per_kwh * (
                        self.peak_cost_multiplier - 1
                    )

                    results.append(
                        OptimizationResult(
                            strategy="load_shifting",
                            asset_id=asset["id"],
                            asset_name=asset["name"],
                            current_power_kw=current_power,
                            optimized_power_kw=current_power - savings_kw,
                            savings_kw=savings_kw,
                            savings_kwh_daily=savings_kwh,
                            savings_usd_daily=round(cost_savings, 2),
                            co2_reduction_kg=round(savings_kwh * self.co2_factor, 2),
                            action="shift_load_to_offpeak",
                            parameters={
                                "reduce_by_percent": 30,
                                "shift_to_hours": "22:00-06:00",
                                "current_hour": current_hour,
                            },
                            confidence=0.82,
                            risk_level="low",
                        )
                    )

        return results

    def _setpoint_optimization(self, assets: List[Dict]) -> List[OptimizationResult]:
        """Optimize HVAC and process setpoints."""
        results = []

        for asset in assets:
            if asset.get("asset_type") == "hvac":
                current_power = asset.get("current_power_kw", 0)
                current_temp = asset.get("current_temperature", 22.0)

                # Each 1°C setpoint increase saves ~3% cooling energy
                if current_temp < 23.0:
                    temp_increase = min(2.0, 24.0 - current_temp)
                    savings_percent = temp_increase * 0.03
                    savings_kw = current_power * savings_percent
                    savings_kwh = savings_kw * 10  # Operating hours

                    results.append(
                        OptimizationResult(
                            strategy="setpoint_adjustment",
                            asset_id=asset["id"],
                            asset_name=asset["name"],
                            current_power_kw=current_power,
                            optimized_power_kw=current_power - savings_kw,
                            savings_kw=savings_kw,
                            savings_kwh_daily=savings_kwh,
                            savings_usd_daily=round(
                                savings_kwh * self.cost_per_kwh, 2
                            ),
                            co2_reduction_kg=round(
                                savings_kwh * self.co2_factor, 2
                            ),
                            action="adjust_setpoint",
                            parameters={
                                "current_setpoint": current_temp,
                                "recommended_setpoint": current_temp + temp_increase,
                                "savings_per_degree": "3%",
                            },
                            confidence=0.90,
                            risk_level="low",
                        )
                    )

        return results

    def _equipment_scheduling(
        self, assets: List[Dict], current_hour: int
    ) -> List[OptimizationResult]:
        """Optimize equipment start/stop scheduling."""
        results = []

        for asset in assets:
            status = asset.get("status")
            asset_type = asset.get("asset_type")
            current_power = asset.get("current_power_kw", 0)

            # Detect running non-critical equipment during off-hours
            if (
                status == "running"
                and not asset.get("is_critical")
                and current_hour in range(22, 6)
                and asset_type in ["lighting", "hvac", "conveyor"]
            ):
                savings_kwh = current_power * 8  # 8 off-hours

                results.append(
                    OptimizationResult(
                        strategy="equipment_scheduling",
                        asset_id=asset["id"],
                        asset_name=asset["name"],
                        current_power_kw=current_power,
                        optimized_power_kw=0.0,
                        savings_kw=current_power,
                        savings_kwh_daily=savings_kwh,
                        savings_usd_daily=round(savings_kwh * self.cost_per_kwh, 2),
                        co2_reduction_kg=round(savings_kwh * self.co2_factor, 2),
                        action="schedule_shutdown",
                        parameters={
                            "shutdown_time": "22:00",
                            "restart_time": "06:00",
                            "reason": "Non-critical equipment running during off-hours",
                        },
                        confidence=0.95,
                        risk_level="low",
                    )
                )

        return results

    def _peak_shaving(
        self, assets: List[Dict], demand_limit_kw: float
    ) -> List[OptimizationResult]:
        """Reduce peak demand to stay under contract limit."""
        results = []

        total_power = sum(a.get("current_power_kw", 0) for a in assets)

        if total_power <= demand_limit_kw:
            return results

        excess_kw = total_power - demand_limit_kw

        # Find non-critical loads to reduce
        non_critical = [
            a for a in assets
            if not a.get("is_critical") and a.get("current_power_kw", 0) > 0
        ]
        non_critical.sort(key=lambda x: x.get("current_power_kw", 0), reverse=True)

        remaining_excess = excess_kw
        for asset in non_critical:
            if remaining_excess <= 0:
                break

            power = asset.get("current_power_kw", 0)
            reduction = min(power * 0.5, remaining_excess)  # Max 50% reduction
            remaining_excess -= reduction

            results.append(
                OptimizationResult(
                    strategy="peak_shaving",
                    asset_id=asset["id"],
                    asset_name=asset["name"],
                    current_power_kw=power,
                    optimized_power_kw=power - reduction,
                    savings_kw=reduction,
                    savings_kwh_daily=reduction * 2,  # 2 peak hours
                    savings_usd_daily=round(
                        reduction * 2 * self.cost_per_kwh * self.peak_cost_multiplier, 2
                    ),
                    co2_reduction_kg=round(reduction * 2 * self.co2_factor, 2),
                    action="reduce_load",
                    parameters={
                        "reduce_by_kw": round(reduction, 2),
                        "demand_limit_kw": demand_limit_kw,
                        "current_total_kw": total_power,
                    },
                    confidence=0.88,
                    risk_level="medium",
                )
            )

        return results

    def calculate_savings_summary(
        self, results: List[OptimizationResult]
    ) -> Dict:
        """Calculate total savings from optimization results."""
        return {
            "total_savings_kw": round(sum(r.savings_kw for r in results), 2),
            "total_savings_kwh_daily": round(
                sum(r.savings_kwh_daily for r in results), 2
            ),
            "total_savings_usd_daily": round(
                sum(r.savings_usd_daily for r in results), 2
            ),
            "total_savings_usd_monthly": round(
                sum(r.savings_usd_daily for r in results) * 30, 2
            ),
            "total_co2_reduction_kg": round(
                sum(r.co2_reduction_kg for r in results), 2
            ),
            "recommendation_count": len(results),
        }
