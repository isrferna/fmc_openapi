"""Custom exceptions for the FMC OpenAPI package."""


class AuthenticationError(Exception):
    """Raised when FMC authentication fails."""


class SwaggerFetchError(Exception):
    """Raised when there is an issue fetching the Swagger file."""
