import logging
import requests
from typing import Optional, Dict, Any


def is_requests_installed() -> bool:
    """
    Checks if the 'requests' library is installed.

    Returns:
        bool: True if the 'requests' library is installed, False otherwise.
    """
    try:
        import requests

        return True
    except ImportError:
        return False


def configure_logger() -> None:
    """
    Configures the logging settings for the application.
    Sets the log level to INFO and specifies the log message format.
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def request(
    client, url: str, method: str = "GET", payload: Optional[Dict[str, Any]] = None
) -> requests.Response:
    """
    Sends an HTTP request using the specified method and URL.

    Args:
        client: The client instance that holds session information and headers.
        url: The URL to send the request to.
        method: The HTTP method (GET, POST, PUT, DELETE).
        payload: The payload data to send with POST or PUT requests (optional).

    Returns:
        requests.Response: The response object from the HTTP request.

    Raises:
        ValueError: If an unsupported HTTP method is provided.
        requests.RequestException: If the request fails due to network issues or invalid responses.
    """
    method = method.upper()
    if method not in ["GET", "POST", "PUT", "DELETE"]:
        raise ValueError(f"Unsupported method: {method}")

    func = getattr(client.session, method.lower())
    try:
        if method in ["POST", "PUT"] and payload:
            return func(
                url,
                headers=client.headers,
                json=payload,
                verify=client.verify,
                timeout=client.timeout,
            )
        return func(url, headers=client.headers, verify=client.verify, timeout=client.timeout)
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        raise
