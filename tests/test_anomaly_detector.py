import pandas as pd

from datasentinel.anomaly.detector import AnomalyDetector


def test_zscore_detects_anomaly() -> None:
    """Test Z-score anomaly detection."""
    data = pd.DataFrame(
        {
            "value": [
                10,
                11,
                10,
                12,
                11,
                10,
                100,
            ]
        }
    )

    detector = AnomalyDetector()

    result = detector.detect_zscore(
        data,
        "value",
        threshold=2.0,
    )

    assert 6 in result.anomaly_indices
    assert result.method == "zscore"
    assert 6 in result.confidence_scores


def test_iqr_detects_anomaly() -> None:
    """Test IQR anomaly detection."""
    data = pd.DataFrame(
        {
            "value": [
                10,
                11,
                10,
                12,
                11,
                10,
                100,
            ]
        }
    )

    detector = AnomalyDetector()

    result = detector.detect_iqr(
        data,
        "value",
        multiplier=1.5,
    )

    assert 6 in result.anomaly_indices
    assert result.method == "iqr"
    assert 6 in result.confidence_scores


def test_zscore_without_variation() -> None:
    """Test Z-score with identical values."""
    data = pd.DataFrame(
        {
            "value": [10, 10, 10, 10],
        }
    )

    detector = AnomalyDetector()

    result = detector.detect_zscore(data, "value")

    assert result.anomaly_indices == []
    assert result.confidence_scores == {}


def test_iqr_without_variation() -> None:
    """Test IQR with identical values."""
    data = pd.DataFrame(
        {
            "value": [10, 10, 10, 10],
        }
    )

    detector = AnomalyDetector()

    result = detector.detect_iqr(data, "value")

    assert result.anomaly_indices == []
    assert result.confidence_scores == {}