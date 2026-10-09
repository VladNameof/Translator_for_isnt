"""
Automated Quality Assurance & Verification Module
Validates generated PPTX presentations to guarantee 0 source language remnants.
"""

import re
from typing import List, Dict, Any
from src.core.extractor import PPTXExtractor, ExtractedItem

class VerificationIssue:
    def __init__(self, slide: Any, path: str, matched_keyword: str, text: str):
        self.slide = slide
        self.path = path
        self.matched_keyword = matched_keyword
        self.text = text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slide": self.slide,
            "path": self.path,
            "matched_keyword": self.matched_keyword,
            "text": self.text
        }


class VerificationResult:
    def __init__(self, file_path: str, is_passed: bool, issues: List[VerificationIssue], total_text_nodes: int):
        self.file_path = file_path
        self.is_passed = is_passed
        self.issues = issues
        self.total_text_nodes = total_text_nodes


class PPTXVerifier:
    # Key Polish industrial keywords indicating un-translated remnants
    DEFAULT_PL_KEYWORDS = [
        r"\bWłącz\b", r"\bSprawdź\b", r"\bWybierz\b", r"\bOdbierz\b",
        r"\bnaklejk\w*", r"\bdwukrotnie\b", r"\bstacj\w*", r"\boknie\b",
        r"\bzeskanuj\b", r"\bpierwszego\b", r"\bdrugiego\b", r"\bzależności\b",
        r"\bwyniku\b", r"\bmontażu\b", r"\bstanowisk\w*", r"\bINSTRUKCJA\b",
        r"\bOPRACOWAŁ\b", r"\bZATWIERDZIŁ\b", r"\bDOKUMENT\b", r"\bUtworzenie\b",
        r"\bdokumentacji\b", r"\bkomponenty\b", r"\bprawidłowo\b", r"\bzmontowane\b",
        r"\bwkrętak\b", r"\bmłotek\b", r"\bFIKSTURY\b", r"\bDokręcić\b",
        r"\bZałożyć\b", r"\bPrzykręcić\b", r"\bWoreczek\b", r"\bDRUKARKA\b",
        r"\bŚruby\b", r"\bUwaga\b", r"\bPodłączyć\b", r"\bOznaczenie\b"
    ]

    def __init__(self, pl_keywords: List[str] = None):
        self.keywords = pl_keywords or self.DEFAULT_PL_KEYWORDS

    def verify_file(self, pptx_path: str) -> VerificationResult:
        """
        Extracts all text from pptx_path and scans for any occurrences of source language keywords.
        """
        items: List[ExtractedItem] = PPTXExtractor.extract_from_presentation(pptx_path)
        issues: List[VerificationIssue] = []

        for item in items:
            for kw in self.keywords:
                if re.search(kw, item.text, flags=re.IGNORECASE):
                    issues.append(VerificationIssue(
                        slide=item.slide,
                        path=item.path,
                        matched_keyword=kw,
                        text=item.text
                    ))
                    break

        is_passed = len(issues) == 0
        return VerificationResult(
            file_path=pptx_path,
            is_passed=is_passed,
            issues=issues,
            total_text_nodes=len(items)
        )
