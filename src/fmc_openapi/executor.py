"""Executor module for performing API operations."""

import logging
from typing import Optional, Dict, Any
from .swagger import extract_operation
from .utils import request, handle_response, build_url


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
    url = build_url(client.hostname, details["url"], kwargs, bulk, offset, limit)

    try:
        # Make the request and handle response
        resp = request(client, url, details["method"], payload)
        return handle_response(resp, details["method"], client, manual_pagination)
    except Exception as e:
        logging.error("Error during operation '%s': %s", operation_id, e)  # Lazy logging
        raise
