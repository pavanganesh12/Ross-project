import os
from pathlib import Path
from agno.agent import Agent
from agno.tools.file import FileTools
from agno.models.openai import OpenAIChat
from agno.tools.file_generation import FileGenerationTools
from Opportunity_Discovery_Workflow.Instructions.report_instructions import report_instructions


def get_agent(model_id="gpt-5.1-2025-11-13"):
    """
    Initializes and returns the Report Agent.
    """
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Output directory
    output_dir = os.path.join(base_path, "outputs")

    return Agent(
        name="Report_Agent",
        model=OpenAIChat(id=model_id, temperature=0, seed=42),
        instructions=report_instructions,
        tools=[FileTools(base_dir=Path(output_dir)), FileGenerationTools(output_directory=output_dir)],
        markdown=True,
    )
