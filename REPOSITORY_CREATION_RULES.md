# ORION ARCHITEKT AT - Immutable Repository Creation Rules
**Version:** 1.0.0
**Date:** 2026-04-11
**Status:** CANONICAL - These rules are MANDATORY for all code in this repository

---

## I. FUNDAMENTAL PRINCIPLES (Non-Negotiable)

### 1. Security First
```python
# RULE 1.1: NO hardcoded credentials EVER
# ❌ FORBIDDEN
DATABASE_URL = "postgresql://user:password@localhost/db"
API_KEY = "sk-1234567890"

# ✅ REQUIRED
import os
DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable required")
```

### 2. Error Handling
```python
# RULE 2.1: NO bare except statements
# ❌ FORBIDDEN
try:
    operation()
except:
    pass

# ✅ REQUIRED
try:
    operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    # Graceful degradation or re-raise
```

### 3. Logging
```python
# RULE 3.1: ALL errors must be logged
# ❌ FORBIDDEN
def process():
    try:
        return risky_operation()
    except Exception:
        return None

# ✅ REQUIRED
import logging
logger = logging.getLogger(__name__)

def process():
    try:
        return risky_operation()
    except ValueError as e:
        logger.error(f"Invalid value in process(): {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in process(): {e}")
        raise
```

---

## II. CODE QUALITY STANDARDS

### 4. Type Hints
```python
# RULE 4.1: ALL public functions MUST have type hints
# ❌ FORBIDDEN
def calculate_area(width, height):
    return width * height

# ✅ REQUIRED
from typing import Union

def calculate_area(width: float, height: float) -> float:
    """Calculate area from width and height.

    Args:
        width: Width in meters
        height: Height in meters

    Returns:
        Area in square meters

    Raises:
        ValueError: If width or height is negative
    """
    if width < 0 or height < 0:
        raise ValueError("Dimensions must be non-negative")
    return width * height
```

### 5. Documentation
```python
# RULE 5.1: ALL public functions MUST have docstrings
# RULE 5.2: Docstrings MUST include Args, Returns, Raises
# RULE 5.3: Use Google-style docstrings

def validate_oenorm_b1800(
    bgf: float,
    ngf: float,
    nrf: float
) -> dict:
    """Validate area calculations per ÖNORM B 1800.

    Checks relationships between BGF (Brutto-Grundfläche),
    NGF (Netto-Grundfläche), and NRF (Nutzfläche).

    Args:
        bgf: Gross floor area in m²
        ngf: Net floor area in m²
        nrf: Usable floor area in m²

    Returns:
        Dictionary with validation results:
        {
            "valid": bool,
            "errors": List[str],
            "warnings": List[str]
        }

    Raises:
        ValueError: If any area is negative

    Example:
        >>> validate_oenorm_b1800(1000.0, 850.0, 750.0)
        {'valid': True, 'errors': [], 'warnings': []}
    """
    pass
```

### 6. Input Validation
```python
# RULE 6.1: VALIDATE ALL user inputs
# RULE 6.2: SANITIZE ALL file paths
# RULE 6.3: VALIDATE ALL file uploads

from pathlib import Path
from orion_exceptions import InvalidDataError, MissingDataError

def process_ifc_file(file_path: str) -> dict:
    """Process IFC file with comprehensive validation."""

    # Validate file path
    if not file_path:
        raise MissingDataError("file_path")

    path = Path(file_path)

    # Security: Prevent directory traversal
    if ".." in file_path or not path.is_absolute():
        raise InvalidDataError("file_path", file_path, "absolute path")

    # Validate file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Validate file extension
    if path.suffix.lower() not in ['.ifc', '.ifcxml']:
        raise InvalidDataError("file_path", file_path, ".ifc or .ifcxml")

    # Validate file size (max 100MB)
    max_size = 100 * 1024 * 1024
    if path.stat().st_size > max_size:
        raise InvalidDataError("file_path", file_path, f"file < {max_size} bytes")

    return process_file(path)
```

---

## III. AUSTRIAN BUILDING STANDARDS COMPLIANCE

