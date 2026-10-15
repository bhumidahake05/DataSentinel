import pandas as pd

from datasentinel.connectors.base import BaseConnector
from datasentinel.connectors.dataset import DataSet


class CSVConnector(BaseConnector):
    """Connector for CSV files."""

    def connect(self, source: str) -> DataSet:
        """Load a CSV file into a DataSet."""
        try:
            data = pd.read_csv(source)
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"CSV file not found: {source}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load CSV file '{source}': {exc}"
            ) from exc

        return DataSet(
            data=data,
            source=source,
        )