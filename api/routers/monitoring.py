"""
Health Check and Monitoring Endpoints for ORION Architekt AT

Implements:
- /health - System health check
- /health/ready - Readiness probe (Kubernetes)
- /health/live - Liveness probe (Kubernetes)
- /metrics - Prometheus metrics

Following REPOSITORY_CREATION_RULES.md Section XI and XXIII
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict

import psutil
from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse, PlainTextResponse

# Prometheus metrics
try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("prometheus_client not available - metrics endpoint disabled")

router = APIRouter(tags=["Monitoring"])
logger = logging.getLogger(__name__)

# Metrics (if Prometheus available)
if PROMETHEUS_AVAILABLE:
    request_count = Counter(
        "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
    )
    request_duration = Histogram(
        "http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"]
    )
    active_connections = Gauge("active_connections", "Number of active connections")
    database_connections = Gauge(
        "database_connections_active", "Number of active database connections"
    )
    cache_hits = Counter("cache_hits_total", "Total cache hits", ["cache_type"])
    cache_misses = Counter("cache_misses_total", "Total cache misses", ["cache_type"])


async def check_database() -> Dict[str, Any]:
    """Check database connectivity and performance."""
    try:
        from models import db

        start = time.time()
        result = await db.execute("SELECT 1")
        latency = time.time() - start

        return {
            "status": "healthy",
            "latency_ms": round(latency * 1000, 2),
            "details": "Database connection successful",
        }
    except ImportError as e:
        logger.warning(f"Database module not available: {e}")
        return {"status": "unknown", "details": "Database module not configured"}
    except Exception as e:
        logger.error(f"Database health check failed: {type(e).__name__}: {e}")
        return {"status": "unhealthy", "error": str(e), "details": "Database connection failed"}


async def check_redis() -> Dict[str, Any]:
    """Check Redis connectivity and performance."""
    try:
        import redis

        from api.middleware.rate_limit import redis_client

        if not redis_client:
            return {
                "status": "disabled",
                "details": "Redis not configured (using in-memory fallback)",
            }

        start = time.time()
        redis_client.ping()
        latency = time.time() - start

        info = redis_client.info("server")  # type: ignore[assignment]

        return {
            "status": "healthy",
            "latency_ms": round(latency * 1000, 2),
            "version": info.get("redis_version", "unknown"),  # type: ignore[union-attr]
            "uptime_days": round(info.get("uptime_in_seconds", 0) / 86400, 1),  # type: ignore[union-attr]
            "details": "Redis connection successful",
        }
    except ImportError:
        return {"status": "disabled", "details": "Redis module not available"}
    except redis.RedisError as e:
        logger.warning(f"Redis health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "details": "Redis connection failed - using in-memory fallback",
        }
    except Exception as e:
        logger.error(f"Unexpected error in Redis health check: {type(e).__name__}: {e}")
        return {"status": "unknown", "error": str(e)}


async def check_ifcopenshell() -> Dict[str, Any]:
    """Check ifcopenshell library availability."""
    try:
        import ifcopenshell

        return {
            "status": "healthy",
            "version": ifcopenshell.version,
            "details": "IFC processing available",
        }
    except ImportError:
        return {
            "status": "unavailable",
            "details": "ifcopenshell not installed - BIM processing disabled",
        }
    except Exception as e:
        logger.warning(f"ifcopenshell check failed: {type(e).__name__}: {e}")
        return {"status": "unknown", "error": str(e)}


async def get_system_metrics() -> Dict[str, Any]:
    """Get system resource metrics."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "cpu_percent": round(cpu_percent, 1),
            "memory_percent": round(memory.percent, 1),
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": round(disk.percent, 1),
            "disk_free_gb": round(disk.free / (1024**3), 2),
        }
    except Exception as e:
        logger.warning(f"System metrics collection failed: {e}")
        return {"error": "System metrics unavailable"}


