from agno.agent import Agent
from agno.models.openai import OpenAIChat
from Opportunity_Discovery_Workflow.tools.sam_gov_tool import SamGovTools
from Opportunity_Discovery_Workflow.Models.data_models import OpportunityList
from Opportunity_Discovery_Workflow.Instructions.sam_gov_instructions import get_instructions

def get_agent(model_id="gpt-5.1-2025-11-13"):
    """
    Initializes and returns the SAM.gov Fetch Agent.
    
    This agent fetches opportunities from SAM.gov 
    posted in the last 7 days without any keyword filtering.
    """
    return Agent(
        name="Fetch_Agent_SAM_Gov",
        model=OpenAIChat(id=model_id, temperature=0, seed=42),
        tools=[SamGovTools()],
        instructions=get_instructions(),
        markdown=True,
        description="Fetches federal contract opportunities from SAM.gov posted in the last 7 days",
        output_schema=OpportunityList,
    )
