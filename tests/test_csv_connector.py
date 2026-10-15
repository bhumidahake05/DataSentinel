from pathlib import Path

from datasentinel.connectors.csv import CSVConnector


def test_csv_connector() -> None:
    source = Path("data/sample.csv")

    connector = CSVConnector()
    dataset = connector.connect(str(source))

    assert len(dataset.data) == 5
    assert list(dataset.data.columns) == [
        "id",
        "name",
        "age",
        "salary",
    ]
    assert dataset.source == str(source)