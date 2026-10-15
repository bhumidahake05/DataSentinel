import sqlite3
from pathlib import Path

from datasentinel.connectors.sqlite import SQLiteConnector


def test_sqlite_connector(tmp_path: Path) -> None:
    database = tmp_path / "sample.db"

    connection = sqlite3.connect(database)

    connection.execute(
        """
        CREATE TABLE employees (
            id INTEGER,
            name TEXT,
            department TEXT,
            salary INTEGER
        )
        """
    )

    connection.executemany(
        "INSERT INTO employees VALUES (?, ?, ?, ?)",
        [
            (1, "Amit", "IT", 30000),
            (2, "Riya", "HR", 35000),
            (3, "Rohan", "Sales", 40000),
        ],
    )

    connection.commit()
    connection.close()

    connector = SQLiteConnector()

    dataset = connector.connect(
        f"sqlite:///{database}"
    )

    assert len(dataset.data) == 3

    assert list(dataset.data.columns) == [
        "id",
        "name",
        "department",
        "salary",
    ]

    assert dataset.source == f"sqlite:///{database}"