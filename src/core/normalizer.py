"""
Text Normalization Module for PPTX Translation Engine
Handles non-breaking spaces, Unicode variations, and line breaks.
"""

import re
import unicodedata

class TextNormalizer:
    @staticmethod
    def normalize(text: str) -> str:
        """
        Normalizes a string for robust dictionary lookup:
        - Replaces NBSP (0x00A0) with standard space
        - Replaces En-dash (0x2013), Em-dash (0x2014) with standard dash (-)
        - Replaces carriage returns and line feeds with standard spaces
        - Collapses consecutive whitespace into a single space
        - Trims leading and trailing whitespace
        """
        if not text:
            return ""
        
        # Normalize Unicode
        t = unicodedata.normalize('NFKC', text)
        
        # Replace special whitespace and dashes
        t = t.replace('\xa0', ' ')
        t = t.replace('\u2013', '-').replace('\u2014', '-')
        t = t.replace('\r', ' ').replace('\n', ' ')
        
        # Collapse multiple spaces and trim
        t = re.sub(r'\s+', ' ', t).strip()
        return t

    @staticmethod
    def is_translatable(text: str) -> bool:
        """
        Determines if a text block contains translatable natural language
        or is purely a technical number, date, or standalone symbol.
        """
        if not text or not text.strip():
            return False
        
        cleaned = text.strip()
        
        # Standalone numbers, single letters, revision symbols
        if re.match(r'^[0-9]+(\.[0-9]+)?$', cleaned):
            return False
        if len(cleaned) <= 2 and cleaned.isalnum():
            return False
        
        # Pure dates: 01.10.2026, 01-10-2026
        if re.match(r'^\d{2}[.-]\d{2}[.-]\d{4}$', cleaned):
            return False
        
        # Part numbers with no spaces (e.g. TYEH-GOO-431008-01-MP_970)
        if re.match(r'^[A-Z0-9_\-\.]{6,}$', cleaned) and not ' ' in cleaned:
            return False

        return True
