from agno.agent import Agent
from agno.models.openai import OpenAIChat
from Opportunity_Discovery_Workflow.Models.data_models import OpportunityList
from Opportunity_Discovery_Workflow.Instructions.filter_instructions import get_filter_instructions

def get_agent(model_id="gpt-5.1-2025-11-13"):
    """
    Initializes and returns the Filter Agent.
    
    This agent filters opportunities based on keywords from 6 domains
    defined in keywords.json and assigns appropriate sectors.
    """
    return Agent(
        name="Filter_Agent",
        model=OpenAIChat(id=model_id, temperature=0, seed=42),
        instructions=get_filter_instructions(),
        markdown=True,
        description="Filters opportunities by domains/keywords and assigns sectors",
        output_schema=OpportunityList,
    )

