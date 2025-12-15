"""
FastAPI Application Configuration and Setup.

This module configures the FastAPI application with all routes,
middleware, exception handlers, and startup/shutdown events.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

from .routes import (
    opportunities_router,
    workflows_router,
    keywords_router,
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
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Opportunity Discovery API...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Ensure output directory exists
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_path, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info("API startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Opportunity Discovery API...")
    logger.info("API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Opportunity Discovery API",
    description="""
## Opportunity Discovery Workflow API

This API provides endpoints for discovering, filtering, scoring, and managing
federal grant and contract opportunities from multiple government sources.

### Features

- **Opportunities**: Browse, filter, and manage discovered opportunities
- **Workflows**: Execute and monitor discovery workflows
- **Keywords**: Manage keyword domains for filtering opportunities
- **Reports**: Access generated markdown reports

### Data Sources

- Simpler.Grants.gov
- Grants.gov
- SAM.gov

### Workflow Phases

1. **Fetch**: Retrieve opportunities from configured sources
2. **Aggregate**: Deduplicate and merge similar opportunities
3. **Filter**: Apply keyword-based filtering by domain
4. **Score**: AI-powered scoring based on feasibility, impact, and alignment
5. **Report**: Generate comprehensive markdown reports
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
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
            "message": str(exc) if os.getenv("DEBUG") else "An unexpected error occurred",
            "timestamp": datetime.now().isoformat(),
        },
    )


# Include routers
app.include_router(health_router)
app.include_router(opportunities_router)
app.include_router(workflows_router)
app.include_router(keywords_router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Opportunity Discovery API",
        "version": "1.0.0",
        "description": "API for discovering and managing federal grant opportunities",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "opportunities": "/opportunities",
            "workflows": "/workflows",
            "keywords": "/keywords",
        },
    }
