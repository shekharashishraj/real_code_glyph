#!/usr/bin/env python3
"""
TRUE Font Manipulation - Make 'hello' COPY as 'world' but LOOK like 'hello'
Uses actual TrueType font glyph mapping modification
"""

import os
import sys
import tempfile
import shutil
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
import subprocess

def create_manipulated_font(input_font_path, output_font_path, mappings):
    """
    Create a font where specific characters map to different glyphs.

    Args:
        input_font_path: Path to source TTF font
        output_font_path: Path to save modified font
        mappings: Dict like {'h': 'w', 'e': 'o', 'l': 'r', 'o': 'l', ...}
                 Maps what you TYPE to what glyph it should DISPLAY
    """
    print(f"Loading font: {input_font_path}")
    font = TTFont(input_font_path)

    # Get the cmap table (character to glyph mapping)
    cmap = font['cmap']

    # Find the Unicode BMP cmap table
    unicode_cmap = None
    for table in cmap.tables:
        if table.platformID == 3 and table.platEncID == 1:  # Windows Unicode BMP
            unicode_cmap = table
            break

    if not unicode_cmap:
        for table in cmap.tables:
            if table.platformID == 0:  # Unicode
                unicode_cmap = table
                break

    if not unicode_cmap:
        raise ValueError("No suitable cmap table found")

    print(f"Found cmap table: format {unicode_cmap.format}")
    print(f"\nApplying mappings:")

    # Store original mappings
    original_mappings = {}

    # Apply each mapping
    for type_char, display_char in mappings.items():
        type_code = ord(type_char)
        display_code = ord(display_char)

        # Get the glyph name for the character we want to display
        if display_code in unicode_cmap.cmap:
            target_glyph = unicode_cmap.cmap[display_code]

            # Store original mapping
            if type_code in unicode_cmap.cmap:
                original_mappings[type_char] = unicode_cmap.cmap[type_code]

            # Remap: when user types 'type_char', show glyph of 'display_char'
            unicode_cmap.cmap[type_code] = target_glyph

            print(f"  '{type_char}' (U+{type_code:04X}) → displays as '{display_char}' (glyph: {target_glyph})")
        else:
            print(f"  ⚠️  Warning: '{display_char}' not found in font")

    # Save modified font
    print(f"\nSaving modified font to: {output_font_path}")
    font.save(output_font_path)

    return original_mappings

