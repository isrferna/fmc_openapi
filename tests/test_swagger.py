"""
Unit tests for the FMC OpenAPI Swagger functionality.
"""

from unittest.mock import patch, MagicMock
import pytest
from fmc_openapi.swagger import fetch_swagger_json, extract_operation


@patch("fmc_openapi.client.requests.Session.get")
def test_fetch_swagger_json_success(mock_get, client_with_swagger):
    """Test successful fetching of Swagger JSON"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"paths": {}}
    mock_get.return_value = mock_response

    client_with_swagger.swagger_url = "https://test-hostname/api/api-explorer/fmc.json"
    swagger = fetch_swagger_json(client_with_swagger)

    assert swagger == {"paths": {}}


@patch("fmc_openapi.client.requests.Session.get")
def test_fetch_swagger_json_failure(mock_get, client_with_swagger):
    """Test failure in fetching Swagger JSON"""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    client_with_swagger.swagger_url = "https://test-hostname/api/api-explorer/fmc.json"

    with pytest.raises(Exception, match="Failed to retrieve Swagger file"):
        fetch_swagger_json(client_with_swagger)


def test_extract_operation(client_with_swagger):
    """Test extracting an operation from Swagger JSON"""
    client_with_swagger.swagger_json = {
        "paths":
        {
            "/test-path":
            {
                "get":
                {
                    "operationId": "testOperationId"
                }
            }
        }
    }
    operation = extract_operation(client_with_swagger, "testOperationId")
    assert operation == {"url": "/test-path", "method": "GET", "parameters": []}


def test_extract_operation_not_found(client_with_swagger):
    """Test extraction failure when operation ID is not found"""
    client_with_swagger.swagger_json = {"paths": {}}

    with pytest.raises(Exception, match="Operation ID 'invalidOperation' not found"):
        extract_operation(client_with_swagger, "invalidOperation")
