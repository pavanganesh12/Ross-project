import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Opportunity_Discovery_Workflow.Workflows.discovery_workflow import DiscoveryWorkflow

def main():

    load_dotenv()

    try:
        workflow = DiscoveryWorkflow()
        workflow.run()
    except Exception as e:
        print(f"An error occurred while running the workflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
