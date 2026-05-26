"""Anomaly detection engine for identifying energy waste patterns.

Uses statistical methods and machine learning to detect:
- Phantom loads (equipment consuming power when idle)
- HVAC overcooling/overheating
- Air leaks in compressed air systems
- Voltage imbalance
- Furnace cycling inefficiency
- Motor overload conditions
- Power spikes and unusual patterns
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


@dataclass
class AnomalyResult:
    """Result of anomaly detection analysis."""

    is_anomaly: bool
    anomaly_type: str
    severity: str  # low, medium, high, critical
    confidence: float
    description: str
    baseline_value: float
    actual_value: float
    deviation_percent: float
    estimated_waste_kwh: float
    estimated_cost_usd: float
    root_cause: str


class AnomalyDetector:
    """
    AI-powered anomaly detection for industrial energy systems.

    Combines multiple detection methods:
    1. Statistical (Z-score, IQR)
    2. Isolation Forest
    3. Pattern-based rules
    4. Contextual analysis
    """

    def __init__(self):
        self.threshold = settings.AI_ANOMALY_THRESHOLD
        self.cost_per_kwh = 0.12  # Default electricity cost
        self._models: Dict[str, any] = {}

    def detect_anomalies(
        self,
        sensor_values: List[float],
        timestamps: List[datetime],
        sensor_type: str,
        baseline_avg: float,
        baseline_std: float,
        asset_type: str = "generic",
    ) -> List[AnomalyResult]:
        """
        Run anomaly detection on a series of sensor readings.

        Args:
            sensor_values: List of sensor readings
            timestamps: Corresponding timestamps
            sensor_type: Type of sensor (power, temperature, etc.)
            baseline_avg: Historical average for this sensor
            baseline_std: Historical standard deviation
            asset_type: Type of asset for context-aware detection

        Returns:
            List of detected anomalies
        """
        anomalies = []

        if len(sensor_values) < 10:
            return anomalies

        values = np.array(sensor_values)

        # Method 1: Z-score based detection
        z_anomalies = self._zscore_detection(
            values, baseline_avg, baseline_std, sensor_type
        )
        anomalies.extend(z_anomalies)

        # Method 2: Pattern-based detection
        pattern_anomalies = self._pattern_detection(
            values, timestamps, sensor_type, asset_type
        )
        anomalies.extend(pattern_anomalies)

        # Method 3: Isolation Forest (ML-based)
        ml_anomalies = self._isolation_forest_detection(values, baseline_avg)
        anomalies.extend(ml_anomalies)

        # Deduplicate and rank by severity
        anomalies = self._deduplicate_anomalies(anomalies)

        return anomalies

    def _zscore_detection(
        self,
        values: np.ndarray,
        baseline_avg: float,
        baseline_std: float,
        sensor_type: str,
    ) -> List[AnomalyResult]:
        """Detect anomalies using Z-score method."""
        anomalies = []

        if baseline_std == 0:
            baseline_std = 0.01  # Prevent division by zero

        # Calculate Z-scores relative to baseline
        z_scores = np.abs((values - baseline_avg) / baseline_std)

        # Find values exceeding threshold
        anomaly_mask = z_scores > 3.0  # 3 sigma rule
        current_value = values[-1] if len(values) > 0 else 0
        current_z = z_scores[-1] if len(z_scores) > 0 else 0

        if current_z > 3.0:
            deviation = ((current_value - baseline_avg) / baseline_avg) * 100
            severity = self._calculate_severity(current_z)
            waste_kwh = abs(current_value - baseline_avg) * 0.25  # 15-min estimate

            anomalies.append(
                AnomalyResult(
                    is_anomaly=True,
                    anomaly_type=self._infer_anomaly_type(
                        sensor_type, current_value, baseline_avg
                    ),
                    severity=severity,
                    confidence=min(0.99, 0.7 + (current_z - 3) * 0.1),
                    description=(
                        f"Sensor reading {current_value:.2f} deviates "
                        f"{abs(deviation):.1f}% from baseline {baseline_avg:.2f}"
                    ),
                    baseline_value=baseline_avg,
                    actual_value=current_value,
                    deviation_percent=deviation,
                    estimated_waste_kwh=waste_kwh,
                    estimated_cost_usd=waste_kwh * self.cost_per_kwh,
                    root_cause=self._infer_root_cause(
                        sensor_type, current_value, baseline_avg
                    ),
                )
            )

        return anomalies

    def _pattern_detection(
        self,
        values: np.ndarray,
        timestamps: List[datetime],
        sensor_type: str,
        asset_type: str,
    ) -> List[AnomalyResult]:
        """Detect anomalies based on known industrial patterns."""
        anomalies = []

        # Phantom Load Detection: Power > 0 when expected to be off
        if sensor_type == "power" and asset_type in ["motor", "compressor", "pump"]:
            recent_values = values[-12:]  # Last hour (5-min intervals)
            if np.all(recent_values > 0) and np.all(recent_values < np.mean(values) * 0.15):
                avg_phantom = np.mean(recent_values)
                anomalies.append(
                    AnomalyResult(
                        is_anomaly=True,
                        anomaly_type="phantom_load",
                        severity="medium",
                        confidence=0.85,
                        description=(
                            f"Phantom load detected: {avg_phantom:.2f} kW "
                            f"consumed during expected idle period"
                        ),
                        baseline_value=0.0,
                        actual_value=avg_phantom,
                        deviation_percent=100.0,
                        estimated_waste_kwh=avg_phantom * 24,
                        estimated_cost_usd=avg_phantom * 24 * self.cost_per_kwh,
                        root_cause="Equipment not fully shutting down or standby power draw",
                    )
                )

        # HVAC Overcooling Detection
        if sensor_type == "temperature" and asset_type == "hvac":
            recent_avg = np.mean(values[-12:])
            if recent_avg < 18.0:  # Below 18°C is likely overcooling
                anomalies.append(
                    AnomalyResult(
                        is_anomaly=True,
                        anomaly_type="hvac_overcooling",
                        severity="medium",
                        confidence=0.80,
                        description=(
                            f"HVAC overcooling detected: zone temperature "
                            f"{recent_avg:.1f}°C (below 18°C threshold)"
                        ),
                        baseline_value=22.0,
                        actual_value=recent_avg,
                        deviation_percent=((recent_avg - 22.0) / 22.0) * 100,
                        estimated_waste_kwh=5.0,
                        estimated_cost_usd=5.0 * self.cost_per_kwh,
                        root_cause="Setpoint too low or faulty thermostat",
                    )
                )

        # Power Spike Detection
        if sensor_type == "power":
            if len(values) >= 3:
                recent_diff = np.diff(values[-5:])
                max_spike = np.max(np.abs(recent_diff))
                avg_value = np.mean(values)
                if max_spike > avg_value * 0.5:  # >50% jump
                    anomalies.append(
                        AnomalyResult(
                            is_anomaly=True,
                            anomaly_type="power_spike",
                            severity="high",
                            confidence=0.88,
                            description=(
                                f"Power spike detected: {max_spike:.2f} kW "
                                f"sudden change (>{avg_value * 0.5:.1f} kW threshold)"
                            ),
                            baseline_value=avg_value,
                            actual_value=values[-1],
                            deviation_percent=(max_spike / avg_value) * 100,
                            estimated_waste_kwh=max_spike * 0.083,
                            estimated_cost_usd=max_spike * 0.083 * self.cost_per_kwh,
                            root_cause="Sudden load change, possible equipment fault",
                        )
                    )

        return anomalies

    def _isolation_forest_detection(
        self, values: np.ndarray, baseline_avg: float
    ) -> List[AnomalyResult]:
        """Detect anomalies using Isolation Forest algorithm."""
        anomalies = []

        if len(values) < 50:
            return anomalies

        try:
            from sklearn.ensemble import IsolationForest

            # Reshape for sklearn
            X = values.reshape(-1, 1)

            # Fit Isolation Forest
            model = IsolationForest(
                contamination=0.05,
                random_state=42,
                n_estimators=100,
            )
            predictions = model.fit_predict(X)
            scores = model.decision_function(X)

            # Check if latest points are anomalous
            if predictions[-1] == -1:
                anomaly_score = abs(scores[-1])
                current_value = values[-1]
                deviation = ((current_value - baseline_avg) / baseline_avg) * 100

                anomalies.append(
                    AnomalyResult(
                        is_anomaly=True,
                        anomaly_type="unusual_pattern",
                        severity="medium" if anomaly_score < 0.3 else "high",
                        confidence=min(0.95, 0.6 + anomaly_score),
                        description=(
                            f"ML model detected unusual pattern "
                            f"(isolation score: {anomaly_score:.3f})"
                        ),
                        baseline_value=baseline_avg,
                        actual_value=current_value,
                        deviation_percent=deviation,
                        estimated_waste_kwh=abs(current_value - baseline_avg) * 0.25,
                        estimated_cost_usd=(
                            abs(current_value - baseline_avg) * 0.25 * self.cost_per_kwh
                        ),
                        root_cause="Unusual operational pattern detected by ML model",
                    )
                )

        except ImportError:
            logger.warning("scikit-learn not available for Isolation Forest")
        except Exception as e:
            logger.error("Isolation Forest error", error=str(e))

        return anomalies

    def _calculate_severity(self, z_score: float) -> str:
        """Calculate severity based on Z-score."""
        if z_score > 5.0:
            return "critical"
        elif z_score > 4.0:
            return "high"
        elif z_score > 3.5:
            return "medium"
        else:
            return "low"

    def _infer_anomaly_type(
        self, sensor_type: str, actual: float, baseline: float
    ) -> str:
        """Infer the anomaly type based on context."""
        if sensor_type == "power":
            if actual > baseline:
                return "motor_overload"
            else:
                return "efficiency_drop"
        elif sensor_type == "temperature":
            if actual < baseline:
                return "hvac_overcooling"
            else:
                return "furnace_cycling"
        elif sensor_type == "pressure":
            if actual < baseline:
                return "air_leak"
            else:
                return "unusual_pattern"
        elif sensor_type == "voltage":
            return "voltage_imbalance"
        return "unusual_pattern"

    def _infer_root_cause(
        self, sensor_type: str, actual: float, baseline: float
    ) -> str:
        """Infer probable root cause."""
        causes = {
            "power": "Possible mechanical overload or electrical fault",
            "temperature": "Thermostat misconfiguration or insulation issue",
            "pressure": "Possible air leak or valve malfunction",
            "voltage": "Possible phase imbalance or transformer issue",
            "current": "Possible motor winding issue or overload",
            "vibration": "Possible bearing failure or misalignment",
        }
        return causes.get(sensor_type, "Further investigation required")

    def _deduplicate_anomalies(
        self, anomalies: List[AnomalyResult]
    ) -> List[AnomalyResult]:
        """Remove duplicate anomalies, keeping highest confidence."""
        seen_types = {}
        for anomaly in anomalies:
            key = anomaly.anomaly_type
            if key not in seen_types or anomaly.confidence > seen_types[key].confidence:
                seen_types[key] = anomaly
        return list(seen_types.values())
