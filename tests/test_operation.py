import pytest
from unittest.mock import patch, MagicMock
from fmc_openapi import FMCOpenAPIClient


@pytest.fixture
def client():
    """Fixture to provide a client instance for testing"""
    return FMCOpenAPIClient(
        hostname="test-hostname",
        username="test-username",
        password="test-password",
        verify=False,
    )


@patch("fmc_openapi.client.requests.Session.get")
def test_operation_success(mock_get, client):
    """Test successful operation"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": ["item1", "item2"]}
    mock_get.return_value = mock_response

    client.swagger_json = {"paths": {"/test-path": {"get": {"operationId": "testOperationId"}}}}

    result = client.operation("testOperationId", id="test-id")
    assert result["items"] == ["item1", "item2"]


def test_operation_failure(client):
    """Test operation failure due to invalid operationId"""
    client.swagger_json = {"paths": {"/test-path": {"get": {"operationId": "testOperationId"}}}}

    with pytest.raises(Exception, match="Operation ID 'invalidOperationId' not found"):
        client.operation("invalidOperationId", id="test-id")
