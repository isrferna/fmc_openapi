import logging
from .utils import request
from typing import Dict, Any


def fetch_swagger_json(client) -> Dict[str, Any]:
    """
    Fetches the Swagger JSON file from the provided client's Swagger URL.

    Args:
        client: The FMCOpenAPIClient instance that contains the Swagger URL.

    Returns:
        Dict[str, Any]: The parsed Swagger JSON data.

    Raises:
        Exception: If the Swagger file cannot be retrieved or the response status is not 200.
    """
    resp = request(client, client.swagger_url)
    if resp.status_code == 200:
        logging.info("Swagger file retrieved successfully")
        return resp.json()
    raise Exception("Failed to retrieve Swagger file")


def extract_operation(client, operation_id: str) -> Dict[str, Any]:
    """
    Extracts an operation's details from the Swagger JSON based on the operation ID.

    Args:
        client: The FMCOpenAPIClient instance that contains the loaded Swagger JSON.
        operation_id: The ID of the operation to be extracted from the Swagger file.

    Returns:
        Dict[str, Any]: A dictionary containing the operation's URL, method, and parameters.

    Raises:
        Exception: If the Swagger JSON is not loaded or the operation ID is not found in the Swagger file.
    """
    if not client.swagger_json:
        raise Exception("Swagger not loaded")

    for path, path_item in client.swagger_json.get("paths", {}).items():
        for method, operation in path_item.items():
            if operation.get("operationId") == operation_id:
                return {
                    "url": path,
                    "method": method.upper(),
                    "parameters": operation.get("parameters", []),
                }

    raise Exception(f"Operation ID '{operation_id}' not found")
