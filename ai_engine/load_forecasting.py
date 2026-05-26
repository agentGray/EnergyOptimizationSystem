"""Load forecasting engine for predicting energy demand.

Uses historical patterns to predict future energy consumption,
enabling proactive optimization and demand response.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dataclasses import dataclass

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ForecastPoint:
    """Single point in a load forecast."""
    timestamp: datetime
    predicted_kw: float
    lower_bound_kw: float
    upper_bound_kw: float
    confidence: float



class LoadForecaster:
    """
    Energy load forecasting using historical patterns.

    Methods:
    1. Seasonal decomposition (hourly, daily, weekly)
    2. Linear regression with features
    3. Moving average with trend
    """

    def __init__(self):
        self._model = None

    def forecast(
        self,
        historical_values: List[float],
        historical_timestamps: List[datetime],
        horizon_hours: int = 24,
        interval_minutes: int = 60,
    ) -> List[ForecastPoint]:
        """
        Generate load forecast.

        Args:
            historical_values: Past power readings (kW)
            historical_timestamps: Corresponding timestamps
            horizon_hours: How far ahead to forecast
            interval_minutes: Forecast interval

        Returns:
            List of forecast points
        """
        if len(historical_values) < 24:
            return self._simple_forecast(
                historical_values, horizon_hours, interval_minutes
            )

        values = np.array(historical_values)
        forecasts = []

        # Calculate patterns
        hourly_pattern = self._extract_hourly_pattern(values)
        trend = self._calculate_trend(values)
        volatility = np.std(values) / np.mean(values) if np.mean(values) > 0 else 0.1

        now = datetime.utcnow()
        points_count = (horizon_hours * 60) // interval_minutes

        for i in range(points_count):
            future_time = now + timedelta(minutes=i * interval_minutes)
            hour = future_time.hour

            # Base prediction from hourly pattern
            predicted = hourly_pattern[hour] + trend * (i / points_count)

            # Confidence decreases with horizon
            confidence = max(0.5, 0.95 - (i * 0.02))

            # Uncertainty bounds
            uncertainty = predicted * volatility * (1 + i * 0.05)
            lower = max(0, predicted - uncertainty)
            upper = predicted + uncertainty

            forecasts.append(
                ForecastPoint(
                    timestamp=future_time,
                    predicted_kw=round(predicted, 2),
                    lower_bound_kw=round(lower, 2),
                    upper_bound_kw=round(upper, 2),
                    confidence=round(confidence, 3),
                )
            )

        return forecasts

    def _extract_hourly_pattern(self, values: np.ndarray) -> np.ndarray:
        """Extract average hourly pattern from data."""
        # Assume data is at regular intervals, reshape to daily
        points_per_day = min(24, len(values))
        if len(values) >= 24:
            daily_segments = len(values) // 24
            reshaped = values[: daily_segments * 24].reshape(daily_segments, 24)
            return np.mean(reshaped, axis=0)
        else:
            # Pad with mean if not enough data
            pattern = np.full(24, np.mean(values))
            pattern[: len(values)] = values[: min(24, len(values))]
            return pattern

    def _calculate_trend(self, values: np.ndarray) -> float:
        """Calculate linear trend in the data."""
        if len(values) < 2:
            return 0.0
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        return coeffs[0]  # Slope

    def _simple_forecast(
        self,
        values: List[float],
        horizon_hours: int,
        interval_minutes: int,
    ) -> List[ForecastPoint]:
        """Simple moving average forecast for limited data."""
        if not values:
            return []

        avg = np.mean(values)
        std = np.std(values) if len(values) > 1 else avg * 0.1
        now = datetime.utcnow()
        points_count = (horizon_hours * 60) // interval_minutes

        forecasts = []
        for i in range(points_count):
            future_time = now + timedelta(minutes=i * interval_minutes)
            forecasts.append(
                ForecastPoint(
                    timestamp=future_time,
                    predicted_kw=round(avg, 2),
                    lower_bound_kw=round(max(0, avg - 2 * std), 2),
                    upper_bound_kw=round(avg + 2 * std, 2),
                    confidence=0.6,
                )
            )
        return forecasts



class LoadForecaster:
    """
    Energy load forecasting using historical patterns.

    Methods:
    1. Seasonal decomposition (hourly, daily, weekly patterns)
    2. Linear regression with time-based features
    3. Moving average with trend detection
    """

    def __init__(self):
        self._model = None

    def forecast(
        self,
        historical_values: List[float],
        historical_timestamps: List[datetime],
        horizon_hours: int = 24,
        interval_minutes: int = 60,
    ) -> List[ForecastPoint]:
        """
        Generate load forecast.

        Args:
            historical_values: Past power readings (kW)
            historical_timestamps: Corresponding timestamps
            horizon_hours: How far ahead to forecast
            interval_minutes: Forecast interval

        Returns:
            List of forecast points
        """
        if len(historical_values) < 24:
            return self._simple_forecast(
                historical_values, horizon_hours, interval_minutes
            )

        values = np.array(historical_values)
        forecasts = []

        # Calculate patterns
        hourly_pattern = self._extract_hourly_pattern(values)
        trend = self._calculate_trend(values)
        volatility = (
            np.std(values) / np.mean(values) if np.mean(values) > 0 else 0.1
        )

        now = datetime.utcnow()
        points_count = (horizon_hours * 60) // interval_minutes

        for i in range(points_count):
            future_time = now + timedelta(minutes=i * interval_minutes)
            hour = future_time.hour

            predicted = hourly_pattern[hour] + trend * (i / points_count)
            confidence = max(0.5, 0.95 - (i * 0.02))
            uncertainty = predicted * volatility * (1 + i * 0.05)

            forecasts.append(
                ForecastPoint(
                    timestamp=future_time,
                    predicted_kw=round(predicted, 2),
                    lower_bound_kw=round(max(0, predicted - uncertainty), 2),
                    upper_bound_kw=round(predicted + uncertainty, 2),
                    confidence=round(confidence, 3),
                )
            )

        return forecasts

    def _extract_hourly_pattern(self, values: np.ndarray) -> np.ndarray:
        """Extract average hourly pattern from data."""
        if len(values) >= 24:
            daily_segments = len(values) // 24
            reshaped = values[: daily_segments * 24].reshape(daily_segments, 24)
            return np.mean(reshaped, axis=0)
        else:
            pattern = np.full(24, np.mean(values))
            pattern[: len(values)] = values[: min(24, len(values))]
            return pattern

    def _calculate_trend(self, values: np.ndarray) -> float:
        """Calculate linear trend in the data."""
        if len(values) < 2:
            return 0.0
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        return coeffs[0]

    def _simple_forecast(
        self,
        values: List[float],
        horizon_hours: int,
        interval_minutes: int,
    ) -> List[ForecastPoint]:
        """Simple moving average forecast for limited data."""
        if not values:
            return []

        avg = np.mean(values)
        std = np.std(values) if len(values) > 1 else avg * 0.1
        now = datetime.utcnow()
        points_count = (horizon_hours * 60) // interval_minutes

        forecasts = []
        for i in range(points_count):
            future_time = now + timedelta(minutes=i * interval_minutes)
            forecasts.append(
                ForecastPoint(
                    timestamp=future_time,
                    predicted_kw=round(avg, 2),
                    lower_bound_kw=round(max(0, avg - 2 * std), 2),
                    upper_bound_kw=round(avg + 2 * std, 2),
                    confidence=0.6,
                )
            )
        return forecasts
