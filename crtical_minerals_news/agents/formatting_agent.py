from agno.agent import Agent
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

from instructions import FORMATTING_AGENT_INSTRUCTIONS

load_dotenv()

formatting_agent = Agent(
    name="Report Formatting Agent",
    model=OpenAIChat(id="gpt-5.1-2025-11-13", temperature=0.2, seed=42),
    role="Format aggregated content into a professional markdown report",
    instructions=FORMATTING_AGENT_INSTRUCTIONS,
    markdown=True,
)
