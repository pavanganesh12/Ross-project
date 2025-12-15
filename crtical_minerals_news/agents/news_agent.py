from datetime import datetime, timedelta
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools
from dotenv import load_dotenv

from instructions import NEWS_AGENT_INSTRUCTIONS

load_dotenv()

# Get date for 7 days ago
start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

news_search_agent = Agent(
    name="News Search Agent",
    model=OpenAIChat(id="gpt-5.1-2025-11-13", temperature=0.2, seed=42),
    tools=[
        ExaTools(
            category="news",
            num_results=20,
            api_key='47f17539-8154-4177-9da2-aab9af9b9495',
            show_results=True,
            use_autoprompt=True,
            start_published_date=start_date,
            text=True,
            text_length_limit=3000,  # Increased from default 1000 to capture more content
            highlights=True,  # Include highlighted snippets for key content
            livecrawl="always",  # Always fetch fresh content from pages
        )
    ],
    role="Search news sites for official articles and press releases about critical minerals",
    instructions=NEWS_AGENT_INSTRUCTIONS,
    markdown=True,
)
