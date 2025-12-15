from pathlib import Path
from .text_processing import normalize_unicode_characters
from .pdf_templates import PDF_TEMPLATE


class MarkdownToPdfConverter:
    """Converts markdown files to PDF using xhtml2pdf."""
    
    def convert(self, input_file, output_file=None):
        """Convert markdown file to PDF."""
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"✗ Input file not found: {input_file}")
            return False
        
        if input_path.suffix.lower() != '.md':
            print(f"✗ Input must be a markdown file: {input_file}")
            return False
        
        if output_file is None:
            output_file = str(input_path.with_suffix('.pdf'))
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import markdown
            from xhtml2pdf import pisa
            
            with open(input_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Normalize Unicode characters to prevent square boxes in PDF
            md_content = normalize_unicode_characters(md_content)
            
            html_content = markdown.markdown(
                md_content,
                extensions=['tables', 'toc', 'fenced_code', 'extra']
            )
            
            # Create styled HTML document
            styled_html = PDF_TEMPLATE.format(html_content=html_content)
            
            with open(output_file, "wb") as pdf_file:
                pisa_status = pisa.CreatePDF(styled_html, dest=pdf_file, encoding='utf-8')
            
            if pisa_status.err:
                print(f"✗ PDF creation error: {pisa_status.err}")
                return False
            
            print(f"✓ PDF created: {output_file}")
            return True
            
        except ImportError as e:
            print(f"✗ Missing library: {e}. Install with: pip install markdown xhtml2pdf")
            return False
        except Exception as e:
            print(f"✗ Conversion failed: {e}")
            return False


def convert_md_to_pdf(md_filepath, pdf_filepath=None):
    """Convert markdown file to PDF. Returns PDF path on success, None on failure."""
    converter = MarkdownToPdfConverter()
    if pdf_filepath is None:
        pdf_filepath = str(Path(md_filepath).with_suffix('.pdf'))
    return pdf_filepath if converter.convert(md_filepath, pdf_filepath) else None
