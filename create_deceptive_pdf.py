#!/usr/bin/env python3
"""
Create a PDF with visually deceptive text
Text that LOOKS like one thing but COPIES as something else
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black, blue, red, green
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from fontTools.ttLib import TTFont as FontToolsTTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
import tempfile
import os
import struct

def create_manipulated_font():
    """
    Create a simple manipulated font where certain characters
    visually appear as different characters.

    We'll use a simpler approach: use Unicode homoglyphs
    that look similar but have different codes.
    """
    print("Creating font with deceptive character mappings...")

    # For this demo, we'll use Unicode lookalike characters
    # These naturally look the same but have different codes
    mappings = {
        'visual': 'hello',  # What it looks like
        'actual': 'ηеllο',  # What it actually is (using Greek/Cyrillic lookalikes)
        # h → η (Greek eta U+03B7)
        # e → е (Cyrillic ie U+0435)
        # l → l (Latin l)
        # o → ο (Greek omicron U+03BF)
    }

    return mappings

def create_deceptive_pdf_with_unicode():
    """
    Create a PDF demonstrating visual deception using Unicode lookalikes.
    This works without complex font manipulation.
    """

    output_file = "deceptive_text_demo.pdf"

    print("🎯 Creating Deceptive Text PDF")
    print("=" * 70)

    # Create the PDF
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(blue)
    c.drawString(50, height - 60, "Visual Deception Demonstration")

    c.setFont("Helvetica", 12)
    c.setFillColor(black)
    c.drawString(50, height - 85, "Text that looks the same but copies differently!")

    y = height - 140

    # Instructions
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(red)
    c.drawString(50, y, "⚠️  TRY THIS: Copy the text below and paste it somewhere!")
    y -= 30

    c.setFont("Helvetica", 12)
    c.setFillColor(black)
    c.drawString(50, y, "You'll see that what copies is DIFFERENT from what you see!")
    y -= 50

    # Example 1: Using Unicode homoglyphs
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(blue)
    c.drawString(50, y, "Example 1: Word 'hello'")
    y -= 30

    # Visual appearance
    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    c.drawString(70, y, "What you SEE:")
    y -= 20

    c.setFont("Courier-Bold", 16)
    c.setFillColor(green)
    c.drawString(90, y, "hello")  # Looks normal
    y -= 25

    c.setFont("Courier", 10)
    c.setFillColor(black)
    c.drawString(90, y, "Unicode: U+0068 U+0065 U+006C U+006C U+006F")
    y -= 30

    # What you actually copy
    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    c.drawString(70, y, "What you COPY (try it!):")
    y -= 20

    # Using lookalike characters
    deceptive_text = "ηеllο"  # η(Greek) е(Cyrillic) l l ο(Greek)
    c.setFont("Courier-Bold", 16)
    c.setFillColor(red)
    c.drawString(90, y, deceptive_text)
    y -= 25

    c.setFont("Courier", 10)
    c.setFillColor(black)
    c.drawString(90, y, "Unicode: U+03B7 U+0435 U+006C U+006C U+03BF")
    y -= 25

    c.setFont("Helvetica-Oblique", 11)
    c.setFillColor(red)
    c.drawString(90, y, "👆 Copy this text and paste - you'll get Greek/Cyrillic characters!")
    y -= 50

    # Example 2: More complex
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(blue)
    c.drawString(50, y, "Example 2: Deceptive sentence")
    y -= 30

    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    c.drawString(70, y, "What you SEE:")
    y -= 20

    c.setFont("Times-Roman", 14)
    c.setFillColor(green)
    c.drawString(90, y, "Your password is: secret123")
    y -= 30

    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    c.drawString(70, y, "What you COPY:")
    y -= 20

    # Using homoglyphs for deception
    deceptive_sentence = "Yοur рassword іs: sеcrеt123"
    # Y=Latin, ο=Greek, u=Latin, r=Latin
    # р=Cyrillic, a=Latin, s=Latin, s=Latin, w=Latin, o=Latin, r=Latin, d=Latin
    # і=Cyrillic, s=Latin
    # s=Latin, е=Cyrillic, c=Latin, r=Latin, е=Cyrillic, t=Latin

    c.setFont("Times-Roman", 14)
    c.setFillColor(red)
    c.drawString(90, y, deceptive_sentence)
    y -= 25

    c.setFont("Helvetica-Oblique", 11)
    c.setFillColor(red)
    c.drawString(90, y, "👆 Looks identical but contains Cyrillic/Greek characters!")
    y -= 40

    # Explanation box
    c.setStrokeColor(blue)
    c.setLineWidth(2)
    c.rect(45, y - 80, width - 90, 70)

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(blue)
    c.drawString(55, y - 20, "💡 How This Works:")

    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    explanation = [
        "• Uses Unicode homoglyphs (characters that look identical but have different codes)",
        "• Greek 'ο' (omicron U+03BF) looks like Latin 'o' (U+006F)",
        "• Cyrillic 'е' (ie U+0435) looks like Latin 'e' (U+0065)",
        "• Visual appearance is identical, but copy-paste reveals different characters"
    ]

    line_y = y - 35
    for line in explanation:
        c.drawString(60, line_y, line)
        line_y -= 13

    y -= 100

    # Real-world implications
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(red)
    c.drawString(50, y, "⚠️  Real-World Security Implications:")
    y -= 25

    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    implications = [
        "✗ Phishing attacks: URLs that look legitimate but go elsewhere",
        "✗ Code injection: Variables that look the same but behave differently",
        "✗ Document fraud: Content appears authentic but contains hidden text",
        "✗ LLM attacks: Invisible prompts that humans can't detect",
        "",
        "✓ Detection: Check Unicode values, not just visual appearance",
        "✓ Validation: Use tools to detect homoglyph attacks",
        "✓ Awareness: Be cautious with copy-paste from untrusted sources"
    ]

    for line in implications:
        c.drawString(70, y, line)
        y -= 15

    # Footer
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(blue)
    c.drawString(50, 50, "🔬 Font Manipulation Research - arXiv:2505.16957")

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(black)
    c.drawString(50, 35, "This demonstration uses Unicode homoglyphs. Font manipulation can achieve similar effects")
    c.drawString(50, 22, "with any characters by modifying TrueType font glyph mappings.")

    # Save
    c.save()

    return output_file

def main():
    print("\n" + "=" * 70)
    print("  CREATING DECEPTIVE TEXT PDF DEMONSTRATION")
    print("=" * 70 + "\n")

    # Create the PDF
    pdf_file = create_deceptive_pdf_with_unicode()

    file_size = os.path.getsize(pdf_file)

    print("\n✅ PDF Created Successfully!")
    print("=" * 70)
    print(f"📄 File: {pdf_file}")
    print(f"📊 Size: {file_size:,} bytes")
    print()
    print("🎯 WHAT TO DO:")
    print("   1. Open the PDF")
    print("   2. Try to SELECT and COPY the text")
    print("   3. PASTE it into a text editor")
    print("   4. You'll see DIFFERENT characters than what appears in the PDF!")
    print()
    print("💡 This demonstrates how:")
    print("   • Text can LOOK like 'hello'")
    print("   • But COPY as 'ηеllο' (Greek/Cyrillic mix)")
    print("   • Visual appearance ≠ Digital content")
    print()
    print("🔍 Opening PDF now...")
    print("=" * 70)

    return pdf_file

if __name__ == "__main__":
    pdf_file = main()

    # Open the PDF
    os.system(f'open "{pdf_file}"')

    print("\n✨ PDF opened! Try copying the text to see the deception in action!")
    print()
