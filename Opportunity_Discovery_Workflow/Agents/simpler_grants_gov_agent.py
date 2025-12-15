from agno.agent import Agent
from agno.models.openai import OpenAIChat
from Opportunity_Discovery_Workflow.Models.data_models import OpportunityList
from Opportunity_Discovery_Workflow.tools.simpler_grants_gov_tool import SimplerGrantsGovTools
from Opportunity_Discovery_Workflow.Instructions.simpler_grants_gov_instructions import get_instructions

def get_agent(model_id="gpt-5.1-2025-11-13"):
    """
    Initializes and returns the Simpler.Grants.gov Fetch Agent.
    
    This agent fetches opportunities from Simpler.Grants.gov 
    posted in the last 7 days without any keyword filtering.
    """
    return Agent(
        name="Fetch_Agent_Simpler",
        model=OpenAIChat(id=model_id, temperature=0, seed=42),
        tools=[SimplerGrantsGovTools()],
        instructions=get_instructions(),
        markdown=True,
        description="Fetches federal grant opportunities from Simpler.Grants.gov posted in the last 7 days",
        output_schema=OpportunityList,
    )
