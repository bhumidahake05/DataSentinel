from typing import Any

import httpx
import pandas as pd

from datasentinel.connectors.base import BaseConnector
from datasentinel.connectors.dataset import DataSet


class RESTConnector(BaseConnector):
    """Connector for REST APIs."""

    def connect(self, source: str) -> DataSet:
        """Load data from a REST API."""
        try:
            records = self._fetch_all_pages(source)

            if not records:
                data = pd.DataFrame()
            else:
                data = pd.json_normalize(records)

            return DataSet(
                data=data,
                source=source,
            )

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"REST API request failed for '{source}': {exc}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load REST API data from '{source}': {exc}"
            ) from exc

    @staticmethod
    def _fetch_all_pages(source: str) -> list[dict[str, Any]]:
        """Fetch all pages from a REST API."""
        records: list[dict[str, Any]] = []
        page = 1

        with httpx.Client(timeout=30.0) as client:
            while True:
                response = client.get(
                    source,
                    params={"page": page},
                )
                response.raise_for_status()

                payload: Any = response.json()

                page_records = RESTConnector._extract_records(
                    payload
                )

                if not page_records:
                    break

                records.extend(page_records)

                if len(page_records) == 0:
                    break

                page += 1

        return records

    @staticmethod
    def _extract_records(
        payload: Any,
    ) -> list[dict[str, Any]]:
        """Extract records from a REST API response."""
        if isinstance(payload, list):
            return [
                item
                for item in payload
                if isinstance(item, dict)
            ]

        if isinstance(payload, dict):
            data = payload.get("data", [])

            if isinstance(data, list):
                return [
                    item
                    for item in data
                    if isinstance(item, dict)
                ]

        raise ValueError(
            "REST API response must contain a list of records "
            "or a 'data' list."
        )