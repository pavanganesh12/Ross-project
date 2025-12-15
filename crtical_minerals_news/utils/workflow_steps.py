"""Workflow step functions for critical minerals news discovery."""

from textwrap import dedent
from datetime import datetime
import re
from pathlib import Path
from agno.workflow.types import StepInput, StepOutput


def prepare_search_queries(step_input: StepInput) -> StepOutput:
    """Prepare search queries for all platforms."""
    topic = step_input.input
    return StepOutput(content=dedent(f"""\
        Search Topic: {topic}
        
        Search across: NEWS, TWITTER, LINKEDIN
        Focus on recent, relevant content about critical minerals.
    """))


def search_news(step_input: StepInput) -> StepOutput:
    """Search news sources."""
    return StepOutput(content=dedent(f"""\
        {step_input.previous_step_content}
        
        SEARCH NEWS SOURCES for critical minerals information.
    """))


def search_twitter(step_input: StepInput) -> StepOutput:
    """Search Twitter."""
    base_topic = step_input.input or "critical minerals"
    return StepOutput(content=dedent(f"""\
        SEARCH TWITTER for: {base_topic}
        Focus on: expert tweets, breaking news, market sentiment.
    """))


def search_linkedin(step_input: StepInput) -> StepOutput:
    """Search LinkedIn."""
    base_topic = step_input.input or "critical minerals"
    return StepOutput(content=dedent(f"""\\
        SEARCH LINKEDIN for: {base_topic}
        Focus on: industry insights, company announcements, thought leadership.
    """))


def search_csis(step_input: StepInput) -> StepOutput:
    """Search CSIS."""
    base_topic = step_input.input or "critical minerals"
    return StepOutput(content=dedent(f"""\\
        SEARCH CSIS for: {base_topic}
        Focus on: deep analysis, reports, and policy briefs.
    """))


def aggregate_results(step_input: StepInput) -> StepOutput:
    """Aggregate results from all sources using proper step access methods."""
    
    # Use get_step_content to access each search agent's output by step name
    news_results = step_input.get_step_content("news_search") or ""
    twitter_results = step_input.get_step_content("twitter_search") or ""
    linkedin_results = step_input.get_step_content("linkedin_search") or ""
    csis_results = step_input.get_step_content("csis_search") or ""
    
    # Fallback: if get_step_content doesn't work, try get_all_previous_content
    if not any([news_results, twitter_results, linkedin_results, csis_results]):
        all_content = step_input.get_all_previous_content() or ""
        if all_content:
            # Use all previous content as a single block
            return StepOutput(content=dedent(f"""\
                AGGREGATE AND PROCESS ALL SEARCH RESULTS BELOW:
                
                {all_content}
                
                Tasks: 
                1. Merge ALL content into a single unified list of insights.
                2. Do NOT separate by source type in the output.
                3. Deduplicate rigorously.
                4. Preserve ALL source URLs for citation.
            """))
    
    return StepOutput(content=dedent(f"""\
        AGGREGATE search results from ALL sources:
        
        === NEWS SEARCH RESULTS ===
        {news_results}
        
        === TWITTER SEARCH RESULTS ===
        {twitter_results}
        
        === LINKEDIN SEARCH RESULTS ===
        {linkedin_results}

        === CSIS RESEARCH RESULTS ===
        {csis_results}
        
        Tasks: 
        1. Merge ALL content into a single unified list of insights.
        2. Do NOT separate by source type in the output.
        3. Deduplicate rigorously.
        4. Preserve ALL source URLs for citation.
    """))



def format_report(step_input: StepInput) -> StepOutput:
    """Format the final report."""
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return StepOutput(content=dedent(f"""\
        CREATE MARKDOWN REPORT
        Date: {current_date}
        
        Content: {step_input.previous_step_content}
        
        Include:
        - A single unified list of insights (1, 2, 3...)
        - NO separation by source type (News/Twitter/LinkedIn/CSIS mixed together)
        - APA Style Citations at the bottom
        - Inline citations: [Source Name](URL)
    """))


def save_enhanced_report(step_input: StepInput) -> StepOutput:
    """Save the enhanced report."""
    report_content = step_input.previous_step_content
    
    if not report_content or len(report_content.strip()) < 100:
        return StepOutput(content="Error: Report content empty or incomplete.", success=False, error="Report content empty or incomplete")

    utc_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    header = f"**Generated on:** {utc_now} UTC"
    
    pattern = r"(^\*\*Generated on:\*\*).*$"
    new_content = re.sub(pattern, header, report_content, flags=re.MULTILINE)
    
    if new_content == report_content:
        lines = report_content.splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith("# "):
                lines.insert(i + 1, header)
                break
        report_content = "\n".join(lines)
    else:
        report_content = new_content
    
    output_dir = Path(__file__).parent.parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"critical_minerals_enhanced_{timestamp}.md"
    filepath = output_dir / filename
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        return StepOutput(
            content=f"Report saved: {filename}\nLocation: {filepath}\nFILEPATH:{filepath}",
            success=True
        )
    except Exception as e:
        return StepOutput(content=f"Error saving report: {e}", success=False, error=str(e))


def convert_to_pdf(step_input: StepInput) -> StepOutput:
    """Convert the saved markdown report to PDF."""
    from .md_to_pdf_converter import MarkdownToPdfConverter
    import re
    
    md_filepath = None
    
    # Extract filepath from previous step content
    if step_input.previous_step_content:
        match = re.search(r'FILEPATH:(.+?)(?:\n|$)', str(step_input.previous_step_content))
        if match:
            md_filepath = match.group(1).strip()
    
    if not md_filepath:
        output_dir = Path(__file__).parent.parent / "outputs"
        md_files = sorted(output_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
        if md_files:
            md_filepath = str(md_files[0])
    
    if not md_filepath:
        return StepOutput(content="Error: No markdown file found.", success=False, error="No markdown file found")
    
    md_path = Path(md_filepath)
    pdf_filepath = md_path.with_suffix('.pdf')
    
    try:
        converter = MarkdownToPdfConverter()
        if converter.convert(str(md_path), str(pdf_filepath)):
            return StepOutput(
                content=f"PDF generated: {pdf_filepath.name}\nPDF Location: {pdf_filepath}",
                success=True
            )
        else:
            return StepOutput(content="PDF conversion failed.", success=False, error="Conversion returned False")
    except Exception as e:
        return StepOutput(content=f"Error converting to PDF: {e}", success=False, error=str(e))
