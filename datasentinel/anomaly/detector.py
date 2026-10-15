from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class AnomalyResult:
    """Result of statistical anomaly detection."""

    method: str
    column: str
    anomaly_indices: list[int]
    confidence_scores: dict[int, float]


class AnomalyDetector:
    """Detect statistical anomalies using Z-score and IQR."""

    def detect_zscore(
        self,
        data: pd.DataFrame,
        column: str,
        threshold: float = 3.0,
    ) -> AnomalyResult:
        """Detect anomalies using the Z-score method."""
        self._check_column(data, column)

        values = pd.to_numeric(data[column], errors="coerce")

        mean = float(values.mean())
        standard_deviation = float(values.std())

        if pd.isna(standard_deviation) or standard_deviation == 0:
            return AnomalyResult(
                method="zscore",
                column=column,
                anomaly_indices=[],
                confidence_scores={},
            )

        z_scores = (values - mean) / standard_deviation
        anomaly_mask = z_scores.abs() > threshold

        anomaly_indices = [
            int(index)
            for index in data.index[anomaly_mask.fillna(False)]
        ]

        confidence_scores: dict[int, float] = {}

        for index in anomaly_indices:
            raw_score: Any = z_scores.loc[index]

            if raw_score is None or pd.isna(raw_score):
                continue

            score = float(str(raw_score))
            confidence = min(abs(score) / threshold, 1.0)

            confidence_scores[int(index)] = confidence

        return AnomalyResult(
            method="zscore",
            column=column,
            anomaly_indices=anomaly_indices,
            confidence_scores=confidence_scores,
        )

    def detect_iqr(
        self,
        data: pd.DataFrame,
        column: str,
        multiplier: float = 1.5,
    ) -> AnomalyResult:
        """Detect anomalies using the IQR method."""
        self._check_column(data, column)

        values = pd.to_numeric(data[column], errors="coerce")

        first_quartile = float(str(values.quantile(0.25)))
        third_quartile = float(str(values.quantile(0.75)))

        iqr: float = third_quartile - first_quartile

        if iqr == 0:
            return AnomalyResult(
                method="iqr",
                column=column,
                anomaly_indices=[],
                confidence_scores={},
            )

        lower_bound: float = (
            first_quartile - (multiplier * iqr)
        )

        upper_bound: float = (
            third_quartile + (multiplier * iqr)
        )

        anomaly_mask = (
            (values < lower_bound)
            | (values > upper_bound)
        )

        anomaly_indices = [
            int(index)
            for index in data.index[anomaly_mask.fillna(False)]
        ]

        confidence_scores: dict[int, float] = {}

        for index in anomaly_indices:
            raw_value: Any = values.loc[index]

            if raw_value is None:
                continue

            value = float(str(raw_value))

            if pd.isna(value):
                continue

            if value < lower_bound:
                distance: float = lower_bound - value
            else:
                distance = value - upper_bound

            confidence: float = (
                distance / (iqr * multiplier)
            )

            confidence_scores[int(index)] = min(
                confidence,
                1.0,
            )

        return AnomalyResult(
            method="iqr",
            column=column,
            anomaly_indices=anomaly_indices,
            confidence_scores=confidence_scores,
        )

    @staticmethod
    def _check_column(
        data: pd.DataFrame,
        column: str,
    ) -> None:
        """Check that the requested column exists."""
        if column not in data.columns:
            raise ValueError(
                f"Column '{column}' does not exist in the dataset."
            )