#!/usr/bin/env python3
"""
Font Manipulation Engine for Unicode Glyph Mapping Changes
Based on the technique described in arXiv:2505.16957

This module implements the core font manipulation strategy that allows
characters to visually appear as one glyph while having different Unicode values.
"""

import struct
import io
import copy
from typing import Dict, List, Tuple, Optional
from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode


class FontManipulator:
    """
    Core engine for TrueType font manipulation using glyph mapping modification.

    Implements the technique: GlyphIndex = idDelta + Code
    By modifying idDelta values, we can make characters visually appear as one
    glyph while having different Unicode values.
    """

    def __init__(self):
        self.font = None
        self.original_cmap = None
        self.modified_mappings = {}

    def load_font(self, font_path: str) -> bool:
        """Load a TrueType font for manipulation."""
        try:
            self.font = TTFont(font_path)
            self.original_cmap = self._extract_cmap()
            return True
        except Exception as e:
            print(f"Error loading font: {e}")
            return False

    def _extract_cmap(self) -> Dict:
        """Extract the current character mapping from the font."""
        if not self.font or 'cmap' not in self.font:
            return {}

        # Get the Unicode BMP cmap table (platform 3, encoding 1)
        cmap_table = None
        for table in self.font['cmap'].tables:
            if table.platformID == 3 and table.platEncID == 1:
                cmap_table = table
                break

        if not cmap_table:
            return {}

        return cmap_table.cmap

    def create_deceptive_mapping(self,
                                original_char: str,
                                replacement_char: str,
                                visual_char: str) -> bool:
        """
        Create a deceptive mapping where:
        - original_char visually appears as visual_char
        - replacement_char also visually appears as visual_char
        - But they have different Unicode values

        Args:
            original_char: Character to modify (e.g., 'a')
            replacement_char: Character to map to same visual (e.g., 'b')
            visual_char: What both should visually appear as (e.g., 'a')
        """
        if not self.font or not self.original_cmap:
            return False

        try:
            # Get Unicode code points
            orig_code = ord(original_char)
            repl_code = ord(replacement_char)
            visual_code = ord(visual_char)

            # Get the glyph index for the visual character
            if visual_code not in self.original_cmap:
                print(f"Visual character '{visual_char}' not found in font")
                return False

            target_glyph_index = self.original_cmap[visual_code]

            # Store the mapping modification
            self.modified_mappings[orig_code] = {
                'target_glyph': target_glyph_index,
                'visual_char': visual_char,
                'original_char': original_char
            }

            self.modified_mappings[repl_code] = {
                'target_glyph': target_glyph_index,
                'visual_char': visual_char,
                'original_char': replacement_char
            }

            return True

        except Exception as e:
            print(f"Error creating deceptive mapping: {e}")
            return False

    def calculate_id_delta(self, char_code: int, target_glyph_index: int) -> int:
        """
        Calculate the idDelta value needed for the mapping.
        Formula: GlyphIndex = idDelta + Code
        Therefore: idDelta = GlyphIndex - Code
        """
        return target_glyph_index - char_code

    def modify_cmap_table(self) -> bool:
        """Apply all stored modifications to the font's cmap table."""
        if not self.font or not self.modified_mappings:
            return False

        try:
            # Get the cmap table to modify
            cmap_table = None
            for table in self.font['cmap'].tables:
                if table.platformID == 3 and table.platEncID == 1:
                    cmap_table = table
                    break

            if not cmap_table:
                return False

            # Apply modifications
            for char_code, mapping in self.modified_mappings.items():
                cmap_table.cmap[char_code] = mapping['target_glyph']

            return True

        except Exception as e:
            print(f"Error modifying cmap table: {e}")
            return False

    def generate_modified_font(self, output_path: str) -> bool:
        """Generate a new font file with the modified mappings."""
        if not self.font:
            return False

        try:
            # Apply cmap modifications
            if not self.modify_cmap_table():
                return False

            # Save the modified font
            self.font.save(output_path)
            return True

        except Exception as e:
            print(f"Error generating modified font: {e}")
            return False

    def get_mapping_preview(self) -> List[Dict]:
        """Get a preview of all current mappings for display."""
        preview = []

        for char_code, mapping in self.modified_mappings.items():
            preview.append({
                'unicode_value': char_code,
                'character': chr(char_code),
                'visual_appearance': mapping['visual_char'],
                'original_character': mapping['original_char'],
                'glyph_index': mapping['target_glyph']
            })

        return preview

    def reset_mappings(self):
        """Reset all modifications and restore original mappings."""
        self.modified_mappings = {}
        if self.font and self.original_cmap:
            # Restore original cmap
            for table in self.font['cmap'].tables:
                if table.platformID == 3 and table.platEncID == 1:
                    table.cmap = copy.deepcopy(self.original_cmap)
                    break


class WordMappingManager:
    """
    High-level manager for word-based font manipulation.
    Handles the mapping of entire words to different Unicode sequences
    while maintaining visual appearance.
    """

    def __init__(self):
        self.font_manipulator = FontManipulator()
        self.word_mappings = {}

    def load_font(self, font_path: str) -> bool:
        """Load a font for word manipulation."""
        return self.font_manipulator.load_font(font_path)

    def create_word_mapping(self,
                           original_word: str,
                           replacement_word: str) -> bool:
        """
        Create a mapping where replacement_word visually appears as original_word.

        Args:
            original_word: The word as it should visually appear
            replacement_word: The word with different Unicode values
        """
        if len(original_word) != len(replacement_word):
            print("Words must be the same length for character-by-character mapping")
            return False

        try:
            # Create character-by-character mappings
            for i, (orig_char, repl_char) in enumerate(zip(original_word, replacement_word)):
                if not self.font_manipulator.create_deceptive_mapping(
                    repl_char, repl_char, orig_char):
                    print(f"Failed to create mapping for position {i}: {repl_char} -> {orig_char}")
                    return False

            # Store the word mapping
            self.word_mappings[replacement_word] = original_word
            return True

        except Exception as e:
            print(f"Error creating word mapping: {e}")
            return False

    def generate_font_with_mappings(self, output_path: str) -> bool:
        """Generate the modified font with all word mappings applied."""
        return self.font_manipulator.generate_modified_font(output_path)

    def get_all_mappings(self) -> Dict:
        """Get all current word mappings."""
        return {
            'word_mappings': self.word_mappings,
            'character_mappings': self.font_manipulator.get_mapping_preview()
        }

    def clear_all_mappings(self):
        """Clear all mappings and reset to original font."""
        self.word_mappings = {}
        self.font_manipulator.reset_mappings()


if __name__ == "__main__":
    # Example usage
    manager = WordMappingManager()

    # Load a font (you'll need to provide a path to a .ttf file)
    if manager.load_font("sample_font.ttf"):
        # Create a mapping where "hello" appears as "world" visually
        if manager.create_word_mapping("world", "hello"):
            # Generate the modified font
            manager.generate_font_with_mappings("modified_font.ttf")

            # Preview mappings
            mappings = manager.get_all_mappings()
            print("Created mappings:", mappings)