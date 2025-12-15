from pathlib import Path
import re


def normalize_unicode_characters(text):
    """Replace problematic Unicode characters with ASCII equivalents."""
    replacements = {
        # Dashes
        '\u2013': '-',   # en-dash
        '\u2014': '--',  # em-dash
        '\u2015': '--',  # horizontal bar
        '\u2212': '-',   # minus sign
        
        # Quotes
        '\u2018': "'",   # left single quote
        '\u2019': "'",   # right single quote (apostrophe)
        '\u201A': "'",   # single low-9 quote
        '\u201B': "'",   # single high-reversed-9 quote
        '\u201C': '"',   # left double quote
        '\u201D': '"',   # right double quote
        '\u201E': '"',   # double low-9 quote
        '\u201F': '"',   # double high-reversed-9 quote
        '\u00AB': '"',   # left-pointing double angle quote
        '\u00BB': '"',   # right-pointing double angle quote
        
        # Ellipsis
        '\u2026': '...',  # horizontal ellipsis
        
        # Spaces
        '\u00A0': ' ',   # non-breaking space
        '\u2002': ' ',   # en space
        '\u2003': ' ',   # em space
        '\u2009': ' ',   # thin space
        '\u200A': ' ',   # hair space
        '\u200B': '',    # zero-width space
        
        # Bullets and symbols
        '\u2022': '*',   # bullet
        '\u2023': '>',   # triangular bullet
        '\u2043': '-',   # hyphen bullet
        '\u25CF': '*',   # black circle
        '\u25CB': 'o',   # white circle
        '\u25AA': '*',   # black small square
        '\u25AB': '*',   # white small square
        '\u2605': '*',   # black star
        '\u2606': '*',   # white star
        
        # Arrows
        '\u2192': '->',  # rightwards arrow
        '\u2190': '<-',  # leftwards arrow
        '\u2194': '<->',  # left right arrow
        '\u21D2': '=>',  # rightwards double arrow
        '\u21D0': '<=',  # leftwards double arrow
        
        # Math symbols
        '\u00D7': 'x',   # multiplication sign
        '\u00F7': '/',   # division sign
        '\u2264': '<=',  # less-than or equal to
        '\u2265': '>=',  # greater-than or equal to
        '\u2260': '!=',  # not equal to
        '\u00B1': '+/-', # plus-minus sign
        '\u221E': 'inf', # infinity
        
        # Currency
        '\u20AC': 'EUR', # euro sign
        '\u00A3': 'GBP', # pound sign
        '\u00A5': 'JPY', # yen sign
        
        # Trademark/Copyright
        '\u00AE': '(R)',  # registered sign
        '\u2122': '(TM)', # trademark sign
        '\u00A9': '(C)',  # copyright sign
        
        # Other common symbols
        '\u00B0': ' degrees',  # degree sign
        '\u00B2': '2',    # superscript 2
        '\u00B3': '3',    # superscript 3
        '\u00BC': '1/4',  # fraction one quarter
        '\u00BD': '1/2',  # fraction one half
        '\u00BE': '3/4',  # fraction three quarters
    }
    
    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)
    
    # Remove any remaining non-ASCII characters that might cause issues
    # but keep basic Latin characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    return text


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
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Critical Minerals Report</title>
                <style>
                    @page {{
                        size: A4;
                        margin: 2cm;
                        @frame footer {{
                            -pdf-frame-content: footerContent;
                            bottom: 0.5cm;
                            margin-left: 2cm;
                            margin-right: 2cm;
                            height: 1cm;
                        }}
                    }}
                    
                    body {{
                        font-family: Helvetica, Arial, sans-serif;
                        font-size: 11pt;
                        line-height: 1.5;
                        color: #333333;
                    }}
                    
                    h1 {{
                        font-size: 24pt;
                        color: #1a1a1a;
                        margin-top: 20pt;
                        margin-bottom: 15pt;
                        border-bottom: 2pt solid #2c3e50;
                        padding-bottom: 8pt;
                    }}
                    
                    h2 {{
                        font-size: 18pt;
                        color: #2c3e50;
                        margin-top: 18pt;
                        margin-bottom: 10pt;
                        border-left: 4pt solid #3498db;
                        padding-left: 8pt;
                    }}
                    
                    h3 {{
                        font-size: 14pt;
                        color: #34495e;
                        margin-top: 14pt;
                        margin-bottom: 8pt;
                    }}
                    
                    h4, h5, h6 {{
                        font-size: 12pt;
                        color: #555555;
                        margin-top: 10pt;
                        margin-bottom: 6pt;
                    }}
                    
                    p {{
                        margin: 8pt 0;
                        text-align: justify;
                    }}
                    
                    ul, ol {{
                        margin: 10pt 0;
                        padding-left: 25pt;
                    }}
                    
                    li {{
                        margin: 4pt 0;
                    }}
                    
                    strong {{
                        font-weight: bold;
                        color: #2c3e50;
                    }}
                    
                    em {{
                        font-style: italic;
                    }}
                    
                    code {{
                        background-color: #f5f5f5;
                        font-family: Courier, monospace;
                        font-size: 10pt;
                        padding: 1pt 4pt;
                    }}
                    
                    pre {{
                        background-color: #f8f8f8;
                        border-left: 3pt solid #3498db;
                        padding: 10pt;
                        margin: 10pt 0;
                        font-family: Courier, monospace;
                        font-size: 9pt;
                        white-space: pre-wrap;
                        word-wrap: break-word;
                    }}
                    
                    blockquote {{
                        border-left: 4pt solid #3498db;
                        margin: 12pt 0;
                        padding: 8pt 12pt;
                        background-color: #f9f9f9;
                        font-style: italic;
                        color: #555555;
                    }}
                    
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 12pt 0;
                    }}
                    
                    th {{
                        background-color: #2c3e50;
                        color: white;
                        padding: 8pt;
                        text-align: left;
                        font-weight: bold;
                        border: 1pt solid #34495e;
                    }}
                    
                    td {{
                        padding: 6pt 8pt;
                        border: 1pt solid #dddddd;
                    }}
                    
                    tr:nth-child(even) {{
                        background-color: #f9f9f9;
                    }}
                    
                    a {{
                        color: #3498db;
                        text-decoration: none;
                    }}
                    
                    hr {{
                        border: none;
                        border-top: 1pt solid #bdc3c7;
                        margin: 20pt 0;
                    }}
                    
                    .footer {{
                        font-size: 9pt;
                        color: #666666;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                {html_content}
                <div id="footerContent" class="footer">
                    <pdf:pagenumber /> / <pdf:pagecount />
                </div>
            </body>
            </html>
            """
            
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
