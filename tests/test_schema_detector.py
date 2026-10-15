import pandas as pd

from datasentinel.schema.detector import SchemaDriftDetector


def test_schema_detection() -> None:
    """Test extraction of dataframe schema."""
    data = pd.DataFrame(
        {
            "id": [1, 2],
            "name": ["A", "B"],
        }
    )

    detector = SchemaDriftDetector()

    schema = detector.get_schema(data)

    assert schema["id"] == "int64"
    assert schema["name"] == "str"

def test_added_column() -> None:
    """Test detection of an added column."""
    detector = SchemaDriftDetector()

    baseline = {
        "id": "int64",
        "name": "str",
    }

    current = {
        "id": "int64",
        "name": "str",
        "email": "object",
    }

    changes = detector.compare(baseline, current)

    assert len(changes) == 1
    assert changes[0].change_type == "added"
    assert changes[0].column == "email"


def test_removed_column() -> None:
    """Test detection of a removed column."""
    detector = SchemaDriftDetector()

    baseline = {
        "id": "int64",
        "name": "str",
    }

    current = {
        "id": "int64",
    }

    changes = detector.compare(baseline, current)

    assert len(changes) == 1
    assert changes[0].change_type == "removed"
    assert changes[0].column == "name"


def test_type_change() -> None:
    """Test detection of a changed column type."""
    detector = SchemaDriftDetector()

    baseline = {
        "id": "int64",
        "name": "str",
    }

    current = {
        "id": "object",
        "name": "str",
    }

    changes = detector.compare(baseline, current)

    assert len(changes) == 1
    assert changes[0].change_type == "type_changed"
    assert changes[0].column == "id"
    assert changes[0].old_type == "int64"
    assert changes[0].new_type == "object"