### 7. ÖNORM Implementation
```python
# RULE 7.1: ALL ÖNORM standards MUST be cited with version
# RULE 7.2: Standard compliance MUST be verifiable

def calculate_stellplaetze(
    bundesland: str,
    wohneinheiten: int,
    nutzflaeche_m2: float
) -> dict:
    """Calculate required parking spaces per Austrian building codes.

    Standards Applied:
    - Wien Bauordnung § 50 (2023)
    - OÖ Bauordnung § 45 (2022)
    - Tirol Bauordnung § 47 (2022)

    Args:
        bundesland: One of 9 Austrian Bundesländer
        wohneinheiten: Number of residential units
        nutzflaeche_m2: Commercial/office area in m²

    Returns:
        {
            "stellplaetze_wohnen": int,
            "stellplaetze_gewerbe": int,
            "total": int,
            "standard": str,  # e.g., "Wien Bauordnung § 50 (2023)"
            "calculation": str  # Human-readable calculation
        }
    """
    from orion_exceptions import validate_bundesland
    bundesland = validate_bundesland(bundesland)

    # Implementation with specific factors per Bundesland
    pass
```

### 8. OIB-RL Compliance
```python
# RULE 8.1: OIB-RL 1-6 checks MUST reference specific sections
# RULE 8.2: Compliance status MUST be: pass/fail/warning/info

def check_oib_rl_3_room_height(
    room_height_m: float,
    room_type: str
) -> dict:
    """Check room height per OIB-RL 3 Section 3.2.

    Reference: OIB-RL 3:2019 - Hygiene, Gesundheit und Umweltschutz
    Section 3.2: Mindesthöhen von Aufenthaltsräumen

    Requirements:
    - Habitable rooms: ≥ 2.50m
    - Kitchens: ≥ 2.50m
    - Bathrooms: ≥ 2.30m
    - Storage/utility: ≥ 2.10m

    Args:
        room_height_m: Room height in meters
        room_type: "habitable", "kitchen", "bathroom", "storage"

    Returns:
        {
            "status": "pass" | "fail" | "warning",
            "requirement": float,  # Required height
            "actual": float,       # Actual height
            "standard": "OIB-RL 3:2019 Section 3.2",
            "details": str
        }
    """
    requirements = {
        "habitable": 2.50,
        "kitchen": 2.50,
        "bathroom": 2.30,
        "storage": 2.10
    }

    required = requirements.get(room_type, 2.50)

    if room_height_m >= required:
        status = "pass"
        details = f"Height {room_height_m:.2f}m meets requirement ≥{required:.2f}m"
    else:
        status = "fail"
        details = f"Height {room_height_m:.2f}m below requirement ≥{required:.2f}m"

    return {
        "status": status,
        "requirement": required,
        "actual": room_height_m,
        "standard": "OIB-RL 3:2019 Section 3.2",
        "details": details
    }
```

---

## IV. API DESIGN PRINCIPLES

### 9. RESTful API Standards
```python
# RULE 9.1: Use standard HTTP status codes
# RULE 9.2: Return consistent JSON structure
# RULE 9.3: Include error details in responses

from fastapi import HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List

class APIResponse(BaseModel):
    """Standard API response structure."""
    success: bool
    data: Optional[dict] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

@router.post("/validate-compliance", response_model=APIResponse)
async def validate_compliance(request: ComplianceRequest):
    """Validate building compliance.

    Returns:
        200: Validation completed successfully
        400: Invalid request data
        422: Validation errors in input
        500: Internal server error
    """
    try:
        # Validate input
        if not request.bundesland:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="bundesland is required"
            )

        # Process
        results = perform_validation(request)

        return APIResponse(
            success=True,
            data=results,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

### 10. Authentication & Authorization
```python
# RULE 10.1: ALL API endpoints MUST be authenticated (except public docs)
# RULE 10.2: Use JWT tokens with expiration
# RULE 10.3: Implement rate limiting

from fastapi import Depends, Header
from jose import JWTError, jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

