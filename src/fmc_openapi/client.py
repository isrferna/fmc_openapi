import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from .auth import login, logout
from .swagger import fetch_swagger_json, extract_operation
from .executor import perform_operation
from .utils import is_requests_installed, configure_logger
from typing import Optional, Dict, Any


class FMCOpenAPIClient:
    """Client class to interact with the Cisco FMC REST API."""

    def __init__(
        self,
        hostname: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        verify: bool = False,
        retries: int = 5,
        timeout: int = 30,
    ) -> None:
        """
        Initializes the FMCOpenAPIClient object.

        Args:
            hostname (str): The hostname or IP of the FMC device.
            username (Optional[str]): The username for authentication.
            password (Optional[str]): The password for authentication.
            token (Optional[str]): The token for token-based authentication.
            verify (bool): Whether to verify SSL certificates.
            retries (int): Number of retries on failure.
            timeout (int): Timeout in seconds for requests.

        Raises:
            ModuleNotFoundError: If the 'requests' library is not installed.
        """
        if not is_requests_installed():
            raise ModuleNotFoundError(
                "The 'requests' library is not installed. Please install it with 'pip install requests'."
            )

        self.hostname = hostname
        self.username = username
        self.password = password
        self.token = token
        self.verify = verify
        self.retries = retries
        self.timeout = timeout
        self.session = requests.Session()
        self.domain_uuid = ""

        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504, 429],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE"],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

        if not verify:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        self.swagger_json = None
        self.swagger_url = None
        configure_logger()

    def __enter__(self) -> "FMCOpenAPIClient":
        """
        Enter the context manager, perform login.

        Returns:
            FMCOpenAPIClient: The current instance of the client.

        """
        self.login()
        return self

    def __exit__(
        self, exc_type: Optional[type], exc_value: Optional[BaseException], traceback: Optional[Any]
    ) -> None:
        """
        Exit the context manager, perform logout.

        Args:
            exc_type (Optional[type]): The exception type if an exception was raised.
            exc_value (Optional[BaseException]): The exception instance if an exception was raised.
            traceback (Optional[Any]): The traceback object if an exception was raised.
        """
        self.logout()

    def login(self) -> None:
        """
        Authenticate and retrieve an access token or use provided token.

        Raises:
            Exception: If login fails due to invalid credentials or other issues.
        """
        self.headers, self.domain_uuid, self.swagger_url = login(self)
        self.swagger_json = fetch_swagger_json(self)

    def operation(
        self, operation_id: str, payload: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Perform the specified API operation.

        Args:
            operation_id (str): The operation ID to execute.
            payload (Optional[Dict[str, Any]]): The payload to send with the request.
            **kwargs: Additional parameters for the operation.

        Returns:
            Dict[str, Any]: The response data from the operation.

        """
        return perform_operation(self, operation_id, payload, **kwargs)

    def logout(self) -> None:
        """
        Close the session and clean up.

        Raises:
            Exception: If there is an issue during logout.
        """
        logout(self)
