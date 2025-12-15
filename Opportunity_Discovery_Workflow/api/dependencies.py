"""
Dependency Injection for FastAPI.

Provides reusable dependencies for route handlers.
"""
from typing import Generator
from functools import lru_cache

from .services.opportunity_service import OpportunityService
from .services.workflow_service import WorkflowService
from .services.keyword_service import KeywordService
from .config import Settings, get_settings


# Service dependencies using dependency injection pattern
@lru_cache()
def get_opportunity_service() -> OpportunityService:
    """Get cached OpportunityService instance."""
    return OpportunityService()


@lru_cache()
def get_workflow_service() -> WorkflowService:
    """Get cached WorkflowService instance."""
    return WorkflowService()


@lru_cache()
def get_keyword_service() -> KeywordService:
    """Get cached KeywordService instance."""
    return KeywordService()


def get_settings_dependency() -> Settings:
    """Dependency for injecting settings into route handlers."""
    return get_settings()