def get_current_user(authorization: str = Header(None)):
    """Validate JWT token and return current user.

    Raises:
        HTTPException: If token is invalid or expired
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        return user_id
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
```

---

## V. TESTING REQUIREMENTS

### 11. Test Coverage
```python
# RULE 11.1: MINIMUM 80% code coverage for core modules
# RULE 11.2: ALL public functions MUST have unit tests
# RULE 11.3: Integration tests for ALL API endpoints

import pytest
from unittest.mock import Mock, patch

def test_calculate_stellplaetze_wien():
    """Test parking space calculation for Vienna."""
    result = calculate_stellplaetze(
        bundesland="wien",
        wohneinheiten=10,
        nutzflaeche_m2=0
    )

    assert result["total"] >= 10  # Wien requires 1.0-1.5 per unit
    assert result["standard"] == "Wien Bauordnung § 50 (2023)"
    assert "calculation" in result
    assert result["stellplaetze_wohnen"] > 0

def test_calculate_stellplaetze_invalid_bundesland():
    """Test error handling for invalid Bundesland."""
    with pytest.raises(ValueError, match="Ungültiges Bundesland"):
        calculate_stellplaetze(
            bundesland="invalid",
            wohneinheiten=10,
            nutzflaeche_m2=0
        )

@pytest.mark.integration
async def test_api_validate_compliance():
    """Integration test for compliance validation API."""
    from httpx import AsyncClient
    from app import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/validate-compliance",
            json={
                "bundesland": "wien",
                "building_type": "mehrfamilienhaus",
                "floors": 4
            },
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
```

### 12. Performance Testing
```python
# RULE 12.1: API endpoints MUST respond within 2 seconds (95th percentile)
# RULE 12.2: Database queries MUST be optimized (< 100ms)
# RULE 12.3: Load test with 1000+ concurrent users

import pytest
import time

@pytest.mark.performance
def test_ifc_processing_performance():
    """Test IFC processing completes within time limit."""
    start = time.time()

    result = process_ifc_file("test_data/sample.ifc")

    duration = time.time() - start

    assert duration < 5.0, f"Processing took {duration:.2f}s (limit: 5s)"
    assert result["geometry_valid"] is True
```

---

## VI. DATABASE & PERSISTENCE

### 13. Database Design
```python
# RULE 13.1: Use SQLAlchemy ORM for database operations
# RULE 13.2: ALL models MUST have created_at and updated_at
# RULE 13.3: Use database migrations (Alembic)

from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Project(Base):
    """Building project model."""
    __tablename__ = "projects"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Required fields
    name = Column(String(255), nullable=False, index=True)
    bundesland = Column(String(50), nullable=False, index=True)

    # Optional fields
    description = Column(String(1000))
    total_area_m2 = Column(Float)

    # Audit fields (REQUIRED)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"
```

### 14. Data Validation
```python
# RULE 14.1: Validate ALL data before database insertion
# RULE 14.2: Use Pydantic for request/response validation

from pydantic import BaseModel, validator, Field

class ProjectCreate(BaseModel):
    """Request model for creating a project."""
    name: str = Field(..., min_length=3, max_length=255)
    bundesland: str
    description: str = Field(None, max_length=1000)
    total_area_m2: float = Field(None, gt=0, le=1000000)

    @validator('bundesland')
    def validate_bundesland(cls, v):
        """Validate Bundesland is one of 9 Austrian states."""
        valid = [
            "wien", "niederoesterreich", "oberoesterreich",
            "steiermark", "kaernten", "salzburg",
            "tirol", "vorarlberg", "burgenland"
        ]
        if v.lower() not in valid:
            raise ValueError(f"Invalid Bundesland. Must be one of: {', '.join(valid)}")
        return v.lower()

    class Config:
        schema_extra = {
            "example": {
                "name": "Wohnanlage Musterstraße",
                "bundesland": "wien",
                "description": "Mehrfamilienhaus mit 12 Wohneinheiten",
                "total_area_m2": 1250.5
            }
        }
```

---

## VII. DEPLOYMENT & OPERATIONS

### 15. Environment Configuration
```python
# RULE 15.1: ALL configuration via environment variables
# RULE 15.2: Provide .env.example with ALL variables
# RULE 15.3: Use pydantic Settings for config management

from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Application
    APP_NAME: str = "ORION Architekt AT"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # External APIs
    RIS_API_KEY: str = ""
    HORA_API_KEY: str = ""

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: list = [".ifc", ".ifcxml", ".pdf", ".dwg"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @validator('SECRET_KEY', 'JWT_SECRET_KEY')
    def validate_secrets(cls, v):
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 16. Logging Configuration
```python
# RULE 16.1: Use structured logging (JSON format in production)
# RULE 16.2: Include request ID in all logs
# RULE 16.3: Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON log formatter for production."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data)

def setup_logging():
    """Configure application logging."""
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)

    handler = logging.StreamHandler()

    if settings.ENVIRONMENT == "production":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

    logger.addHandler(handler)
```

---

## VIII. SECURITY REQUIREMENTS

### 17. Input Sanitization
```python
# RULE 17.1: SANITIZE ALL user inputs
# RULE 17.2: PREVENT SQL injection (use parameterized queries)
# RULE 17.3: PREVENT XSS (escape HTML)
# RULE 17.4: PREVENT path traversal

import html
import re
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal."""
    # Remove path components
    filename = Path(filename).name

    # Remove dangerous characters
    filename = re.sub(r'[^\w\s.-]', '', filename)

    # Limit length
    if len(filename) > 255:
        filename = filename[:255]

    return filename

