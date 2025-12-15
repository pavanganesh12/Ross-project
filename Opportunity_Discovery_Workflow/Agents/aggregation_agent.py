"""Aggregation Agent - Merges and deduplicates opportunities from domain agents."""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from Opportunity_Discovery_Workflow.Models.data_models import OpportunityList
from Opportunity_Discovery_Workflow.Instructions.aggregation_instructions import aggregation_instructions

def get_agent(model_id="gpt-5.1-2025-11-13"):
    """
    Initializes and returns the Aggregation Agent.
    
    This agent merges opportunities from multiple domain agents,
    removes duplicates, and enriches descriptions.
    """
    return Agent(
        name="Aggregation_Agent",
        model=OpenAIChat(id=model_id, temperature=0, seed=42),
        instructions=aggregation_instructions,
        markdown=True,
        description="Merges opportunities from domain agents, removes duplicates, and enriches descriptions",
        output_schema=OpportunityList,
    )
