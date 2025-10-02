#!/usr/bin/env python3
"""
Binary Font Manipulation Functions
Low-level TrueType font binary manipulation for precise glyph mapping control
Based on the technique described in arXiv:2505.16957
"""

import struct
import io
from typing import Dict, List, Tuple, Optional, BinaryIO
from dataclasses import dataclass


@dataclass
class CmapFormat4:
    """Structure for cmap format 4 table data."""
    format: int
    length: int
    language: int
    seg_count_x2: int
    search_range: int
    entry_selector: int
    range_shift: int
    end_code: List[int]
    reserved_pad: int
    start_code: List[int]
    id_delta: List[int]
    id_range_offset: List[int]
    glyph_id_array: List[int]


class BinaryFontManipulator:
    """
    Low-level binary manipulation of TrueType font files.
    Provides precise control over cmap table modifications.
    """

    def __init__(self):
        self.font_data = None
        self.tables = {}
        self.cmap_offset = None
        self.original_cmap_data = None

    def load_font_binary(self, font_path: str) -> bool:
        """Load font as binary data for manipulation."""
        try:
            with open(font_path, 'rb') as f:
                self.font_data = bytearray(f.read())

            # Parse font header and table directory
            if not self._parse_font_header():
                return False

            # Locate cmap table
            if not self._locate_cmap_table():
                return False

            print(f"Loaded font binary: {font_path}")
            print(f"Font size: {len(self.font_data)} bytes")
            print(f"CMAP table offset: 0x{self.cmap_offset:08X}")

            return True

        except Exception as e:
            print(f"Error loading font binary: {e}")
            return False

    def _parse_font_header(self) -> bool:
        """Parse the font header and table directory."""
        if len(self.font_data) < 12:
            return False

        # Read sfnt header
        offset = 0
        sfnt_version = struct.unpack('>I', self.font_data[offset:offset+4])[0]
        num_tables = struct.unpack('>H', self.font_data[offset+4:offset+6])[0]

        print(f"SFNT version: 0x{sfnt_version:08X}")
        print(f"Number of tables: {num_tables}")

        # Read table directory
        offset = 12
        for i in range(num_tables):
            if offset + 16 > len(self.font_data):
                return False

            tag = self.font_data[offset:offset+4].decode('ascii')
            checksum = struct.unpack('>I', self.font_data[offset+4:offset+8])[0]
            table_offset = struct.unpack('>I', self.font_data[offset+8:offset+12])[0]
            table_length = struct.unpack('>I', self.font_data[offset+12:offset+16])[0]

            self.tables[tag] = {
                'offset': table_offset,
                'length': table_length,
                'checksum': checksum
            }

            offset += 16

        return True

    def _locate_cmap_table(self) -> bool:
        """Locate the cmap table in the font."""
        if 'cmap' not in self.tables:
            print("CMAP table not found")
            return False

        self.cmap_offset = self.tables['cmap']['offset']
        cmap_length = self.tables['cmap']['length']

        # Backup original cmap data
        self.original_cmap_data = bytes(self.font_data[self.cmap_offset:self.cmap_offset + cmap_length])

        return True

    def parse_cmap_format4(self, subtable_offset: int) -> Optional[CmapFormat4]:
        """Parse a cmap format 4 subtable."""
        try:
            offset = self.cmap_offset + subtable_offset

            # Read format 4 header
            format_val = struct.unpack('>H', self.font_data[offset:offset+2])[0]
            if format_val != 4:
                return None

            length = struct.unpack('>H', self.font_data[offset+2:offset+4])[0]
            language = struct.unpack('>H', self.font_data[offset+4:offset+6])[0]
            seg_count_x2 = struct.unpack('>H', self.font_data[offset+6:offset+8])[0]
            search_range = struct.unpack('>H', self.font_data[offset+8:offset+10])[0]
            entry_selector = struct.unpack('>H', self.font_data[offset+10:offset+12])[0]
            range_shift = struct.unpack('>H', self.font_data[offset+12:offset+14])[0]

            seg_count = seg_count_x2 // 2
            offset += 14

            # Read endCode array
            end_code = []
            for i in range(seg_count):
                end_code.append(struct.unpack('>H', self.font_data[offset:offset+2])[0])
                offset += 2

            # Read reserved padding
            reserved_pad = struct.unpack('>H', self.font_data[offset:offset+2])[0]
            offset += 2

            # Read startCode array
            start_code = []
            for i in range(seg_count):
                start_code.append(struct.unpack('>H', self.font_data[offset:offset+2])[0])
                offset += 2

            # Read idDelta array
            id_delta = []
            for i in range(seg_count):
                id_delta.append(struct.unpack('>h', self.font_data[offset:offset+2])[0])  # signed
                offset += 2

            # Read idRangeOffset array
            id_range_offset = []
            for i in range(seg_count):
                id_range_offset.append(struct.unpack('>H', self.font_data[offset:offset+2])[0])
                offset += 2

            # Read glyphIdArray (remaining data)
            glyph_id_array = []
            remaining_length = length - (offset - (self.cmap_offset + subtable_offset))
            for i in range(0, remaining_length, 2):
                if offset + 2 <= len(self.font_data):
                    glyph_id_array.append(struct.unpack('>H', self.font_data[offset:offset+2])[0])
                    offset += 2

            return CmapFormat4(
                format=format_val,
                length=length,
                language=language,
                seg_count_x2=seg_count_x2,
                search_range=search_range,
                entry_selector=entry_selector,
                range_shift=range_shift,
                end_code=end_code,
                reserved_pad=reserved_pad,
                start_code=start_code,
                id_delta=id_delta,
                id_range_offset=id_range_offset,
                glyph_id_array=glyph_id_array
            )

        except Exception as e:
            print(f"Error parsing cmap format 4: {e}")
            return None

    def find_unicode_subtable(self) -> Optional[Tuple[int, int]]:
        """Find Unicode BMP subtable (platform 3, encoding 1)."""
        try:
            offset = self.cmap_offset

            # Read cmap header
            version = struct.unpack('>H', self.font_data[offset:offset+2])[0]
            num_tables = struct.unpack('>H', self.font_data[offset+2:offset+4])[0]
            offset += 4

            print(f"CMAP version: {version}, subtables: {num_tables}")

            # Search for Unicode BMP subtable
            for i in range(num_tables):
                platform_id = struct.unpack('>H', self.font_data[offset:offset+2])[0]
                encoding_id = struct.unpack('>H', self.font_data[offset+2:offset+4])[0]
                subtable_offset = struct.unpack('>I', self.font_data[offset+4:offset+8])[0]

                print(f"Subtable {i}: Platform {platform_id}, Encoding {encoding_id}, Offset 0x{subtable_offset:08X}")

                # Check for Unicode BMP (Platform 3, Encoding 1)
                if platform_id == 3 and encoding_id == 1:
                    return (subtable_offset, i)

                offset += 8

            return None

        except Exception as e:
            print(f"Error finding Unicode subtable: {e}")
            return None

    def modify_id_delta_for_character(self, char_code: int, new_glyph_id: int) -> bool:
        """
        Modify idDelta for a specific character using the paper's algorithm.
        Algorithm: New idDelta = target_glyph_id - char_code
        """
        try:
            # Find Unicode subtable
            subtable_info = self.find_unicode_subtable()
            if not subtable_info:
                print("Unicode subtable not found")
                return False

            subtable_offset, table_index = subtable_info

            # Parse format 4 subtable
            cmap_format4 = self.parse_cmap_format4(subtable_offset)
            if not cmap_format4:
                print("Failed to parse cmap format 4")
                return False

            # Find segment containing the character
            segment_index = self._find_segment_for_char(cmap_format4, char_code)
            if segment_index == -1:
                print(f"Character U+{char_code:04X} not found in any segment")
                return False

            print(f"Character U+{char_code:04X} found in segment {segment_index}")

            # Calculate new idDelta
            new_id_delta = new_glyph_id - char_code

            # Check if we need to isolate the character
            start_code = cmap_format4.start_code[segment_index]
            end_code = cmap_format4.end_code[segment_index]

            if start_code == char_code and end_code == char_code:
                # Character is already isolated, just modify idDelta
                return self._update_id_delta_directly(subtable_offset, segment_index, new_id_delta)
            else:
                # Need to split segment to isolate character
                return self._isolate_and_modify_character(
                    subtable_offset, cmap_format4, segment_index, char_code, new_id_delta
                )

        except Exception as e:
            print(f"Error modifying idDelta: {e}")
            return False

    def _find_segment_for_char(self, cmap_format4: CmapFormat4, char_code: int) -> int:
        """Find which segment contains the given character code."""
        for i, (start, end) in enumerate(zip(cmap_format4.start_code, cmap_format4.end_code)):
            if start <= char_code <= end:
                return i
        return -1

    def _update_id_delta_directly(self, subtable_offset: int, segment_index: int, new_id_delta: int) -> bool:
        """Update idDelta directly for an already isolated character."""
        try:
            # Calculate offset to idDelta array in the binary data
            offset = self.cmap_offset + subtable_offset + 14  # Skip format 4 header

            # Skip endCode array
            seg_count = (struct.unpack('>H', self.font_data[self.cmap_offset + subtable_offset + 6:self.cmap_offset + subtable_offset + 8])[0]) // 2
            offset += seg_count * 2

            # Skip reserved padding
            offset += 2

            # Skip startCode array
            offset += seg_count * 2

            # Now we're at idDelta array, go to the specific segment
            id_delta_offset = offset + (segment_index * 2)

            # Update the idDelta value
            original_id_delta = struct.unpack('>h', self.font_data[id_delta_offset:id_delta_offset+2])[0]
            struct.pack_into('>h', self.font_data, id_delta_offset, new_id_delta)

            print(f"Updated idDelta for segment {segment_index}: {original_id_delta} -> {new_id_delta}")
            return True

        except Exception as e:
            print(f"Error updating idDelta directly: {e}")
            return False

    def _isolate_and_modify_character(self,
                                    subtable_offset: int,
                                    cmap_format4: CmapFormat4,
                                    segment_index: int,
                                    char_code: int,
                                    new_id_delta: int) -> bool:
        """
        Isolate a character in its own segment and modify its idDelta.
        This implements the segment splitting technique from the paper.
        """
        try:
            # Create new segment arrays
            new_segments = self._split_segment_for_isolation(
                cmap_format4, segment_index, char_code, new_id_delta
            )

            # Rebuild the entire cmap format 4 subtable
            return self._rebuild_cmap_format4_subtable(subtable_offset, new_segments)

        except Exception as e:
            print(f"Error isolating and modifying character: {e}")
            return False

    def _split_segment_for_isolation(self,
                                   cmap_format4: CmapFormat4,
                                   segment_index: int,
                                   char_code: int,
                                   new_id_delta: int) -> CmapFormat4:
        """Split a segment to isolate a specific character."""
        original_start = cmap_format4.start_code[segment_index]
        original_end = cmap_format4.end_code[segment_index]
        original_id_delta = cmap_format4.id_delta[segment_index]
        original_id_range_offset = cmap_format4.id_range_offset[segment_index]

        # Create new arrays
        new_end_code = []
        new_start_code = []
        new_id_delta = []
        new_id_range_offset = []

        # Copy segments before the target segment
        for i in range(segment_index):
            new_end_code.append(cmap_format4.end_code[i])
            new_start_code.append(cmap_format4.start_code[i])
            new_id_delta.append(cmap_format4.id_delta[i])
            new_id_range_offset.append(cmap_format4.id_range_offset[i])

        # Split the target segment
        if original_start < char_code:
            # Add segment before the character
            new_end_code.append(char_code - 1)
            new_start_code.append(original_start)
            new_id_delta.append(original_id_delta)
            new_id_range_offset.append(original_id_range_offset)

        # Add isolated segment for the character
        new_end_code.append(char_code)
        new_start_code.append(char_code)
        new_id_delta.append(new_id_delta)
        new_id_range_offset.append(0)

        if char_code < original_end:
            # Add segment after the character
            new_end_code.append(original_end)
            new_start_code.append(char_code + 1)
            new_id_delta.append(original_id_delta)
            new_id_range_offset.append(original_id_range_offset)

        # Copy segments after the target segment
        for i in range(segment_index + 1, len(cmap_format4.end_code)):
            new_end_code.append(cmap_format4.end_code[i])
            new_start_code.append(cmap_format4.start_code[i])
            new_id_delta.append(cmap_format4.id_delta[i])
            new_id_range_offset.append(cmap_format4.id_range_offset[i])

        # Update header values
        new_seg_count = len(new_end_code)
        new_seg_count_x2 = new_seg_count * 2

        # Calculate other header values
        search_range = 2 * (2 ** int(new_seg_count.bit_length() - 1))
        entry_selector = int(new_seg_count.bit_length() - 1)
        range_shift = new_seg_count_x2 - search_range

        return CmapFormat4(
            format=4,
            length=0,  # Will be calculated during rebuild
            language=cmap_format4.language,
            seg_count_x2=new_seg_count_x2,
            search_range=search_range,
            entry_selector=entry_selector,
            range_shift=range_shift,
            end_code=new_end_code,
            reserved_pad=0,
            start_code=new_start_code,
            id_delta=new_id_delta,
            id_range_offset=new_id_range_offset,
            glyph_id_array=cmap_format4.glyph_id_array  # Copy original for now
        )

    def _rebuild_cmap_format4_subtable(self, subtable_offset: int, new_segments: CmapFormat4) -> bool:
        """Rebuild the entire cmap format 4 subtable with new segments."""
        try:
            # Calculate new subtable size
            seg_count = len(new_segments.end_code)
            header_size = 14
            arrays_size = seg_count * 8 + 2  # 4 arrays of seg_count words + reserved padding
            glyph_array_size = len(new_segments.glyph_id_array) * 2
            new_length = header_size + arrays_size + glyph_array_size

            new_segments.length = new_length

            # Build new subtable data
            subtable_data = bytearray()

            # Header
            subtable_data.extend(struct.pack('>H', new_segments.format))
            subtable_data.extend(struct.pack('>H', new_segments.length))
            subtable_data.extend(struct.pack('>H', new_segments.language))
            subtable_data.extend(struct.pack('>H', new_segments.seg_count_x2))
            subtable_data.extend(struct.pack('>H', new_segments.search_range))
            subtable_data.extend(struct.pack('>H', new_segments.entry_selector))
            subtable_data.extend(struct.pack('>H', new_segments.range_shift))

            # Arrays
            for end_code in new_segments.end_code:
                subtable_data.extend(struct.pack('>H', end_code))

            subtable_data.extend(struct.pack('>H', new_segments.reserved_pad))

            for start_code in new_segments.start_code:
                subtable_data.extend(struct.pack('>H', start_code))

            for id_delta in new_segments.id_delta:
                subtable_data.extend(struct.pack('>h', id_delta))

            for id_range_offset in new_segments.id_range_offset:
                subtable_data.extend(struct.pack('>H', id_range_offset))

            for glyph_id in new_segments.glyph_id_array:
                subtable_data.extend(struct.pack('>H', glyph_id))

            # Replace subtable data in font
            start_offset = self.cmap_offset + subtable_offset
            end_offset = start_offset + len(subtable_data)

            # This is a simplified replacement - in practice, you'd need to handle
            # size changes and update table directory
            if len(subtable_data) <= len(self.original_cmap_data):
                self.font_data[start_offset:end_offset] = subtable_data
                print(f"Rebuilt cmap format 4 subtable with {seg_count} segments")
                return True
            else:
                print("New subtable is larger than original - complex table reorganization needed")
                return False

        except Exception as e:
            print(f"Error rebuilding cmap format 4 subtable: {e}")
            return False

    def save_modified_font(self, output_path: str) -> bool:
        """Save the modified font binary data."""
        try:
            with open(output_path, 'wb') as f:
                f.write(self.font_data)

            print(f"Modified font saved to: {output_path}")
            return True

        except Exception as e:
            print(f"Error saving modified font: {e}")
            return False

    def restore_original_cmap(self) -> bool:
        """Restore the original cmap table data."""
        if not self.original_cmap_data or not self.cmap_offset:
            return False

        try:
            cmap_length = len(self.original_cmap_data)
            self.font_data[self.cmap_offset:self.cmap_offset + cmap_length] = self.original_cmap_data
            print("Restored original cmap table")
            return True

        except Exception as e:
            print(f"Error restoring original cmap: {e}")
            return False


