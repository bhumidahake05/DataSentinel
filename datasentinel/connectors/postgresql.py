import pandas as pd
from sqlalchemy import create_engine, text

from datasentinel.connectors.base import BaseConnector
from datasentinel.connectors.dataset import DataSet


class PostgreSQLConnector(BaseConnector):
    """Connector for PostgreSQL databases."""

    def connect(self, source: str) -> DataSet:
        """Connect to PostgreSQL and load data."""
        if not source.startswith("postgresql"):
            raise ValueError(
                "PostgreSQL source must use a PostgreSQL connection URL."
            )

        try:
            engine = create_engine(source)

            with engine.connect() as connection:
                result = connection.execute(
                    text(
                        "SELECT table_name "
                        "FROM information_schema.tables "
                        "WHERE table_schema = 'public' "
                        "ORDER BY table_name"
                    )
                )

                tables = [str(row[0]) for row in result]

                if not tables:
                    raise ValueError(
                        "PostgreSQL database does not contain any "
                        "tables in the public schema."
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
                f"Failed to load PostgreSQL database: {exc}"
            ) from exc