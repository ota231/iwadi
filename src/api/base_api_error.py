from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class APIErrorDetail:
    """Structured error details container"""

    code: Optional[str] = None
    description: Optional[str] = None
    retryable: bool = False
    metadata: Optional[Dict[str, Any]] = None


class BaseAPIError(Exception):
    """Root error class for all API operations"""

    def __init__(
        self,
        message: str,
        *,
        error_type: str = "generic",
        status_code: Optional[int] = None,
        details: Optional[APIErrorDetail] = None,
        source: Optional[str] = None,
    ):
        """
        Args:
            message: Human-readable error message
            error_type: Machine-readable error category
            status_code: HTTP status code if applicable
            details: Structured error details
            source: Which API subsystem failed (e.g., 'arxiv', 'ieee')
        """
        self.error_type = error_type
        self.status_code = status_code
        self.details = details or APIErrorDetail()
        self.source = source
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        base = f"[{self.source}] {self.__class__.__name__}: {super().__str__()}"
        if self.status_code:
            base += f" (HTTP {self.status_code})"
        if self.details.code:
            base += f" | Code: {self.details.code}"
        return base


# --------------------------
# Specialized Error Classes
# --------------------------


class APIRequestError(BaseAPIError):
    """For request/transport-level failures"""

    def __init__(self, **kwargs: Any):
        kwargs.setdefault("error_type", "request_failure")
        super().__init__(**kwargs)


class APIAuthError(BaseAPIError):
    """Authentication/authorization failures"""

    def __init__(self, **kwargs: Any):
        kwargs.setdefault("error_type", "auth_failure")
        kwargs["details"].retryable = False  # Auth errors usually shouldn't be retried
        super().__init__(**kwargs)


class APIQuotaError(BaseAPIError):
    """Rate limiting/quota violations"""

    def __init__(self, **kwargs: Any):
        kwargs.setdefault("error_type", "quota_exceeded")
        kwargs["details"].retryable = True
        super().__init__(**kwargs)


class APIResponseError(BaseAPIError):
    """For malformed API responses"""

    def __init__(self, **kwargs: Any):
        kwargs.setdefault("error_type", "invalid_response")
        super().__init__(**kwargs)


class APIServiceError(BaseAPIError):
    """When the API service is malfunctioning"""

    def __init__(self, **kwargs: Any):
        kwargs.setdefault("error_type", "service_error")
        kwargs["details"].retryable = True
        super().__init__(**kwargs)
