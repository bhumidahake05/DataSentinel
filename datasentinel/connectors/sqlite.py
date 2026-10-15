import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection

from datasentinel.connectors.base import BaseConnector
from datasentinel.connectors.dataset import DataSet


class SQLiteConnector(BaseConnector):
    """Connector for SQLite databases."""

    def connect(self, source: str) -> DataSet:
        """Connect to a SQLite database and load its data."""
        if not source.startswith("sqlite:///"):
            raise ValueError(
                "SQLite source must use the format "
                "'sqlite:///path/to/database.db'."
            )

        try:
            engine = create_engine(source)

            with engine.connect() as connection:
                tables = self._get_tables(connection)

                if not tables:
                    raise ValueError(
                        "SQLite database does not contain any tables."
                    )

                table_name = tables[0]

                data = pd.read_sql(
                    text(f'SELECT * FROM "{table_name}"'),
                    connection,
                )

            return DataSet(
                data=data,
                source=source,
            )

        except Exception as exc:
            raise RuntimeError(
                f"Failed to load SQLite database '{source}': {exc}"
            ) from exc

    @staticmethod
    def _get_tables(connection: Connection) -> list[str]:
        """Return table names from the SQLite database."""
        result = connection.execute(
            text(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' ORDER BY name"
            )
        )

        return [str(row[0]) for row in result]