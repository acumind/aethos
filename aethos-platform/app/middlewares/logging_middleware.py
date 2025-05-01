import time
import uuid
from typing import Callable
import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request, log details, and pass to the next middleware/route handler.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            The response from the next middleware or route handler
        """
        # Generate a unique request ID
        request_id = str(uuid.uuid4())

        # Add request ID to request state for use in route handlers
        request.state.request_id = request_id

        # Start timer for request processing
        start_time = time.time()

        # Log the incoming request
        client_host = request.client.host if request.client else "unknown"
        logger.info(
            f"Request started | ID: {request_id} | "
            f"Method: {request.method} | Path: {request.url.path} | "
            f"Client: {client_host}"
        )

        # Process the request and get the response
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log the response
            logger.info(
                f"Request completed | ID: {request_id} | "
                f"Status: {response.status_code} | "
                f"Duration: {process_time:.4f}s"
            )

            # Add request ID and processing time to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # Log exceptions
            process_time = time.time() - start_time
            logger.error(
                f"Request failed | ID: {request_id} | "
                f"Duration: {process_time:.4f}s | "
                f"Error: {str(e)}"
            )

            # Re-raise the exception to be handled by the global exception handler
            raise
