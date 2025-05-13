import base64
import logging
from .utils import request
from typing import Tuple, Dict, Optional


def login(client) -> Tuple[Dict[str, str], str, str]:
    """
    Perform login to the FMC and retrieve authentication details.

    This function authenticates the client either using a provided token or
    by using basic authentication with the username and password.

    Args:
        client: The FMCOpenAPIClient instance performing the login.

    Returns:
        Tuple[Dict[str, str], str, str]:
            - A dictionary of headers including the authorization token.
            - The domain UUID (a string).
            - The Swagger URL (a string).

    Raises:
        ValueError: If both username and password are not provided for basic authentication.
        Exception: If the login fails due to invalid credentials or other issues.
    """
    domain_uuid = None

    if client.token:
        client.headers["Authorization"] = f"Bearer {client.token}"
        logging.info("Using provided token for authentication")
    else:
        if not client.username or not client.password:
            raise ValueError("Username and password must be provided for login.")
        login_url = f"https://{client.hostname}/api/fmc_platform/v1/auth/generatetoken"
        credentials = f"{client.username}:{client.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        client.headers["Authorization"] = f"Basic {encoded_credentials}"

        resp = request(client, login_url, "POST")
        if resp.status_code != 204:
            raise Exception("Login failed")

        headers = resp.headers
        client.headers["X-auth-access-token"] = headers.get("x-auth-access-token")
        domain_uuid = headers.get("DOMAINS")
        logging.info("Logged in successfully")

    swagger_url = f"https://{client.hostname}/api/api-explorer/fmc.json"
    return client.headers, domain_uuid, swagger_url


def logout(client) -> None:
    """
    Logout from the FMC and close the session.

    This function terminates the current session, effectively logging out the user.

    Args:
        client: The FMCOpenAPIClient instance performing the logout.

    Raises:
        Exception: If there is an issue closing the session.
    """
    try:
        client.session.close()
        logging.info("Logged out successfully")
    except Exception as e:
        logging.error(f"Error during logout: {e}")
        raise
