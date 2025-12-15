import os
import sys
from dotenv import load_dotenv

# Add the parent directory to sys.path to allow imports from the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Opportunity_Discovery_Workflow.Workflows.discovery_workflow import DiscoveryWorkflow

# Load environment variables
load_dotenv()

def main():
    workflow = DiscoveryWorkflow()
    workflow.run()

if __name__ == "__main__":
    main()
