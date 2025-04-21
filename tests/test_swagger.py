import pytest
from unittest.mock import patch, MagicMock
from fmc_openapi import FMCOpenAPIClient
from fmc_openapi.swagger import fetch_swagger_json, extract_operation

@pytest.fixture
def client():
    """Fixture to provide a client instance for testing"""
    return FMCOpenAPIClient(
        hostname="test-hostname",
        username="test-username",
        password="test-password",
        verify=False,
    )

@patch('fmc_openapi.client.requests.Session.get')
def test_fetch_swagger_json_success(mock_get, client):
    """Test successful fetching of Swagger JSON"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"paths": {}}
    mock_get.return_value = mock_response

    client.swagger_url = "https://test-hostname/api/api-explorer/fmc.json"
    swagger = fetch_swagger_json(client)

    assert swagger == {"paths": {}}

@patch('fmc_openapi.client.requests.Session.get')
def test_fetch_swagger_json_failure(mock_get, client):
    """Test failure in fetching Swagger JSON"""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    client.swagger_url = "https://test-hostname/api/api-explorer/fmc.json"
    
    with pytest.raises(Exception, match="Failed to retrieve Swagger file"):
        fetch_swagger_json(client)

def test_extract_operation(client):
    """Test extracting an operation from Swagger JSON"""
    client.swagger_json = {
        "paths": {
            "/test-path": {
                "get": {"operationId": "testOperationId"}
            }
        }
    }
    operation = extract_operation(client, "testOperationId")
    assert operation == {
        "url": "/test-path",
        "method": "GET",
        "parameters": []
    }

def test_extract_operation_not_found(client):
    """Test extraction failure when operation ID is not found"""
    client.swagger_json = {"paths": {}}

    with pytest.raises(Exception, match="Operation ID 'invalidOperation' not found"):
        extract_operation(client, "invalidOperation")
