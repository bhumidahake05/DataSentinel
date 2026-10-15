import pandas as pd

from datasentinel.connectors.base import BaseConnector
from datasentinel.connectors.dataset import DataSet


class ExcelConnector(BaseConnector):
    """Connector for Excel files."""

    def connect(self, source: str) -> DataSet:
        """Load an Excel file into a DataSet."""
        try:
            data = pd.read_excel(source)
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Excel file not found: {source}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load Excel file '{source}': {exc}"
            ) from exc

        return DataSet(
            data=data,
            source=source,
        )