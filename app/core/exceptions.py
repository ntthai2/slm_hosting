class VllmTimeoutError(Exception):
    """Raised when vLLM does not respond in time."""
    pass


class VllmUnavailableError(Exception):
    """Raised when vLLM service is down."""
    pass


class InvalidRequestError(Exception):
    """Raised when request payload is invalid."""
    pass
