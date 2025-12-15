import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from dotenv import load_dotenv

load_dotenv()


def main():
    """Run the FastAPI application."""
    # Configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    workers = int(os.getenv("API_WORKERS", "1"))
    log_level = os.getenv("API_LOG_LEVEL", "info")
    
    print("=" * 60)
    print("OPPORTUNITY DISCOVERY API")
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
        workers=workers if not reload else 1,
        log_level=log_level,
    )


if __name__ == "__main__":
    main()
