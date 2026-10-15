from unittest.mock import MagicMock, patch

import pandas as pd

from datasentinel.connectors.postgresql import PostgreSQLConnector


def test_postgresql_connector() -> None:
    mock_connection = MagicMock()

    table_result = MagicMock()
    table_result.__iter__.return_value = [
        ("employees",),
    ]

    mock_connection.execute.return_value = table_result

    mock_data = pd.DataFrame(
        {
            "id": [1, 2],
            "name": ["Amit", "Riya"],
        }
    )

    with (
        patch(
            "datasentinel.connectors.postgresql.create_engine"
        ) as mock_create_engine,
        patch(
            "datasentinel.connectors.postgresql.pd.read_sql",
            return_value=mock_data,
        ),
    ):
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = (
            mock_connection
        )

        mock_create_engine.return_value = mock_engine

        connector = PostgreSQLConnector()

        dataset = connector.connect(
            "postgresql://user:password@localhost/testdb"
        )

    assert len(dataset.data) == 2
    assert list(dataset.data.columns) == [
        "id",
        "name",
    ]
    assert dataset.source == (
        "postgresql://user:password@localhost/testdb"
    )