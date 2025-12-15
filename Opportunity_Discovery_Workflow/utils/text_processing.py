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
