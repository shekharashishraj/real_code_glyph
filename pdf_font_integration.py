#!/usr/bin/env python3
"""
PDF Font Integration Module
Integrates font manipulation with PDF generation pipeline
Combines manipulated fonts with PDF creation and text rendering
"""

import os
import tempfile
from typing import Dict, List, Tuple, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import black, red, blue
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import PyPDF2
from io import BytesIO

from enhanced_font_manipulator import EnhancedFontManipulator
from font_manipulator import WordMappingManager


class PDFFontIntegrator:
    """
    Integrates font manipulation with PDF generation.
    Creates PDFs where text appears visually different from its Unicode content.
    """

    def __init__(self):
        self.font_manipulator = EnhancedFontManipulator()
        self.word_manager = WordMappingManager()
        self.modified_fonts = {}
        self.font_mappings = {}

    def load_base_font(self, font_path: str) -> bool:
        """Load the base font for manipulation."""
        try:
            success = (self.font_manipulator.load_font(font_path) and
                      self.word_manager.load_font(font_path))

            if success:
                print(f"Loaded base font: {os.path.basename(font_path)}")

            return success
        except Exception as e:
            print(f"Error loading base font: {e}")
            return False

    def create_word_mappings(self, mappings: List[Dict[str, str]]) -> bool:
        """
        Create word mappings for PDF generation.

        Args:
            mappings: List of dictionaries with 'original' and 'replacement' keys
        """
        try:
            self.font_mappings = {}

            for mapping in mappings:
                original = mapping.get('original', '').strip()
                replacement = mapping.get('replacement', '').strip()

                if not original or not replacement:
                    continue

                # Create mapping in both manipulators
                self.font_manipulator.create_deceptive_mapping_with_idelta(
                    replacement, replacement, original
                )

                self.word_manager.create_word_mapping(original, replacement)

                # Store mapping for text transformation
                self.font_mappings[original] = replacement

                print(f"Created mapping: '{original}' -> '{replacement}' (visually appears as '{original}')")

            return len(self.font_mappings) > 0

        except Exception as e:
            print(f"Error creating word mappings: {e}")
            return False

    def generate_modified_font(self, base_font_path: str) -> Optional[str]:
        """Generate a modified font file with all mappings applied."""
        try:
            # Create temporary file for modified font
            with tempfile.NamedTemporaryFile(suffix='.ttf', delete=False) as temp_file:
                modified_font_path = temp_file.name

            # Generate using the enhanced manipulator
            if self.font_manipulator.generate_modified_font(modified_font_path):
                font_name = f"ModifiedFont_{os.getpid()}"
                self.modified_fonts[font_name] = modified_font_path

                print(f"Generated modified font: {modified_font_path}")
                return font_name
            else:
                return None

        except Exception as e:
            print(f"Error generating modified font: {e}")
            return None

    def register_font_with_reportlab(self, font_name: str, font_path: str) -> bool:
        """Register the modified font with ReportLab."""
        try:
            ttfont = TTFont(font_name, font_path)
            pdfmetrics.registerFont(ttfont)
            print(f"Registered font '{font_name}' with ReportLab")
            return True
        except Exception as e:
            print(f"Error registering font with ReportLab: {e}")
            return False

    def transform_text_for_mapping(self, text: str) -> str:
        """Transform input text according to the font mappings."""
        transformed = text

        for original, replacement in self.font_mappings.items():
            transformed = transformed.replace(original, replacement)

        return transformed

    def create_comparison_pdf(self,
                            text: str,
                            output_path: str,
                            show_comparison: bool = True) -> bool:
        """
        Create a PDF showing the font manipulation effects.

        Args:
            text: Original text to display
            output_path: Path for the generated PDF
            show_comparison: Whether to show before/after comparison
        """
        try:
            # Generate modified font
            base_font_path = self.font_manipulator.font_path
            if not base_font_path:
                print("No base font loaded")
                return False

            modified_font_name = self.generate_modified_font(base_font_path)
            if not modified_font_name:
                print("Failed to generate modified font")
                return False

            modified_font_path = self.modified_fonts[modified_font_name]

            # Register fonts with ReportLab
            original_font_name = "OriginalFont"
            try:
                original_ttfont = TTFont(original_font_name, base_font_path)
                pdfmetrics.registerFont(original_ttfont)
            except:
                original_font_name = "Helvetica"  # Fallback

            if not self.register_font_with_reportlab(modified_font_name, modified_font_path):
                return False

            # Create PDF
            c = canvas.Canvas(output_path, pagesize=letter)
            width, height = letter

            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Font Manipulation Demonstration")

            # Add mapping information
            y_pos = height - 80
            c.setFont("Helvetica", 12)
            c.drawString(50, y_pos, "Applied Mappings:")

            y_pos -= 20
            for original, replacement in self.font_mappings.items():
                mapping_text = f"  • '{original}' Unicode -> '{replacement}' Unicode (visually appears as '{original}')"
                c.drawString(60, y_pos, mapping_text)
                y_pos -= 15

            y_pos -= 30

            if show_comparison:
                # Original text section
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y_pos, "Original Text (Normal Font):")
                y_pos -= 25

                c.setFont(original_font_name, 12)
                c.drawString(60, y_pos, text)
                y_pos -= 40

                # Modified text section
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y_pos, "Modified Text (Manipulated Font):")
                y_pos -= 25

            # Transform text according to mappings
            transformed_text = self.transform_text_for_mapping(text)

            # Draw with modified font
            c.setFont(modified_font_name, 12)
            c.drawString(60, y_pos, transformed_text)
            y_pos -= 40

            if show_comparison:
                # Unicode comparison
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y_pos, "Unicode Analysis:")
                y_pos -= 25

                c.setFont("Courier", 10)
                c.drawString(60, y_pos, f"Original Unicode:   {' '.join([f'U+{ord(char):04X}' for char in text[:20]])}")
                y_pos -= 15
                c.drawString(60, y_pos, f"Modified Unicode:   {' '.join([f'U+{ord(char):04X}' for char in transformed_text[:20]])}")
                y_pos -= 30

                # Visual explanation
                c.setFont("Helvetica", 10)
                explanation = [
                    "The modified text has different Unicode values but appears visually identical",
                    "to the original text when rendered with the manipulated font.",
                    "",
                    "This demonstrates the technique described in arXiv:2505.16957 where",
                    "font glyph mappings are modified to create deceptive content."
                ]

                for line in explanation:
                    c.drawString(60, y_pos, line)
                    y_pos -= 12

            c.save()
            print(f"Comparison PDF created: {output_path}")
            return True

        except Exception as e:
            print(f"Error creating comparison PDF: {e}")
            return False

    def create_steganographic_pdf(self,
                                visible_text: str,
                                hidden_text: str,
                                output_path: str) -> bool:
        """
        Create a PDF with steganographic text using font manipulation.

        Args:
            visible_text: Text that appears visually
            hidden_text: Text with different Unicode values
            output_path: Output PDF path
        """
        try:
            if len(visible_text) != len(hidden_text):
                print("Visible and hidden text must have the same length")
                return False

            # Create character-by-character mappings
            mappings = []
            for visible_char, hidden_char in zip(visible_text, hidden_text):
                if visible_char != hidden_char:
                    mappings.append({
                        'original': visible_char,
                        'replacement': hidden_char
                    })

            if not self.create_word_mappings(mappings):
                print("Failed to create character mappings")
                return False

            # Generate modified font
            base_font_path = self.font_manipulator.font_path
            modified_font_name = self.generate_modified_font(base_font_path)
            if not modified_font_name:
                return False

            modified_font_path = self.modified_fonts[modified_font_name]
            if not self.register_font_with_reportlab(modified_font_name, modified_font_path):
                return False

            # Create PDF with steganographic content
            c = canvas.Canvas(output_path, pagesize=letter)
            width, height = letter

            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Steganographic Document")

            c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, "This document contains hidden information in the font encoding.")

            # Main content with hidden text
            c.setFont(modified_font_name, 14)
            c.drawString(50, height - 120, hidden_text)

            c.save()
            print(f"Steganographic PDF created: {output_path}")
            return True

        except Exception as e:
            print(f"Error creating steganographic PDF: {e}")
            return False

    def extract_hidden_unicode(self, pdf_path: str) -> Optional[str]:
        """
        Extract the actual Unicode content from a PDF (for analysis).
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()

                return text

        except Exception as e:
            print(f"Error extracting Unicode from PDF: {e}")
            return None

    def analyze_pdf_content(self, pdf_path: str) -> Dict:
        """Analyze PDF content to show the difference between visual and Unicode content."""
        try:
            # Extract actual Unicode content
            unicode_content = self.extract_hidden_unicode(pdf_path)
            if not unicode_content:
                return {}

            # Analyze character frequencies and mappings
            analysis = {
                'unicode_content': unicode_content,
                'character_count': len(unicode_content),
                'unique_characters': len(set(unicode_content)),
                'unicode_values': [f'U+{ord(char):04X}' for char in unicode_content[:50]],  # First 50 chars
                'mappings_detected': []
            }

            # Check which characters have mappings
            for char in set(unicode_content):
                char_code = ord(char)
                if char_code in self.font_manipulator.modifications:
                    mod_info = self.font_manipulator.modifications[char_code]
                    analysis['mappings_detected'].append({
                        'character': char,
                        'unicode': f'U+{char_code:04X}',
                        'visual_appearance': mod_info['visual_char']
                    })

            return analysis

        except Exception as e:
            print(f"Error analyzing PDF content: {e}")
            return {}

    def cleanup(self):
        """Clean up temporary font files."""
        for font_name, font_path in self.modified_fonts.items():
            try:
                if os.path.exists(font_path):
                    os.unlink(font_path)
                    print(f"Cleaned up temporary font: {font_path}")
            except Exception as e:
                print(f"Error cleaning up font {font_path}: {e}")

        self.modified_fonts.clear()


# Example usage and testing
if __name__ == "__main__":
    integrator = PDFFontIntegrator()

    # Example usage
    base_font_path = "example_font.ttf"  # You'll need to provide a real font file

    if os.path.exists(base_font_path):
        if integrator.load_base_font(base_font_path):
            print("\\nFont loaded successfully")

            # Create example mappings
            mappings = [
                {'original': 'hello', 'replacement': 'world'},
                {'original': 'test', 'replacement': 'demo'}
            ]

            if integrator.create_word_mappings(mappings):
                print("\\nMappings created successfully")

                # Create comparison PDF
                test_text = "This is a hello test document"
                output_pdf = "font_manipulation_demo.pdf"

                if integrator.create_comparison_pdf(test_text, output_pdf):
                    print(f"\\nDemo PDF created: {output_pdf}")

                    # Analyze the created PDF
                    analysis = integrator.analyze_pdf_content(output_pdf)
                    if analysis:
                        print("\\nPDF Analysis:")
                        print(f"  Characters: {analysis['character_count']}")
                        print(f"  Unique characters: {analysis['unique_characters']}")
                        print(f"  Mappings detected: {len(analysis['mappings_detected'])}")

                # Create steganographic PDF
                visible = "hello"
                hidden = "world"
                stego_pdf = "steganographic_demo.pdf"

                if integrator.create_steganographic_pdf(visible, hidden, stego_pdf):
                    print(f"\\nSteganographic PDF created: {stego_pdf}")

                # Cleanup
                integrator.cleanup()
            else:
                print("Failed to create mappings")
        else:
            print(f"Failed to load font: {base_font_path}")
    else:
        print(f"Font file not found: {base_font_path}")
        print("Please provide a valid TrueType font file to test the PDF integration.")