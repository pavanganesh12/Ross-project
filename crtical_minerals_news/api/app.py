"""
FastAPI Application Configuration and Setup.

Critical Minerals News Discovery API
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .routes import (
    workflows_router,
    reports_router,
    config_router,
    health_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Critical Minerals News API...")
    
    # Ensure output directory exists
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_path, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info("API startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Critical Minerals News API...")
    logger.info("API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Critical Minerals News API",
    description="""
## Critical Minerals News Discovery API

This API provides endpoints for discovering, aggregating, and managing
news about critical minerals from multiple sources.

### Features

- **Workflows**: Execute news discovery workflows across News, Twitter, and LinkedIn
- **Reports**: Access and manage generated markdown reports
- **Configuration**: View and customize search settings

### Data Sources

- **News**: Official articles and press releases
- **Twitter/X**: Real-time discussions and expert opinions
- **LinkedIn**: Professional insights and industry analysis

### Search Presets

- `general` - Broad critical minerals coverage
- `lithium` - Lithium-focused news
- `geopolitics` - Supply chain security and international competition
- `sustainability` - Environmental impact and green mining
- `market` - Prices, supply/demand, and investments
- `technology` - Mining and processing innovations
- `supply_chain` - Logistics and distribution
- `policy` - Government regulations and policies

### Workflow Phases

1. **Prepare**: Setup search queries for all platforms
2. **News Search**: Search news sites for articles
3. **Twitter Search**: Search Twitter for discussions
4. **LinkedIn Search**: Search LinkedIn for professional content
5. **Aggregate**: Combine and deduplicate results
6. **Format**: Generate professional markdown report
7. **Save**: Save report to outputs directory
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed response."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation Error",
            "errors": errors,
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal Server Error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat(),
        },
    )


# Include routers
app.include_router(health_router)
app.include_router(workflows_router)
app.include_router(reports_router)
app.include_router(config_router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Critical Minerals News API",
        "version": "1.0.0",
        "description": "API for discovering critical minerals news across multiple sources",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "workflows": "/workflows",
            "reports": "/reports",
            "config": "/config",
        },
        "quick_start": {
            "start_workflow": "POST /workflows/quick",
            "use_preset": "POST /workflows/preset/{preset_name}",
            "view_reports": "GET /reports",
            "get_latest": "GET /reports/latest",
        },
    }
