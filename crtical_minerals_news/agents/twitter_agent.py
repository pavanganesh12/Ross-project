from datetime import datetime, timedelta
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools
from dotenv import load_dotenv

from instructions import TWITTER_AGENT_INSTRUCTIONS

load_dotenv()

# Get date for 7 days ago
start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

twitter_search_agent = Agent(
    name="Twitter Search Agent",
    model=OpenAIChat(id="gpt-5.1-2025-11-13", temperature=0.2, seed=42),
    tools=[
        ExaTools(
            category="tweet",
            num_results=20,
            api_key='47f17539-8154-4177-9da2-aab9af9b9495',
            show_results=True,
            use_autoprompt=True,
            start_published_date=start_date,
            text=True,
            text_length_limit=2000,  # Increased for fuller tweet threads
            highlights=True,  # Include highlighted snippets
            livecrawl="always",  # Always fetch fresh content
        )
    ],
    role="Search Twitter for real-time discussions and expert opinions about critical minerals",
    instructions=TWITTER_AGENT_INSTRUCTIONS,
    markdown=True,
)
