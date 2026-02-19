"""
Global error handling middleware for AITeam application.

This module provides:
- Centralized exception handling
- Structured error responses
- Proper HTTP status codes
- Logging of errors
"""

import logging
import traceback
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.exceptions import (
    AITeamException,
    ResourceNotFoundError,
    ValidationError,
    ExecutionError,
    LLMError,
    ConfigurationError,
    StorageError,
    WebSocketError,
    LLMRateLimitError,
)

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware that catches all exceptions and returns structured error responses.

    This middleware:
    1. Catches AITeamException and its subclasses for known errors
    2. Catches generic exceptions for unexpected errors
    3. Logs all errors with appropriate severity
    4. Returns consistent JSON error responses
    """

    def __init__(self, app: ASGIApp, debug: bool = False):
        super().__init__(app)
        self.debug = debug

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except AITeamException as e:
            return self._handle_aiteam_exception(e, request)
        except ValueError as e:
            return self._handle_value_error(e, request)
        except Exception as e:
            return self._handle_generic_exception(e, request)

    def _handle_aiteam_exception(self, exc: AITeamException, request: Request) -> JSONResponse:
        """Handle AITeam custom exceptions."""
        status_code = self._get_status_code(exc)
        error_response = exc.to_dict()

        # Log the error
        log_level = logging.WARNING if status_code < 500 else logging.ERROR
        logger.log(
            log_level,
            f"AITeamException during {request.method} {request.url.path}: "
            f"{exc.code} - {exc.message}",
            extra={"error_details": exc.details}
        )

        # Add debug info if enabled
        if self.debug:
            error_response["debug"] = {
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc().split("\n"),
            }

        return JSONResponse(
            status_code=status_code,
            content=error_response,
        )

    def _handle_value_error(self, exc: ValueError, request: Request) -> JSONResponse:
        """Handle ValueError exceptions (often from Pydantic validation)."""
        logger.warning(
            f"ValueError during {request.method} {request.url.path}: {str(exc)}"
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "INVALID_VALUE",
                "message": str(exc),
            },
        )

    def _handle_generic_exception(self, exc: Exception, request: Request) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.error(
            f"Unexpected exception during {request.method} {request.url.path}: "
            f"{type(exc).__name__}: {str(exc)}",
            exc_info=True
        )

        error_response = {
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
        }

        # Add debug info if enabled
        if self.debug:
            error_response["debug"] = {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "traceback": traceback.format_exc().split("\n"),
            }

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response,
        )

    def _get_status_code(self, exc: AITeamException) -> int:
        """Determine HTTP status code based on exception type."""
        if isinstance(exc, ResourceNotFoundError):
            return status.HTTP_404_NOT_FOUND
        elif isinstance(exc, ValidationError):
            return status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, LLMRateLimitError):
            return status.HTTP_429_TOO_MANY_REQUESTS
        elif isinstance(exc, (ConfigurationError, StorageError)):
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        elif isinstance(exc, (ExecutionError, LLMError, WebSocketError)):
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR


def error_handler_middleware(app, debug: bool = False) -> None:
    """
    Add error handler middleware to the FastAPI app.

    Args:
        app: FastAPI application instance
        debug: Whether to include debug information in error responses
    """
    app.add_middleware(ErrorHandlerMiddleware, debug=debug)


def setup_exception_handlers(app, debug: bool = False) -> None:
    """
    Set up exception handlers for the FastAPI app.

    This provides an alternative to middleware-based error handling,
    using FastAPI's built-in exception_handler decorator.

    Args:
        app: FastAPI application instance
        debug: Whether to include debug information in error responses
    """
    from fastapi import HTTPException
    from fastapi.exceptions import RequestValidationError

    @app.exception_handler(AITeamException)
    async def aiteam_exception_handler(request: Request, exc: AITeamException):
        """Handle AITeam custom exceptions."""
        status_code = _get_status_code_for_exception(exc)
        error_response = exc.to_dict()

        log_level = logging.WARNING if status_code < 500 else logging.ERROR
        logger.log(
            log_level,
            f"AITeamException during {request.method} {request.url.path}: "
            f"{exc.code} - {exc.message}",
            extra={"error_details": exc.details}
        )

        if debug:
            error_response["debug"] = {
                "exception_type": type(exc).__name__,
            }

        return JSONResponse(
            status_code=status_code,
            content=error_response,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors."""
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })

        logger.warning(
            f"Validation error during {request.method} {request.url.path}: {errors}"
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": errors},
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        logger.warning(
            f"HTTP {exc.status_code} during {request.method} {request.url.path}: {exc.detail}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(
            f"Unexpected exception during {request.method} {request.url.path}: "
            f"{type(exc).__name__}: {str(exc)}",
            exc_info=True
        )

        error_response = {
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
        }

        if debug:
            error_response["debug"] = {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "traceback": traceback.format_exc().split("\n"),
            }

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response,
        )


def _get_status_code_for_exception(exc: AITeamException) -> int:
    """Determine HTTP status code based on exception type."""
    if isinstance(exc, ResourceNotFoundError):
        return status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValidationError):
        return status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, LLMRateLimitError):
        return status.HTTP_429_TOO_MANY_REQUESTS
    elif isinstance(exc, (ConfigurationError, StorageError)):
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exc, (ExecutionError, LLMError, WebSocketError)):
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
