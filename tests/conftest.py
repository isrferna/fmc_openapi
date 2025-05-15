"""
Shared pytest fixtures for FMC OpenAPI client tests.
"""

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

@pytest.fixture
def client_with_swagger(client):  # pylint: disable=redefined-outer-name
    """Fixture to provide a client instance with swagger_json set"""
    client.swagger_json = {"paths": {"/test-path": {"get": {"operationId": "testOperationId"}}}}
    return client
