"""
Unit tests for the FMCOpenAPIClient initialization.
"""

def test_client_initialization(client_with_swagger):
    """Test if the client is initialized correctly"""
    assert client_with_swagger.hostname == "test-hostname"
    assert client_with_swagger.username == "test-username"
    assert client_with_swagger.password == "test-password"
    assert client_with_swagger.token is None
    assert client_with_swagger.verify is False
    assert client_with_swagger.retries == 5
    assert client_with_swagger.timeout == 30
    assert client_with_swagger.session is not None
