from typing import Type

from datasentinel.connectors.base import BaseConnector
from datasentinel.connectors.csv import CSVConnector
from datasentinel.connectors.excel import ExcelConnector
from datasentinel.connectors.json import JSONConnector
from datasentinel.connectors.postgresql import PostgreSQLConnector
from datasentinel.connectors.rest import RESTConnector
from datasentinel.connectors.sqlite import SQLiteConnector


class ConnectorRegistry:
    """Registry for DataSentinel data connectors."""

    def __init__(self) -> None:
        """Initialize the connector registry."""
        self._connectors: dict[str, Type[BaseConnector]] = {
            "csv": CSVConnector,
            "excel": ExcelConnector,
            "json": JSONConnector,
            "sqlite": SQLiteConnector,
            "postgresql": PostgreSQLConnector,
            "rest": RESTConnector,
        }

    def register(
        self,
        name: str,
        connector: Type[BaseConnector],
    ) -> None:
        """Register a new connector."""
        self._connectors[name] = connector

    def get(self, name: str) -> BaseConnector:
        """Return an instance of the requested connector."""
        if name not in self._connectors:
            raise ValueError(
                f"Unknown connector type: {name}"
            )

        return self._connectors[name]()

    def list_connectors(self) -> list[str]:
        """Return the names of registered connectors."""
        return sorted(self._connectors.keys())