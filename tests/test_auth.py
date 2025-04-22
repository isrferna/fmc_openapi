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


@patch("fmc_openapi.client.requests.Session.post")
@patch("fmc_openapi.client.requests.Session.get")
def test_login_success(mock_get, mock_post, client):
    """Test successful login with correct credentials"""
    # Mock the login POST response
    mock_response_post = MagicMock()
    mock_response_post.status_code = 204
    mock_response_post.headers = {
        "x-auth-access-token": "test-token",
        "DOMAINS": "test-domain-uuid",
    }
    mock_post.return_value = mock_response_post

    # Mock the GET response for fetching the Swagger JSON
    mock_response_get = MagicMock()
    mock_response_get.status_code = 200
    mock_response_get.json.return_value = {"paths": {}}
    mock_get.return_value = mock_response_get

    # Call the login method
    client.login()

    # Assert that the correct token and domain UUID were set
    assert client.headers["X-auth-access-token"] == "test-token"
    assert client.domain_uuid == "test-domain-uuid"


@patch("fmc_openapi.client.requests.Session.post")
def test_login_failure(mock_post, client):
    """Test login failure due to incorrect credentials"""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_post.return_value = mock_response

    with pytest.raises(Exception, match="Login failed"):
        client.login()


@patch("fmc_openapi.client.requests.Session.close")
def test_logout(mock_close, client):
    """Test successful logout"""
    client.logout()

    # Ensure that the session's close method was called
    mock_close.assert_called_once()