def sanitize_html(text: str) -> str:
    """Escape HTML to prevent XSS."""
    return html.escape(text)

# ALWAYS use SQLAlchemy ORM or parameterized queries
# ❌ FORBIDDEN
query = f"SELECT * FROM users WHERE username = '{username}'"

# ✅ REQUIRED
query = "SELECT * FROM users WHERE username = :username"
result = db.execute(query, {"username": username})
```

### 18. Rate Limiting
```python
# RULE 18.1: Implement rate limiting on ALL API endpoints
# RULE 18.2: Different limits for authenticated vs anonymous
# RULE 18.3: Return 429 Too Many Requests when exceeded

from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/upload-ifc")
@limiter.limit("10/minute")  # 10 uploads per minute per IP
async def upload_ifc(request: Request, file: UploadFile):
    """Upload IFC file with rate limiting."""
    pass
```

---

## IX. DOCUMENTATION REQUIREMENTS

### 19. API Documentation
```python
# RULE 19.1: ALL endpoints MUST have OpenAPI documentation
# RULE 19.2: Include examples for ALL requests/responses
# RULE 19.3: Document ALL possible error codes

from fastapi import FastAPI

app = FastAPI(
    title="ORION Architekt AT API",
    description="Austrian Building Compliance Validation API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_tags=[
        {
            "name": "BIM",
            "description": "BIM/IFC file processing and validation"
        },
        {
            "name": "Compliance",
            "description": "Austrian building code compliance checks"
        }
    ]
)

