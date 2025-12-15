from agno.agent import Agent
from agno.models.openai import OpenAIChat
from Opportunity_Discovery_Workflow.Models.data_models import ScoredOpportunityList
from Opportunity_Discovery_Workflow.Instructions.scoring_instructions import scoring_instructions

def get_agent(model_id="gpt-5.1-2025-11-13"):
    """
    Initializes and returns the Scoring Agent.
    """
    return Agent(
        name="Scoring_Agent",
        model=OpenAIChat(id=model_id, temperature=0, seed=42),
        instructions=scoring_instructions,
        markdown=True,
        reasoning=True,
        structured_outputs=True,
        output_schema=ScoredOpportunityList,
    )
