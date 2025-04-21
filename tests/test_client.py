import pytest
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

def test_client_initialization(client):
    """Test if the client is initialized correctly"""
    assert client.hostname == "test-hostname"
    assert client.username == "test-username"
    assert client.password == "test-password"
    assert client.token is None
    assert client.verify is False
    assert client.retries == 5
    assert client.timeout == 30
    assert client.session is not None
