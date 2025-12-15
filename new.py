from agno.agent import Agent
from agno.tools.gmail import GmailTools
from dotenv import load_dotenv

load_dotenv()

agent = Agent(
    tools=[GmailTools(port=8004)],
    instructions="You are an email assistant that helps send emails."
)

# Send email with CC and attachments
agent.print_response(
    """Send an email with the following details:
    - To: kiran@sasi.ac.in
    - Subject: Project Update
    - Body: Please find the attached project report for this week.
    - Attachment: D:/Agno/crtical_minerals_news/outputs/critical_minerals_enhanced_20251201_123459.md
    """,
    markdown=True
)