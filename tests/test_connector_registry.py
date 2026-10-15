from datasentinel.connectors import (
    CSVConnector,
    ConnectorRegistry,
    ExcelConnector,
    JSONConnector,
    PostgreSQLConnector,
    RESTConnector,
    SQLiteConnector,
)


def test_registry_lists_connectors() -> None:
    """Test that all required connectors are registered."""
    registry = ConnectorRegistry()

    assert registry.list_connectors() == [
        "csv",
        "excel",
        "json",
        "postgresql",
        "rest",
        "sqlite",
    ]


def test_registry_returns_correct_connector() -> None:
    """Test that the registry returns the correct connector."""
    registry = ConnectorRegistry()

    assert isinstance(registry.get("csv"), CSVConnector)
    assert isinstance(registry.get("excel"), ExcelConnector)
    assert isinstance(registry.get("json"), JSONConnector)
    assert isinstance(registry.get("sqlite"), SQLiteConnector)
    assert isinstance(registry.get("postgresql"), PostgreSQLConnector)
    assert isinstance(registry.get("rest"), RESTConnector)


def test_registry_can_register_new_connector() -> None:
    """Test that a new connector can be registered."""

    class TestConnector(CSVConnector):
        """Test connector."""

    registry = ConnectorRegistry()
    registry.register("test", TestConnector)

    assert isinstance(registry.get("test"), TestConnector)


def test_registry_rejects_unknown_connector() -> None:
    """Test that an unknown connector raises an error."""
    registry = ConnectorRegistry()

    try:
        registry.get("unknown")
        assert False
    except ValueError as exc:
        assert "Unknown connector type" in str(exc)