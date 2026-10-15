from abc import ABC, abstractmethod

from datasentinel.connectors.dataset import DataSet


class BaseConnector(ABC):
    """Abstract base class for all data connectors."""

    @abstractmethod
    def connect(self, source: str) -> DataSet:
        """Connect to a source and return a DataSet."""
        raise NotImplementedError