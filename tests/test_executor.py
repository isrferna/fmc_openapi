"""
Unit tests for operations in the FMC OpenAPI client.
"""

from unittest.mock import patch, MagicMock
import pytest


@patch("fmc_openapi.client.requests.Session.get")
def test_operation_success(mock_get, client_with_swagger):
    """Test successful operation"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": ["item1", "item2"]}
    mock_get.return_value = mock_response

    result = client_with_swagger.operation("testOperationId", id="test-id")
    assert result["items"] == ["item1", "item2"]


def test_operation_failure(client_with_swagger):
    """Test operation failure due to invalid operationId"""
    with pytest.raises(Exception, match="Operation ID 'invalidOperationId' not found"):
        client_with_swagger.operation("invalidOperationId", id="test-id")