def create_latex_pdf(text_to_type, text_visual_appearance, font_path, output_pdf):
    """
    Create a PDF using LaTeX with the manipulated font.

    Args:
        text_to_type: What user types (e.g., "world")
        text_visual_appearance: What it should look like (e.g., "hello")
        font_path: Path to manipulated font
        output_pdf: Output PDF path
    """
    print(f"\n📄 Creating LaTeX PDF...")
    print(f"   Text typed: {text_to_type}")
    print(f"   Visual appearance: {text_visual_appearance}")

    # Create temporary directory for LaTeX
    temp_dir = tempfile.mkdtemp()

    try:
        # Copy font to temp directory
        font_name = os.path.basename(font_path)
        temp_font_path = os.path.join(temp_dir, font_name)
        shutil.copy(font_path, temp_font_path)

        # Create LaTeX document
        tex_file = os.path.join(temp_dir, 'document.tex')

        latex_content = r"""\documentclass[12pt]{article}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage[margin=1in]{geometry}

% Set the manipulated font
\setmainfont{""" + font_name.replace('.ttf', '') + r"""}[
    Path = """ + temp_dir + r"""/,
    Extension = .ttf,
    UprightFont = """ + font_name + r"""
]

\begin{document}

\begin{center}
{\Huge \textbf{Font Manipulation Demonstration}}\\[0.5cm]
{\large Based on arXiv:2505.16957}
\end{center}

\vspace{1cm}

\section*{Visual Deception Test}

\subsection*{Instructions:}
\begin{enumerate}
    \item \textbf{Look} at the text below - note what you SEE
    \item \textbf{Copy} the red text (Ctrl+C / Cmd+C)
    \item \textbf{Paste} it into a text editor (Ctrl+V / Cmd+V)
    \item \textbf{Compare} - the copied text will be DIFFERENT!
\end{enumerate}

\vspace{1cm}

\subsection*{What You SEE:}
\begin{center}
{\huge \textcolor{green}{\textbf{""" + text_visual_appearance + r"""}}}
\end{center}

\vspace{0.5cm}

\subsection*{What You COPY (try it!):}
\begin{center}
{\huge \textcolor{red}{\textbf{""" + text_to_type + r"""}}}
\end{center}

\vspace{1cm}

\subsection*{Explanation:}
This text uses a \textbf{manipulated font} where:
\begin{itemize}
    \item The Unicode characters for ``""" + text_to_type + r"""'' are present
    \item But they display the glyphs from ``""" + text_visual_appearance + r"""''
    \item Visual appearance $\neq$ Digital content
    \item Copy-paste reveals the actual Unicode values
\end{itemize}

\vspace{1cm}

\subsection*{How It Works:}
\begin{enumerate}
    \item TrueType fonts use a \texttt{cmap} table (character-to-glyph mapping)
    \item Formula: \texttt{GlyphIndex = idDelta + Unicode}
    \item By modifying the \texttt{cmap}, we redirect Unicode values to different glyphs
    \item Example: Unicode for 'w' points to glyph of 'h'
\end{enumerate}

\vspace{1cm}

\begin{center}
\textcolor{blue}{\textbf{Security Implications:}}
\end{center}

This technique can be used for:
\begin{itemize}
    \item \textcolor{red}{Attack:} Phishing, code injection, document fraud
    \item \textcolor{green}{Defense:} Detection systems, security research, awareness
\end{itemize}

\vspace{1cm}

\begin{center}
\small{\textit{For educational and defensive security research only}}\\
\textit{Research: arXiv:2505.16957}
\end{center}

\end{document}
"""

        # Write LaTeX file
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)

        print(f"   Created LaTeX file: {tex_file}")

        # Compile with XeLaTeX (supports fontspec)
        print("   Compiling with XeLaTeX...")

        result = subprocess.run(
            ['xelatex', '-interaction=nonstopmode', 'document.tex'],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("   ⚠️  First compilation (expected errors)")
            # Run again to resolve references
            result = subprocess.run(
                ['xelatex', '-interaction=nonstopmode', 'document.tex'],
                cwd=temp_dir,
                capture_output=True,
                text=True
            )

        # Check if PDF was created
        output_pdf_temp = os.path.join(temp_dir, 'document.pdf')
        if os.path.exists(output_pdf_temp):
            shutil.copy(output_pdf_temp, output_pdf)
            print(f"   ✅ PDF created: {output_pdf}")
            return True
        else:
            print(f"   ❌ PDF creation failed")
            print("   LaTeX output:")
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            return False

    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

def extract_text_from_pdf(pdf_path):
    """Extract actual text content from PDF."""
    import PyPDF2

    print(f"\n📖 Extracting text from PDF: {pdf_path}")

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

    return text

def test_font_manipulation():
    """Complete test of font manipulation."""
    print("=" * 70)
    print("  TRUE FONT MANIPULATION TEST")
    print("  Make 'hello' COPY as 'world' but LOOK like 'hello'")
    print("=" * 70)
    print()

    # Check for required tools
    if shutil.which('xelatex') is None:
        print("❌ XeLaTeX not found!")
        print("   Install MacTeX: brew install --cask mactex")
        print("   Or BasicTeX: brew install --cask basictex")
        return False

    # Define the mapping
    # To make "world" LOOK like "hello":
    # w → h, o → e, r → l, l → l, d → o
    mappings = {
        'w': 'h',  # When user types 'w', show glyph 'h'
        'o': 'e',  # When user types 'o', show glyph 'e'
        'r': 'l',  # When user types 'r', show glyph 'l'
        'l': 'l',  # When user types 'l', show glyph 'l' (no change)
        'd': 'o'   # When user types 'd', show glyph 'o'
    }

    # Use the downloaded font
    input_font = 'Roboto.ttf'

    if not os.path.exists(input_font):
        print(f"❌ Font not found: {input_font}")
        print("   Downloading...")
        os.system('curl -L -o Roboto.ttf "https://github.com/google/fonts/raw/refs/heads/main/ofl/roboto/Roboto%5Bwdth%2Cwght%5D.ttf"')

    # Create manipulated font
    output_font = 'manipulated_font.ttf'

    try:
        create_manipulated_font(input_font, output_font, mappings)

        # Create PDF
        # User will type: "world"
        # It will look like: "hello"
        output_pdf = 'true_manipulation_demo.pdf'

        success = create_latex_pdf(
            text_to_type="world",
            text_visual_appearance="hello",
            font_path=output_font,
            output_pdf=output_pdf
        )

        if success:
            # Test: Extract text
            extracted = extract_text_from_pdf(output_pdf)

            print("\n" + "=" * 70)
            print("📊 TEST RESULTS:")
            print("=" * 70)
            print(f"✅ Modified font created: {output_font}")
            print(f"✅ PDF created: {output_pdf}")
            print(f"\n📝 Extracted text contains:")

            # Look for our manipulated text
            if 'world' in extracted.lower():
                print(f"   ✅ Found 'world' in extracted text!")
                print(f"   This is the ACTUAL Unicode content")

            if 'hello' in extracted.lower():
                print(f"   ⚠️  Also found 'hello' (from headers/explanations)")

            print(f"\n🎯 NOW DO THIS:")
            print(f"   1. Open: {output_pdf}")
            print(f"   2. Look at the RED text - it will LOOK like 'hello'")
            print(f"   3. Copy the RED text")
            print(f"   4. Paste into text editor")
            print(f"   5. You'll see: 'world' (not 'hello'!)")
            print()

            # Open PDF
            os.system(f'open "{output_pdf}"')

            return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_font_manipulation()
