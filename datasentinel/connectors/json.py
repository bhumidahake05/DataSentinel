import json
from pathlib import Path
from typing import Any

import pandas as pd

from datasentinel.connectors.base import BaseConnector
from datasentinel.connectors.dataset import DataSet


class JSONConnector(BaseConnector):
    """Connector for JSON files."""

    def connect(self, source: str) -> DataSet:
        """Load a JSON file into a DataSet."""
        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(
                f"JSON file not found: {source}"
            )

        try:
            with path.open("r", encoding="utf-8") as file:
                content: Any = json.load(file)

            data = self._convert_to_dataframe(content)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON file '{source}': {exc}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load JSON file '{source}': {exc}"
            ) from exc

        return DataSet(
            data=data,
            source=source,
        )

    @staticmethod
    def _convert_to_dataframe(content: Any) -> pd.DataFrame:
        """Convert flat or nested JSON content to a DataFrame."""
        if isinstance(content, list):
            return pd.json_normalize(content)

        if isinstance(content, dict):
            return pd.json_normalize(content)

        raise ValueError(
            "JSON data must contain an object or an array."
        )