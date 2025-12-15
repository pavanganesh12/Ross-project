from agno.agent import Agent
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

from instructions import AGGREGATION_AGENT_INSTRUCTIONS

load_dotenv()

aggregation_agent = Agent(
    name="Content Aggregation Agent",
    model=OpenAIChat(id="gpt-5.1-2025-11-13", temperature=0.2, seed=42),
    role="Aggregate and organize content from multiple sources",
    instructions=AGGREGATION_AGENT_INSTRUCTIONS,
    markdown=True,
)