# Example usage
if __name__ == "__main__":
    manipulator = BinaryFontManipulator()

    # Example font path - you'll need to provide an actual font file
    font_path = "example_font.ttf"

    if manipulator.load_font_binary(font_path):
        print("\\nAnalyzing font structure...")

        # Find Unicode subtable
        subtable_info = manipulator.find_unicode_subtable()
        if subtable_info:
            subtable_offset, table_index = subtable_info
            print(f"Found Unicode subtable at offset 0x{subtable_offset:08X}")

            # Parse cmap format 4
            cmap_format4 = manipulator.parse_cmap_format4(subtable_offset)
            if cmap_format4:
                print(f"Parsed cmap format 4 with {len(cmap_format4.end_code)} segments")

                # Example: modify character 'b' (0x62) to appear as 'a' glyph
                char_code = ord('b')
                # Assuming 'a' glyph is at ID 68 (you'd need to determine this from the font)
                target_glyph_id = 68

                if manipulator.modify_id_delta_for_character(char_code, target_glyph_id):
                    print(f"\\nModified character mapping for 'b'")

                    # Save modified font
                    output_path = "modified_font_binary.ttf"
                    if manipulator.save_modified_font(output_path):
                        print(f"Modified font saved to {output_path}")
                else:
                    print("Failed to modify character mapping")
            else:
                print("Failed to parse cmap format 4")
        else:
            print("Unicode subtable not found")
    else:
        print(f"Failed to load font: {font_path}")