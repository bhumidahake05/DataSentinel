from pathlib import Path

import pandas as pd

from datasentinel.connectors.excel import ExcelConnector


def test_excel_connector(tmp_path: Path) -> None:
    source = tmp_path / "sample.xlsx"

    data = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Amit", "Riya", "Rohan"],
            "age": [25, 24, 27],
        }
    )

    data.to_excel(source, index=False)

    connector = ExcelConnector()
    dataset = connector.connect(str(source))

    assert len(dataset.data) == 3
    assert list(dataset.data.columns) == [
        "id",
        "name",
        "age",
    ]
    assert dataset.source == str(source)