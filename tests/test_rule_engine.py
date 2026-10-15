import pandas as pd

from datasentinel.connectors.dataset import DataSet
from datasentinel.rules.engine import RuleEngine
from datasentinel.rules.models import Rule


def create_dataset() -> DataSet:
    """Create a sample dataset for rule tests."""
    data = pd.DataFrame(
        {
            "id": [1, 2, 2, 4],
            "name": ["Amit", "Riya", None, "Neha123"],
            "age": [25, 24, 70, 26],
        }
    )

    return DataSet(
        data=data,
        source="test",
    )


def test_null_check() -> None:
    """Test null value validation."""
    engine = RuleEngine()
    rule = Rule(
        type="null_check",
        column="name",
        parameters={"allowed_nulls": 0},
    )

    result = engine.run_rule(create_dataset(), rule)

    assert result.passed is False
    assert result.violations == 1


def test_unique_check() -> None:
    """Test uniqueness validation."""
    engine = RuleEngine()
    rule = Rule(
        type="unique_check",
        column="id",
        parameters={},
    )

    result = engine.run_rule(create_dataset(), rule)

    assert result.passed is False
    assert result.violations == 1


def test_range_check() -> None:
    """Test range validation."""
    engine = RuleEngine()
    rule = Rule(
        type="range",
        column="age",
        parameters={
            "min": 18,
            "max": 60,
        },
    )

    result = engine.run_rule(create_dataset(), rule)

    assert result.passed is False
    assert result.violations == 1


def test_regex_check() -> None:
    """Test regular-expression validation."""
    engine = RuleEngine()
    rule = Rule(
        type="regex",
        column="name",
        parameters={
            "pattern": r"^[A-Za-z ]+$",
        },
    )

    result = engine.run_rule(create_dataset(), rule)

    assert result.passed is False
    assert result.violations == 2