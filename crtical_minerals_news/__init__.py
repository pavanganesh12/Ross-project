"""
Critical Minerals News Discovery Workflow Package

This package provides an enhanced workflow for discovering and reporting on critical minerals news
using the Agno framework with ExaSearch tools across multiple sources (News, Twitter, LinkedIn).

Usage:
    from crtical_minerals_news.workflows import enhanced_workflow
    
    enhanced_workflow.print_response(
        "Latest lithium mining news",
        markdown=True
    )
"""

__version__ = "2.0.0"
__author__ = "Agno User"
__description__ = "Critical Minerals News Discovery using Agno Framework"

# Import main components for easy access
try:
    from .workflows import enhanced_workflow
    from .config import WorkflowConfig, SEARCH_QUERIES
    
    __all__ = [
        "enhanced_workflow",
        "WorkflowConfig",
        "SEARCH_QUERIES",
    ]
except ImportError:
    # Fallback if imports fail (e.g., dependencies not installed)
    __all__ = []
