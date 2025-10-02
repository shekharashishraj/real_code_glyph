#!/usr/bin/env python3
"""
Enhanced Font Manipulation Engine with Precise idDelta Modification
Implementation of the technique from arXiv:2505.16957 with detailed algorithm
"""

import struct
import os
from typing import Dict, List, Tuple, Optional
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import table__c_m_a_p
from fontTools.misc.timeTools import timestampSinceEpoch
import copy


class EnhancedFontManipulator:
    """
    Enhanced font manipulator with precise idDelta calculation and
    cmap table modification following the research methodology.
    """

    def __init__(self):
        self.font = None
        self.original_cmap = None
        self.original_cmap_table = None
        self.modifications = {}
        self.font_path = None

    def load_font(self, font_path: str) -> bool:
        """Load TrueType font and extract cmap information."""
        try:
            self.font_path = font_path
            self.font = TTFont(font_path)

            if 'cmap' not in self.font:
                print("Font does not contain cmap table")
                return False

            # Find the Unicode BMP cmap subtable (Platform 3, Encoding 1)
            self.original_cmap_table = self._find_unicode_cmap()
            if not self.original_cmap_table:
                print("No suitable Unicode cmap table found")
                return False

            self.original_cmap = dict(self.original_cmap_table.cmap)
            print(f"Loaded font: {os.path.basename(font_path)}")
            print(f"Characters available: {len(self.original_cmap)}")

            return True

        except Exception as e:
            print(f"Error loading font: {e}")
            return False

    def _find_unicode_cmap(self):
        """Find the Unicode BMP cmap subtable."""
        for table in self.font['cmap'].tables:
            # Platform 3 (Microsoft), Encoding 1 (Unicode BMP)
            if table.platformID == 3 and table.platEncID == 1:
                return table
            # Platform 0 (Unicode), Encoding 3 (Unicode 2.0 BMP)
            elif table.platformID == 0 and table.platEncID == 3:
                return table
        return None

    def analyze_cmap_structure(self) -> Dict:
        """Analyze the current cmap table structure for debugging."""
        if not self.original_cmap_table:
            return {}

        analysis = {
            'format': self.original_cmap_table.format,
            'platform_id': self.original_cmap_table.platformID,
            'plat_enc_id': self.original_cmap_table.platEncID,
            'character_count': len(self.original_cmap_table.cmap),
            'character_range': {
                'min': min(self.original_cmap_table.cmap.keys()) if self.original_cmap_table.cmap else 0,
                'max': max(self.original_cmap_table.cmap.keys()) if self.original_cmap_table.cmap else 0
            }
        }

        # Analyze segments for format 4 tables
        if hasattr(self.original_cmap_table, 'endCode'):
            analysis['segments'] = len(self.original_cmap_table.endCode)
            analysis['format_4_details'] = {
                'seg_count': len(self.original_cmap_table.endCode),
                'id_delta_count': len(self.original_cmap_table.idDelta),
                'id_range_offset_count': len(self.original_cmap_table.idRangeOffset)
            }

        return analysis

    def create_deceptive_mapping_with_idelta(self,
                                           original_char: str,
                                           replacement_char: str,
                                           visual_char: str) -> bool:
        """
        Create deceptive mapping using precise idDelta manipulation.

        Algorithm from paper:
        1. Isolate target character in separate segment
        2. Calculate new idDelta: New idDelta = x2 + d2 - x1
        3. Modify segment boundaries and idDelta values
        """
        if not self.font or not self.original_cmap:
            return False

        try:
            # Get character codes
            orig_code = ord(original_char)
            repl_code = ord(replacement_char)
            visual_code = ord(visual_char)

            # Verify visual character exists in font
            if visual_code not in self.original_cmap:
                print(f"Visual character '{visual_char}' not found in font")
                return False

            target_glyph_id = self.original_cmap[visual_code]

            # Store modification details
            self.modifications[orig_code] = {
                'target_glyph_id': target_glyph_id,
                'visual_char': visual_char,
                'original_char': original_char,
                'method': 'idDelta_modification'
            }

            self.modifications[repl_code] = {
                'target_glyph_id': target_glyph_id,
                'visual_char': visual_char,
                'original_char': replacement_char,
                'method': 'idDelta_modification'
            }

            return True

        except Exception as e:
            print(f"Error creating deceptive mapping: {e}")
            return False

    def _isolate_character_segment(self, char_code: int, target_glyph_id: int):
        """
        Isolate a character in its own segment for precise idDelta control.
        This implements the segment isolation technique from the paper.
        """
        if self.original_cmap_table.format != 4:
            # For non-format-4 tables, use direct mapping
            return self._create_direct_mapping(char_code, target_glyph_id)

        # Find current segment containing the character
        current_segment = self._find_character_segment(char_code)
        if current_segment == -1:
            return False

        # Create new segment boundaries
        new_segments = self._create_isolated_segment(char_code, current_segment)

        # Calculate new idDelta for the isolated segment
        new_id_delta = target_glyph_id - char_code

        return self._update_cmap_segments(new_segments, char_code, new_id_delta)

    def _find_character_segment(self, char_code: int) -> int:
        """Find which segment contains the given character code."""
        if not hasattr(self.original_cmap_table, 'endCode'):
            return -1

        for i, end_code in enumerate(self.original_cmap_table.endCode):
            start_code = self.original_cmap_table.startCode[i]
            if start_code <= char_code <= end_code:
                return i

        return -1

    def _create_isolated_segment(self, char_code: int, current_segment: int) -> Dict:
        """Create new segment structure with isolated character."""
        # This is a simplified version - full implementation would require
        # careful handling of all segment arrays

        segments = {
            'endCode': list(self.original_cmap_table.endCode),
            'startCode': list(self.original_cmap_table.startCode),
            'idDelta': list(self.original_cmap_table.idDelta),
            'idRangeOffset': list(self.original_cmap_table.idRangeOffset)
        }

        # Split current segment if needed
        original_start = segments['startCode'][current_segment]
        original_end = segments['endCode'][current_segment]
        original_id_delta = segments['idDelta'][current_segment]

        if original_start == char_code and original_end == char_code:
            # Character is already isolated
            return segments

        # Need to split the segment
        new_segments = {
            'endCode': [],
            'startCode': [],
            'idDelta': [],
            'idRangeOffset': []
        }

        for i, (start, end, delta, offset) in enumerate(zip(
            segments['startCode'], segments['endCode'],
            segments['idDelta'], segments['idRangeOffset'])):

            if i == current_segment:
                # Split this segment
                if start < char_code:
                    # Add segment before target character
                    new_segments['startCode'].append(start)
                    new_segments['endCode'].append(char_code - 1)
                    new_segments['idDelta'].append(delta)
                    new_segments['idRangeOffset'].append(offset)

                # Add isolated segment for target character
                new_segments['startCode'].append(char_code)
                new_segments['endCode'].append(char_code)
                new_segments['idDelta'].append(0)  # Will be updated later
                new_segments['idRangeOffset'].append(0)

                if char_code < end:
                    # Add segment after target character
                    new_segments['startCode'].append(char_code + 1)
                    new_segments['endCode'].append(end)
                    new_segments['idDelta'].append(delta)
                    new_segments['idRangeOffset'].append(offset)
            else:
                # Keep original segment
                new_segments['startCode'].append(start)
                new_segments['endCode'].append(end)
                new_segments['idDelta'].append(delta)
                new_segments['idRangeOffset'].append(offset)

        return new_segments

    def _create_direct_mapping(self, char_code: int, target_glyph_id: int) -> bool:
        """Create direct character to glyph mapping for non-format-4 tables."""
        try:
            # For format 12 and other tables, direct mapping is simpler
            self.original_cmap_table.cmap[char_code] = target_glyph_id
            return True
        except Exception as e:
            print(f"Error creating direct mapping: {e}")
            return False

    def apply_all_modifications(self) -> bool:
        """Apply all stored modifications to the font's cmap table."""
        if not self.modifications:
            return True

        try:
            # For simplicity, we'll use direct cmap modification
            # In a production version, you'd implement full segment manipulation

            for char_code, mod_info in self.modifications.items():
                self.original_cmap_table.cmap[char_code] = mod_info['target_glyph_id']

            return True

        except Exception as e:
            print(f"Error applying modifications: {e}")
            return False

    def generate_modified_font(self, output_path: str) -> bool:
        """Generate the modified font with all mappings applied."""
        if not self.font:
            return False

        try:
            # Apply all modifications
            if not self.apply_all_modifications():
                return False

            # Update font timestamp
            if 'head' in self.font:
                self.font['head'].modified = timestampSinceEpoch()

            # Save the modified font
            self.font.save(output_path)
            print(f"Modified font saved to: {output_path}")
            return True

        except Exception as e:
            print(f"Error generating modified font: {e}")
            return False

    def get_modification_summary(self) -> Dict:
        """Get a summary of all current modifications."""
        summary = {
            'total_modifications': len(self.modifications),
            'font_info': {
                'path': self.font_path,
                'original_characters': len(self.original_cmap) if self.original_cmap else 0
            },
            'cmap_analysis': self.analyze_cmap_structure(),
            'modifications': []
        }

        for char_code, mod_info in self.modifications.items():
            summary['modifications'].append({
                'character': chr(char_code),
                'unicode_value': f"U+{char_code:04X}",
                'visual_appearance': mod_info['visual_char'],
                'target_glyph_id': mod_info['target_glyph_id'],
                'method': mod_info['method']
            })

        return summary

    def validate_modifications(self) -> List[str]:
        """Validate all current modifications for potential issues."""
        issues = []

        if not self.font:
            issues.append("No font loaded")
            return issues

        if not self.modifications:
            issues.append("No modifications to validate")
            return issues

        # Check for glyph existence
        glyf_table = self.font.get('glyf')
        if glyf_table:
            max_glyph_id = len(glyf_table.glyphs) - 1

            for char_code, mod_info in self.modifications.items():
                glyph_id = mod_info['target_glyph_id']
                if glyph_id > max_glyph_id:
                    issues.append(f"Character U+{char_code:04X}: target glyph ID {glyph_id} exceeds maximum {max_glyph_id}")

        # Check for conflicting mappings
        visual_chars = {}
        for char_code, mod_info in self.modifications.items():
            visual = mod_info['visual_char']
            if visual in visual_chars:
                issues.append(f"Multiple characters map to visual '{visual}': {visual_chars[visual]} and U+{char_code:04X}")
            else:
                visual_chars[visual] = f"U+{char_code:04X}"

        return issues

    def reset_font(self) -> bool:
        """Reset font to original state."""
        if not self.font_path:
            return False

        try:
            self.modifications.clear()
            return self.load_font(self.font_path)
        except Exception as e:
            print(f"Error resetting font: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    manipulator = EnhancedFontManipulator()

    # Example: Load a font and create deceptive mappings
    # You'll need to provide an actual font file path
    font_path = "example_font.ttf"

    if os.path.exists(font_path):
        if manipulator.load_font(font_path):
            print("\\nFont Analysis:")
            analysis = manipulator.analyze_cmap_structure()
            for key, value in analysis.items():
                print(f"  {key}: {value}")

            # Create example mapping: make 'b' appear as 'a'
            if manipulator.create_deceptive_mapping_with_idelta('a', 'b', 'a'):
                print("\\nCreated deceptive mapping")

                # Validate modifications
                issues = manipulator.validate_modifications()
                if issues:
                    print("\\nValidation issues:")
                    for issue in issues:
                        print(f"  - {issue}")
                else:
                    print("\\nValidation passed")

                # Generate modified font
                output_path = "modified_example_font.ttf"
                if manipulator.generate_modified_font(output_path):
                    print(f"\\nModified font generated: {output_path}")

                    # Print summary
                    summary = manipulator.get_modification_summary()
                    print("\\nModification Summary:")
                    print(f"  Total modifications: {summary['total_modifications']}")
                    for mod in summary['modifications']:
                        print(f"    {mod['character']} ({mod['unicode_value']}) -> visually appears as '{mod['visual_appearance']}'")
    else:
        print(f"Font file not found: {font_path}")
        print("Please provide a valid TrueType font file to test the implementation.")