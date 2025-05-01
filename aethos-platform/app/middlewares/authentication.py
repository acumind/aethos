from typing import Callable, Optional
import logging

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError, jwt

from app.core.config import settings

logger = logging.getLogger(__name__)

# Define paths that do not require authentication
PUBLIC_PATHS = [
    f"{settings.API_V1_STR}/auth/login",
    f"{settings.API_V1_STR}/auth/register",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health"
]


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for token validation.

    This middleware checks for valid JWT tokens in protected routes.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request, validate JWT token, and pass to the next middleware/route handler.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            The response from the next middleware or route handler
        """
        # Skip authentication for public paths
        if self._is_public_path(request.url.path):
            return await call_next(request)

        # Skip OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Get the token from the Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            # No token provided, return 401 Unauthorized
            return Response(
                content='{"detail":"Authentication required"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Extract token
        token = self._extract_token(auth_header)
        if not token:
            # Invalid Authorization header format
            return Response(
                content='{"detail":"Invalid Authorization header format"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Validate token
        try:
            # Basic validation (not checking claims like exp)
            # Detailed validation is done in auth dependencies
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            # Token is valid, continue to next middleware
            return await call_next(request)

        except JWTError as e:
            # Invalid token
            logger.warning(f"Invalid token: {str(e)}")
            return Response(
                content='{"detail":"Invalid authentication token"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            logger.error(f"Unexpected error validating token: {str(e)}")
            return Response(
                content='{"detail":"Authentication error"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json",
                headers={"WWW-Authenticate": "Bearer"}
            )

    def _is_public_path(self, path: str) -> bool:
        """
        Check if the path is public (doesn't require authentication).

        Args:
            path: Request path

        Returns:
            True if the path is public, False otherwise
        """
        # Check exact matches
        if path in PUBLIC_PATHS:
            return True

        # Check prefixes (like documentation paths)
        for public_path in PUBLIC_PATHS:
            if public_path.endswith("/") and path.startswith(public_path):
                return True
            if public_path == "/docs" and (path.startswith("/docs/") or path.startswith("/openapi")):
                return True
            if public_path == "/redoc" and path.startswith("/redoc/"):
                return True

        return False

    def _extract_token(self, auth_header: str) -> Optional[str]:
        """
        Extract token from Authorization header.

        Args:
            auth_header: Authorization header value

        Returns:
            Token string or None if invalid format
        """
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]
