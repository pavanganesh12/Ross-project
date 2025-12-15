
PDF_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Opportunity Discovery Report</title>
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
