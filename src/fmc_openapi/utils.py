"""Utils module for the FMC OpenAPI package."""

from typing import Optional, Dict, Any
import logging
import importlib
import re
import requests


def is_requests_installed() -> bool:
    """
    Checks if the 'requests' library is installed.

    Returns:
        bool: True if the 'requests' library is installed, False otherwise.
    """
    return importlib.util.find_spec("requests") is not None


def configure_logger() -> None:
    """
    Configures the logging settings for the application.
    Sets the log level to INFO and specifies the log message format.
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def request(
    client, url: str, method: str = "GET", payload: Optional[Dict[str, Any]] = None
) -> "requests.Response":
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
        logging.error("Request failed: %s", e)
        raise


def build_url(
    hostname: str,
    endpoint: str,
    kwargs: Dict[str, Any],
    bulk: bool,
    offset: Optional[int],
    limit: Optional[int],
) -> str:
    """
    Builds the complete URL for the API request.

    Args:
        hostname: The hostname of the API server.
        endpoint: The API endpoint path.
        kwargs: Parameters to replace placeholders in the URL.
        bulk: Whether the bulk operation flag is set.
        offset: Pagination offset.
        limit: Pagination limit.

    Returns:
        str: The fully constructed API URL.
    """
    url = f"https://{hostname}{endpoint}"

    # Replace placeholders in the URL with provided values from kwargs
    placeholders = re.findall(r"\{(\w+)\}", url)
    for ph in placeholders:
        if ph not in kwargs:
            raise ValueError(f"Missing parameter: {ph}")
        url = url.replace(f"{{{ph}}}", str(kwargs[ph]))

    # Add query parameters
    query = {"bulk": "true" if bulk else None, "offset": offset, "limit": limit}
    query.update({k: v for k, v in kwargs.items() if k not in placeholders})
    query_str = "&".join(f"{k}={v}" for k, v in query.items() if v is not None)
    if query_str:
        url += ("&" if "?" in url else "?") + query_str

    return url


def handle_response(
    resp, method: str, client, manual_pagination: bool
) -> Dict[str, Any]:
    """
    Handles the API response and performs pagination if needed.

    Args:
        resp: The initial API response.
        method: The HTTP method used for the request.
        client: The FMCOpenAPIClient instance.
        manual_pagination: Whether to disable automatic pagination.

    Returns:
        Dict[str, Any]: The final combined response.
    """
    data = resp.json()

    if manual_pagination:
        return data

    # Handle pagination
    all_items = data.get("items", [])
    next_urls = data.get("paging", {}).get("next", [])

    while next_urls:
        # Iterate through each URL in the 'next' list
        for next_url in next_urls:
            resp = request(client, next_url, method)
            items = resp.json().get("items", [])
            all_items.extend(items)
        # Get the next set of URLs
        next_urls = resp.json().get("paging", {}).get("next", [])

    if all_items:
        data["items"] = all_items

    return data
