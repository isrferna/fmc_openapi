"""Executor module for performing API operations."""

import re
import logging
from typing import Optional, Dict, Any
from .swagger import extract_operation
from .utils import request


def perform_operation(
    client,
    operation_id: str,
    payload: Optional[Dict[str, Any]] = None,
    bulk: bool = False,
    manual_pagination: bool = False,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Perform an API operation using the given operation ID, payload, and optional query parameters.

    This function constructs the URL based on the provided operation ID and arguments, performs
    the API request, handles pagination if necessary, and returns the operation result.

    Args:
        client: The FMCOpenAPIClient instance used to perform the operation.
        operation_id: The ID of the operation to be executed.
        payload: Optional dictionary of data to send with the request (for POST/PUT methods).
        bulk: Boolean flag to indicate whether to perform a bulk operation.
        manual_pagination: Boolean flag to disable automatic pagination (default is False).
        offset: Optional offset for pagination.
        limit: Optional limit for pagination.
        **kwargs: Additional parameters to be used in the request URL or as query parameters.

    Returns:
        Dict[str, Any]: A dictionary containing the response data from the operation, including any
        paginated items.

    Raises:
        ValueError: If any required placeholder in the URL is missing.
        Exception: If there is any issue with the request or pagination.
    """
    details = extract_operation(client, operation_id)
    url = _build_url(client.hostname, details["url"], kwargs, bulk, offset, limit)

    try:
        # Make the request and handle response
        resp = request(client, url, details["method"], payload)
        return _handle_response(resp, details["method"], client, manual_pagination)
    except Exception as e:
        logging.error("Error during operation '%s': %s", operation_id, e)  # Lazy logging
        raise


def _build_url(
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


def _handle_response(
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
    next_url = data.get("paging", {}).get("next")

    while next_url:
        resp = request(client, next_url, method)
        items = resp.json().get("items", [])
        all_items.extend(items)
        next_url = resp.json().get("paging", {}).get("next")

    if all_items:
        data["items"] = all_items

    return data
