from pathlib import Path

from datasentinel.connectors.json import JSONConnector


def test_json_connector() -> None:
    source = Path("data/sample.json")

    connector = JSONConnector()
    dataset = connector.connect(str(source))

    assert len(dataset.data) == 3
    assert list(dataset.data.columns) == [
        "id",
        "name",
        "age",
        "department",
    ]
    assert dataset.source == str(source)





def test_nested_json_connector() -> None:
    source = Path("data/nested.json")

    connector = JSONConnector()
    dataset = connector.connect(str(source))

    assert len(dataset.data) == 2
    assert "employee.department" in dataset.data.columns
    assert "employee.location" in dataset.data.columns