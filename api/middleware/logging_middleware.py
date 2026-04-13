"""
Logging Middleware
Structured logging for all API requests
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
from typing import Callable
from orion_logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs all HTTP requests with structured data
    """

    async def dispatch(self, request: Request, call_next: Callable):
        # Start time
        start_time = time.time()

        # Generate request ID
        request_id = self._generate_request_id()
        request.state.request_id = request_id

        # Log request
        await self._log_request(request, request_id)

        # Process request
        try:
            response = await call_next(request)

            # Log response
            process_time = time.time() - start_time
            await self._log_response(request, response, process_time, request_id)

            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}s"

            return response

        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            await self._log_error(request, e, process_time, request_id)
            raise

    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid

        return str(uuid.uuid4())

    async def _log_request(self, request: Request, request_id: str):
        """Log incoming request"""
        # Get client info
        client_ip = self._get_client_ip(request)

        # Get user info if authenticated
        user_info = await self._get_user_info(request)

        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent"),
                "user_id": user_info.get("user_id") if user_info else None,
                "username": user_info.get("username") if user_info else None,
                "event_type": "http_request",
            },
        )

    async def _log_response(self, request: Request, response, process_time: float, request_id: str):
        """Log response"""
        logger.info(
            f"Response: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
                "event_type": "http_response",
            },
        )

        # Log slow requests
        if process_time > 1.0:  # 1 second threshold
            logger.warning(
                f"Slow request: {request.method} {request.url.path} took {process_time:.2f}s",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "process_time_ms": round(process_time * 1000, 2),
                    "event_type": "slow_request",
                },
            )

    async def _log_error(
        self, request: Request, error: Exception, process_time: float, request_id: str
    ):
        """Log error"""
        logger.error(
            f"Error: {request.method} {request.url.path} - {str(error)}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "process_time_ms": round(process_time * 1000, 2),
                "event_type": "http_error",
            },
            exc_info=True,
        )

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def _get_user_info(self, request: Request) -> dict:
        """Extract user info from request"""
        # Try to get from JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                import jwt
                import os

                token = auth_header.split(" ")[1]
                SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                return {"user_id": payload.get("user_id"), "username": payload.get("sub")}
            except jwt.InvalidTokenError as e:
                # Token invalid or expired - log without user context
                logger.debug(f"JWT decode failed in structured logging: {e}")
            except (IndexError, KeyError) as e:
                logger.debug(f"Malformed auth header: {e}")

        return {}


class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    Simplified access log in NCSA Common Log Format
    Compatible with standard log analysis tools
    """

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        # Common Log Format: IP - user [timestamp] "method path protocol" status size
        client_ip = self._get_client_ip(request)
        user = await self._get_username(request) or "-"
        timestamp = time.strftime("%d/%b/%Y:%H:%M:%S %z")
        method = request.method
        path = request.url.path
        protocol = f"HTTP/{request.scope.get('http_version', '1.1')}"
        status = response.status_code
        size = response.headers.get("content-length", "-")

        log_line = f'{client_ip} - {user} [{timestamp}] "{method} {path} {protocol}" {status} {size} "{process_time:.3f}"'
        logger.info(log_line)

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "-"

    async def _get_username(self, request: Request) -> str:
        """Get username from token"""
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                import jwt
                import os

                token = auth_header.split(" ")[1]
                SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                return payload.get("sub", "-")
            except jwt.InvalidTokenError:
                # Token invalid - anonymous user
                return "-"
            except (IndexError, KeyError):
                # Malformed header - anonymous user
                return "-"
        return None
