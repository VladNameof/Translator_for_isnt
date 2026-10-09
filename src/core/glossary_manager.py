"""
Glossary & Dictionary Management Module
Manages termbases, JSON dictionary loading, multi-tier matching, and editing.
"""

import os
import json
from typing import Dict, Optional
from src.core.normalizer import TextNormalizer

class GlossaryManager:
    def __init__(self, dict_path: Optional[str] = None):
        self.direct_map: Dict[str, str] = {}
        self.norm_map: Dict[str, str] = {}
        self.dict_path = dict_path
        
        if dict_path and os.path.exists(dict_path):
            self.load_from_file(dict_path)

    def load_from_file(self, file_path: str):
        """Loads a JSON dictionary file into direct and normalized maps."""
        self.dict_path = file_path
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.load_from_dict(data)

    def load_from_dict(self, data: Dict[str, str]):
        """Populates lookup structures from a Python dictionary."""
        self.direct_map = {}
        self.norm_map = {}
        for k, v in data.items():
            if not k or not v:
                continue
            self.direct_map[k] = v
            self.direct_map[k.strip()] = v
            norm_k = TextNormalizer.normalize(k)
            self.norm_map[norm_k] = v

    def add_entry(self, source_text: str, translated_text: str):
        """Adds or updates an entry in the active dictionary."""
        if not source_text or not translated_text:
            return
        self.direct_map[source_text] = translated_text
        self.direct_map[source_text.strip()] = translated_text
        norm_k = TextNormalizer.normalize(source_text)
        self.norm_map[norm_k] = translated_text

    def find_translation(self, text: str) -> Optional[str]:
        """
        Looks up translation using 3-tier strategy:
        1. Exact match
        2. Trimmed match
        3. Normalized whitespace / unicode match
        """
        if not text or not text.strip():
            return None
        
        # Tier 1: Exact raw match
        if text in self.direct_map:
            return self.direct_map[text]
        
        # Tier 2: Trimmed match
        trimmed = text.strip()
        if trimmed in self.direct_map:
            return self.direct_map[trimmed]
        
        # Tier 3: Normalized match
        norm = TextNormalizer.normalize(text)
        if norm in self.norm_map:
            return self.norm_map[norm]
        
        return None

    def save_to_file(self, target_path: Optional[str] = None):
        """Saves current dictionary entries to a formatted JSON file."""
        save_path = target_path or self.dict_path
        if not save_path:
            raise ValueError("Target file path must be specified.")
        
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.direct_map, f, ensure_ascii=False, indent=2)

    @classmethod
    def create_for_language(cls, target_lang: str, base_dir: Optional[str] = None) -> "GlossaryManager":
        """Factory method to load built-in dictionaries for UA or EN."""
        current_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dict_folder = os.path.join(current_dir, "dictionaries")
        
        lang_code = target_lang.lower().strip()
        if lang_code in ("ua", "uk", "ukrainian"):
            dict_file = os.path.join(dict_folder, "dict_ua.json")
        elif lang_code in ("en", "eng", "english"):
            dict_file = os.path.join(dict_folder, "dict_en.json")
        else:
            dict_file = os.path.join(dict_folder, f"dict_{lang_code}.json")
            
        return cls(dict_file if os.path.exists(dict_file) else None)
