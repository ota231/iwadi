from typing import Callable, TypeVar
from functools import wraps
import typer
from src.api.base_api_error import BaseAPIError
from typing import Tuple

T = TypeVar("T")


def api_error_handler(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to handle API errors consistently."""

    @wraps(func)
    def wrapper(*args: Tuple, **kwargs: Tuple) -> T:
        """Wrapper function to catch and handle API errors."""
        try:
            return func(*args, **kwargs)
        except BaseAPIError as e:
            typer.secho(f"\nError [{e.details.code}]: {e.message}", fg="red", err=True)
            raise typer.Exit(code=1)

    return wrapper
