from workflows import enhanced_workflow


def main():
    """Main function to run the enhanced workflow."""
    print("=" * 70)
    print("ENHANCED CRITICAL MINERALS NEWS DISCOVERY WORKFLOW")
    print("=" * 70)
    
    # Run the enhanced workflow with a comprehensive query
    enhanced_workflow.print_response(
        input="Latest developments in critical minerals: lithium, cobalt, rare earths, and mining industry",
        additional_data={
            "original_query": "critical minerals lithium cobalt rare earth elements mining"
        },
        markdown=True,
    )
    
    print()
    print("-" * 70)
    print("Workflow completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
