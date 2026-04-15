"""
ORION Architekt-AT - Main entry point for the FastAPI application.

For production deployment, use:
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

For development:
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
"""
import sys
import os

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.main import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENVIRONMENT", "production") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )
