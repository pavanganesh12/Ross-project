"""
Entry point for running the FastAPI application.

Run with: python run_api.py
Or with uvicorn: uvicorn api.app:app --reload --host 0.0.0.0 --port 8001
"""
import os
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Run the FastAPI application."""
    # Configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8001"))  # Different port from Opportunity Discovery API
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    log_level = os.getenv("API_LOG_LEVEL", "info")
    
    print("=" * 60)
    print("CRITICAL MINERALS NEWS API")
    print("=" * 60)
    print(f"Starting server on http://{host}:{port}")
    print(f"Documentation: http://{host}:{port}/docs")
    print(f"ReDoc: http://{host}:{port}/redoc")
    print(f"OpenAPI JSON: http://{host}:{port}/openapi.json")
    print("=" * 60)
    
    # Run the server
    uvicorn.run(
        "api.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


if __name__ == "__main__":
    main()
