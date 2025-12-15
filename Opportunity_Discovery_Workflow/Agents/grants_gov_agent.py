from agno.agent import Agent
from agno.models.openai import OpenAIChat
from Opportunity_Discovery_Workflow.Models.data_models import OpportunityList
from Opportunity_Discovery_Workflow.tools.grants_gov_tool import GrantsGovTools
from Opportunity_Discovery_Workflow.Instructions.grants_gov_instructions import get_instructions

def get_agent(model_id="gpt-5.1-2025-11-13"):
    """
    Initializes and returns the Grants.gov Fetch Agent.
    
    This agent fetches opportunities from Grants.gov 
    posted in the last 7 days without any keyword filtering.
    """
    return Agent(
        name="Fetch_Agent_Grants_Gov",
        model=OpenAIChat(id=model_id, temperature=0, seed=42),
        tools=[GrantsGovTools()],
        instructions=get_instructions(),
        markdown=True,
        description="Fetches federal grant opportunities from Grants.gov posted in the last 7 days",
        output_schema=OpportunityList,
    )
