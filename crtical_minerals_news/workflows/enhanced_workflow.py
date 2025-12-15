"""
Enhanced Critical Minerals News Discovery Workflow

Multi-category search across news, Twitter, and LinkedIn with aggregation and formatting.
"""

from agno.workflow.workflow import Workflow
from agno.workflow.step import Step
from agents import (
    news_search_agent,
    twitter_search_agent,
    linkedin_search_agent,
    csis_search_agent,
    aggregation_agent,
    formatting_agent,
)
from utils import (
    prepare_search_queries,
    aggregate_results,
    format_report,
    save_enhanced_report,
    convert_to_pdf,
)


# Create Enhanced Workflow with named Steps
enhanced_workflow = Workflow(
    name="Enhanced Critical Minerals News Discovery",
    description="Multi-category search across news, Twitter, and LinkedIn with PDF output",
    steps=[
        Step(name="prepare_queries", executor=prepare_search_queries),
        Step(name="news_search", agent=news_search_agent),
        Step(name="twitter_search", agent=twitter_search_agent),
        Step(name="linkedin_search", agent=linkedin_search_agent),
        Step(name="csis_search", agent=csis_search_agent),
        Step(name="aggregate_results", executor=aggregate_results),
        Step(name="aggregation_agent", agent=aggregation_agent),
        Step(name="format_report", executor=format_report),
        Step(name="formatting_agent", agent=formatting_agent),
        Step(name="save_report", executor=save_enhanced_report),
        Step(name="convert_pdf", executor=convert_to_pdf),
    ],
)