@router.post(
    "/validate-compliance",
    tags=["Compliance"],
    summary="Validate building compliance",
    description="""
    Comprehensive validation against Austrian building codes:
    - OIB-RL 1-6 compliance
    - ÖNORM standards (B 1600, B 1800, etc.)
    - Bundesland-specific requirements
    """,
    responses={
        200: {
            "description": "Validation completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "overall_status": "pass",
                            "checks": [
                                {
                                    "check": "Room Height",
                                    "status": "pass",
                                    "standard": "OIB-RL 3:2019"
                                }
                            ]
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid request data"},
        422: {"description": "Validation errors"},
        500: {"description": "Internal server error"}
    }
)
async def validate_compliance(request: ComplianceRequest):
    pass
```

### 20. README & Guides
```markdown
# RULE 20.1: README MUST include:
# - Project description and features
# - Installation instructions (all platforms)
# - Quick start guide
# - API documentation link
# - License information
# - Contributing guidelines

# RULE 20.2: Provide platform-specific installation guides
# RULE 20.3: Include troubleshooting section
```

---

## X. PERFORMANCE & SCALABILITY

### 21. Caching Strategy
```python
# RULE 21.1: Cache expensive computations
# RULE 21.2: Use Redis for distributed caching
# RULE 21.3: Set appropriate TTL for cached data

from functools import lru_cache
import redis
import json

redis_client = redis.from_url(settings.REDIS_URL)

def cache_result(key: str, ttl: int = 3600):
    """Decorator for caching function results in Redis."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Try to get from cache
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)

            # Compute result
            result = func(*args, **kwargs)

            # Store in cache
            redis_client.setex(key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator

@cache_result(key="stellplatz:wien", ttl=86400)  # 24 hours
def get_stellplatz_requirements_wien():
    """Get parking requirements for Vienna (cached)."""
    # Expensive computation or API call
    return compute_requirements()
```

### 22. Database Optimization
```python
# RULE 22.1: Use database indexes on frequently queried fields
# RULE 22.2: Optimize N+1 queries with eager loading
# RULE 22.3: Use connection pooling

from sqlalchemy.orm import joinedload

# ❌ FORBIDDEN (N+1 query problem)
projects = session.query(Project).all()
for project in projects:
    print(project.compliance_checks)  # Separate query for each project

# ✅ REQUIRED (Single query with JOIN)
projects = session.query(Project)\
    .options(joinedload(Project.compliance_checks))\
    .all()
```

---

## XI. MONITORING & OBSERVABILITY

### 23. Health Checks
```python
# RULE 23.1: Implement /health endpoint
# RULE 23.2: Check database, Redis, external APIs
# RULE 23.3: Return 200 if healthy, 503 if degraded

@router.get("/health")
async def health_check():
    """System health check."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Check database
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.error(f"Database health check failed: {e}")

    # Check Redis
    try:
        redis_client.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = "unhealthy"
        logger.warning(f"Redis health check failed: {e}")

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)
```

### 24. Metrics & Telemetry
```python
# RULE 24.1: Track key metrics (request count, latency, errors)
# RULE 24.2: Use Prometheus metrics format
# RULE 24.3: Expose /metrics endpoint

from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track metrics for all requests."""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    request_count.labels(method=request.method, endpoint=request.url.path).inc()
    request_duration.observe(duration)

    return response

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type="text/plain")
```

---

## XII. CONTINUOUS INTEGRATION / DEPLOYMENT

### 25. CI/CD Pipeline
```yaml
# RULE 25.1: ALL commits MUST pass CI checks
# RULE 25.2: Run tests, linting, security scans
# RULE 25.3: Automated deployment to staging

# .github/workflows/ci.yml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov black flake8 mypy

      - name: Linting
        run: |
          black --check .
          flake8 .
          mypy .

      - name: Security scan
        run: |
          pip install bandit safety
          bandit -r .
          safety check

      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## COMPLIANCE CHECKLIST

Before committing ANY code, verify:

- [ ] ✅ No hardcoded credentials
- [ ] ✅ All exceptions handled specifically
- [ ] ✅ All errors logged
- [ ] ✅ Type hints on all public functions
- [ ] ✅ Docstrings with Args/Returns/Raises
- [ ] ✅ Input validation and sanitization
- [ ] ✅ ÖNORM/OIB-RL standards cited correctly
- [ ] ✅ Unit tests with 80%+ coverage
- [ ] ✅ Integration tests for API endpoints
- [ ] ✅ API documentation complete
- [ ] ✅ Database models have audit fields
- [ ] ✅ Configuration via environment variables
- [ ] ✅ Structured logging implemented
- [ ] ✅ Rate limiting on endpoints
- [ ] ✅ Health check endpoint
- [ ] ✅ CI/CD pipeline passing

---

## ENFORCEMENT

**These rules are IMMUTABLE and MANDATORY.**

Any code that violates these rules MUST be rejected in code review.

**Automation:**
- Pre-commit hooks enforce formatting and linting
- CI pipeline blocks merges if tests fail
- Security scans flag vulnerabilities
- Code coverage must be ≥ 80%

**Consequences of Violation:**
1. Pull request rejected
2. CI/CD pipeline fails
3. Code cannot be deployed to production

---

**Document Version:** 1.0.0
**Last Updated:** 2026-04-11
**Status:** CANONICAL - IMMUTABLE
**Authority:** ORION Architekt AT Project Lead