@router.get(
    "/health",
    summary="Comprehensive health check",
    description="""
    Returns comprehensive system health status including:
    - Overall health status
    - Database connectivity
    - Redis connectivity
    - IFC processing availability
    - System resource metrics

    Returns 200 if healthy, 503 if any critical component is unhealthy.
    """,
    responses={
        200: {
            "description": "System is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2026-04-11T08:00:00Z",
                        "version": "1.0.0",
                        "checks": {
                            "database": {"status": "healthy", "latency_ms": 5.2},
                            "redis": {"status": "healthy", "latency_ms": 1.3},
                            "ifcopenshell": {"status": "healthy", "version": "0.8.4"},
                        },
                        "system": {
                            "cpu_percent": 15.3,
                            "memory_percent": 45.2,
                            "disk_percent": 38.5,
                        },
                    }
                }
            },
        },
        503: {"description": "System is unhealthy or degraded"},
    },
)
async def health_check():
    """Comprehensive health check for all system components."""

    # Perform all health checks
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "ifcopenshell": await check_ifcopenshell(),
    }

    # Get system metrics
    system_metrics = await get_system_metrics()

    # Determine overall status
    critical_components = ["database"]  # Components that must be healthy

    overall_status = "healthy"
    for component in critical_components:
        if checks[component]["status"] in ["unhealthy", "unknown"]:
            overall_status = "unhealthy"
            break
        elif checks[component]["status"] == "degraded":
            overall_status = "degraded"

    # Build response
    response_data = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "checks": checks,
        "system": system_metrics,
    }

    # Return appropriate status code
    status_code = 200 if overall_status == "healthy" else 503

    return JSONResponse(content=response_data, status_code=status_code)


@router.get(
    "/health/ready",
    summary="Readiness probe",
    description="""
    Kubernetes readiness probe endpoint.
    Returns 200 if the application is ready to serve traffic.

    Checks:
    - Database connectivity
    - Critical dependencies loaded

    Use for: Kubernetes readiness probes, load balancer health checks
    """,
    responses={
        200: {"description": "Application is ready"},
        503: {"description": "Application is not ready"},
    },
)
async def readiness_check():
    """Readiness probe for Kubernetes and load balancers."""

    # Check database
    db_check = await check_database()

    if db_check["status"] == "healthy":
        return Response(status_code=200, content="ready")
    else:
        return Response(status_code=503, content="not ready")


@router.get(
    "/health/live",
    summary="Liveness probe",
    description="""
    Kubernetes liveness probe endpoint.
    Returns 200 if the application is alive and not deadlocked.

    This is a lightweight check that doesn't verify external dependencies.

    Use for: Kubernetes liveness probes to detect deadlocked processes
    """,
    responses={200: {"description": "Application is alive"}},
)
async def liveness_check():
    """Liveness probe for Kubernetes."""
    return Response(status_code=200, content="alive")


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    description="""
    Prometheus metrics endpoint in text format.

    Metrics include:
    - HTTP request counts by method, endpoint, and status
    - Request duration histograms
    - Active connections gauge
    - Cache hit/miss rates
    - System resource utilization

    Configure Prometheus to scrape this endpoint.
    """,
    responses={
        200: {
            "description": "Prometheus metrics in text format",
            "content": {"text/plain": {"example": """# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/projects",status="200"} 1523.0
"""}},
        },
        503: {"description": "Prometheus not available"},
    },
)
async def metrics():
    """Prometheus metrics endpoint."""

    if not PROMETHEUS_AVAILABLE:
        return JSONResponse(
            content={
                "error": "Prometheus metrics not available",
                "details": "Install prometheus_client: pip install prometheus-client",
            },
            status_code=503,
        )

    # Generate Prometheus metrics
    metrics_output = generate_latest()

    return Response(content=metrics_output, media_type=CONTENT_TYPE_LATEST)


@router.get(
    "/health/detailed",
    summary="Detailed diagnostic information",
    description="""
    Detailed diagnostic information for troubleshooting.

    WARNING: This endpoint may expose sensitive system information.
    Should be restricted to admin users only in production.
    """,
    responses={200: {"description": "Detailed diagnostic information"}},
)
async def detailed_diagnostics():
    """Detailed diagnostic information for troubleshooting."""

    import platform
    import sys

    diagnostics = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "python": {
            "version": sys.version,
            "executable": sys.executable,
            "platform": platform.platform(),
        },
        "system": await get_system_metrics(),
        "health_checks": {
            "database": await check_database(),
            "redis": await check_redis(),
            "ifcopenshell": await check_ifcopenshell(),
        },
    }

    # Add package versions
    try:
        import pkg_resources

        installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        diagnostics["packages"] = {
            "fastapi": installed_packages.get("fastapi", "unknown"),
            "sqlalchemy": installed_packages.get("sqlalchemy", "unknown"),
            "redis": installed_packages.get("redis", "unknown"),
            "ifcopenshell": installed_packages.get("ifcopenshell", "unknown"),
            "pydantic": installed_packages.get("pydantic", "unknown"),
        }
    except Exception as e:
        logger.warning(f"Could not get package versions: {e}")
        diagnostics["packages"] = {"error": "Could not retrieve package versions"}

    return diagnostics
