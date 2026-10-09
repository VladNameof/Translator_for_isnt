"""
Core PPTX Translation Engine
Applies translations from GlossaryManager while preserving run-level formatting,
font sizes, colors, alignments, and visual integrity without requiring MS Office.
"""

import os
from typing import Callable, Optional
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from src.core.glossary_manager import GlossaryManager

class TranslationResult:
    def __init__(self, source_path: str, target_path: str, translated_count: int, total_shapes: int):
        self.source_path = source_path
        self.target_path = target_path
        self.translated_count = translated_count
        self.total_shapes = total_shapes
        self.success = True


class PPTXTranslationEngine:
    def __init__(self, glossary_manager: GlossaryManager):
        self.glossary = glossary_manager

    def _update_text_frame_safely(self, text_frame, new_text: str):
        """
        Updates text_frame text while capturing and restoring font properties
        (Name, Size, Bold, Italic, Color) from the original runs.
        """
        first_run = None
        for p in text_frame.paragraphs:
            for r in p.runs:
                first_run = r
                break
            if first_run:
                break

        font_name = first_run.font.name if first_run and first_run.font else None
        font_size = first_run.font.size if first_run and first_run.font else None
        font_bold = first_run.font.bold if first_run and first_run.font else None
        font_italic = first_run.font.italic if first_run and first_run.font else None
        
        font_color = None
        if first_run and first_run.font and hasattr(first_run.font, 'color') and hasattr(first_run.font.color, 'rgb'):
            try:
                font_color = first_run.font.color.rgb
            except Exception:
                font_color = None

        # Replace text
        text_frame.text = new_text

        # Re-apply typography
        if first_run:
            for p in text_frame.paragraphs:
                for r in p.runs:
                    if font_name:
                        r.font.name = font_name
                    if font_size:
                        r.font.size = font_size
                    if font_bold is not None:
                        r.font.bold = font_bold
                    if font_italic is not None:
                        r.font.italic = font_italic
                    if font_color:
                        try:
                            r.font.color.rgb = font_color
                        except Exception:
                            pass

    def _process_text_frame(self, text_frame) -> int:
        if not text_frame or not text_frame.text:
            return 0
        
        raw_text = text_frame.text
        if not raw_text.strip():
            return 0

        translation = self.glossary.find_translation(raw_text)
        if translation:
            self._update_text_frame_safely(text_frame, translation)
            return 1
        return 0

    def _traverse_shape(self, shape) -> int:
        count = 0
        
        # 1. Grouped Shapes
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            for child in shape.shapes:
                count += self._traverse_shape(child)

        # 2. Tables
        elif shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    if cell.text_frame:
                        count += self._process_text_frame(cell.text_frame)

        # 3. Standard TextFrame Shapes
        elif shape.has_text_frame:
            count += self._process_text_frame(shape.text_frame)

        return count

    def translate_presentation(
        self,
        source_path: str,
        target_path: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> TranslationResult:
        """
        Translates a single PPTX presentation file into target_path.
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")

        prs = Presentation(source_path)
        translated_count = 0
        total_shapes = 0

        if progress_callback:
            progress_callback(f"Translating: {os.path.basename(source_path)}")

        # 1. Slide Masters
        for master in prs.slide_masters:
            for shape in master.shapes:
                total_shapes += 1
                translated_count += self._traverse_shape(shape)

        # 2. Slides
        for s_idx, slide in enumerate(prs.slides, start=1):
            for shape in slide.shapes:
                total_shapes += 1
                translated_count += self._traverse_shape(shape)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
        prs.save(target_path)

        if progress_callback:
            progress_callback(f"Saved: {os.path.basename(target_path)} (Applied {translated_count} translations)")

        return TranslationResult(source_path, target_path, translated_count, total_shapes)
