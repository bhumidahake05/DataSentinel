from unittest.mock import MagicMock, patch

from datasentinel.connectors.rest import RESTConnector


def test_rest_connector_pagination() -> None:
    first_response = MagicMock()
    first_response.raise_for_status.return_value = None
    first_response.json.return_value = {
        "data": [
            {"id": 1, "name": "Amit"},
            {"id": 2, "name": "Riya"},
        ]
    }

    second_response = MagicMock()
    second_response.raise_for_status.return_value = None
    second_response.json.return_value = {
        "data": [
            {"id": 3, "name": "Rohan"},
        ]
    }

    third_response = MagicMock()
    third_response.raise_for_status.return_value = None
    third_response.json.return_value = {
        "data": []
    }

    with patch(
        "datasentinel.connectors.rest.httpx.Client"
    ) as mock_client:
        client = mock_client.return_value.__enter__.return_value

        client.get.side_effect = [
            first_response,
            second_response,
            third_response,
        ]

        connector = RESTConnector()

        dataset = connector.connect(
            "https://example.com/api/employees"
        )

    assert len(dataset.data) == 3

    assert list(dataset.data.columns) == [
        "id",
        "name",
    ]

    assert dataset.source == (
        "https://example.com/api/employees"
    )

    assert client.get.call_count == 3