#!/usr/bin/env python3
"""
PERFECT Font Manipulation - Make "world" LOOK exactly like "hello" and COPY exactly as "world"
"""

import os
import shutil
import tempfile
from fontTools.ttLib import TTFont
import subprocess

def create_perfect_manipulation():
    """
    Create perfect mapping:
    - User types: w o r l d
    - It looks like: h e l l o
    - It copies as: w o r l d
    """
    print("=" * 70)
    print("  PERFECT FONT MANIPULATION")
    print("  Type 'world' → Looks like 'hello' → Copies as 'world'")
    print("=" * 70)
    print()

    # The correct mapping
    mappings = {
        'w': 'h',  # w displays as h
        'o': 'e',  # first o displays as e
        'r': 'l',  # r displays as l
        'l': 'l',  # l displays as l
        'd': 'o'   # d displays as o
    }

    print("Font Mapping:")
    for typed, shows in mappings.items():
        print(f"  Type '{typed}' → Shows '{shows}'")

    print("\nResult:")
    print("  Type: w-o-r-l-d")
    print("  Show: h-e-l-l-o")
    print()

    # Load font
    input_font = 'Roboto.ttf'

    if not os.path.exists(input_font):
        print(f"❌ Font not found: {input_font}")
        return False

    print(f"✅ Loading font: {input_font}")
    font = TTFont(input_font)

    # Get cmap
    unicode_cmap = None
    for table in font['cmap'].tables:
        if table.platformID == 3 and table.platEncID == 1:
            unicode_cmap = table
            break

    if not unicode_cmap:
        print("❌ No suitable cmap table found")
        return False

    print(f"✅ Found cmap table (format {unicode_cmap.format})")
    print("\nApplying glyph mappings...")

    # Apply mappings
    for type_char, display_char in mappings.items():
        type_code = ord(type_char)
        display_code = ord(display_char)

        if display_code in unicode_cmap.cmap:
            target_glyph = unicode_cmap.cmap[display_code]
            unicode_cmap.cmap[type_code] = target_glyph
            print(f"  ✅ '{type_char}' (U+{type_code:04X}) → glyph of '{display_char}' ({target_glyph})")

    # Save font
    output_font = 'perfect_font.ttf'
    font.save(output_font)
    print(f"\n✅ Saved manipulated font: {output_font}")

    # Create LaTeX PDF
    print("\n📄 Creating PDF with LaTeX...")

    temp_dir = tempfile.mkdtemp()
    try:
        # Copy font
        shutil.copy(output_font, os.path.join(temp_dir, 'perfect_font.ttf'))

        # Create LaTeX document
        tex_content = r"""\documentclass[12pt]{article}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage[margin=1in]{geometry}

\setmainfont{perfect_font}[
    Path = """ + temp_dir + r"""/,
    Extension = .ttf
]

\begin{document}

\begin{center}
{\Huge \textbf{Perfect Font Manipulation}}\\[0.5cm]
{\large The word "world" looks like "hello"}
\end{center}

\vspace{2cm}

\begin{center}
{\huge \textbf{TEST THIS:}}
\end{center}

\vspace{1cm}

\begin{center}
\fbox{\parbox{0.8\textwidth}{
\begin{enumerate}
    \item Look at the RED text below
    \item It will appear as: \textcolor{green}{\textbf{"hello"}}
    \item Select and COPY the RED text
    \item Paste into any text editor
    \item You will see: \textcolor{blue}{\textbf{"world"}}
\end{enumerate}
}}
\end{center}

\vspace{2cm}

\begin{center}
{\Huge \textcolor{red}{\textbf{world}}}
\end{center}

\vspace{1cm}

\begin{center}
\textit{(This text contains the Unicode characters: w-o-r-l-d)}\\
\textit{(But displays the glyphs: h-e-l-l-o)}
\end{center}

\vspace{2cm}

\subsection*{How This Works:}

\begin{itemize}
    \item The font's cmap table has been modified
    \item Unicode for 'w' points to glyph of 'h'
    \item Unicode for 'o' points to glyph of 'e'
    \item Unicode for 'r' points to glyph of 'l'
    \item Unicode for 'l' points to glyph of 'l' (unchanged)
    \item Unicode for 'd' points to glyph of 'o'
\end{itemize}

Therefore:
\begin{itemize}
    \item Actual text: \texttt{world} (w-o-r-l-d)
    \item Visual appearance: \textbf{world} (looks like h-e-l-l-o)
    \item Copy-paste reveals: \texttt{world}
\end{itemize}

\vspace{1cm}

\begin{center}
\small{\textit{Font Manipulation Research - arXiv:2505.16957}}\\
\small{\textit{For educational and defensive security research only}}
\end{center}

\end{document}
"""

        tex_file = os.path.join(temp_dir, 'document.tex')
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(tex_content)

        # Compile
        print("  Compiling with XeLaTeX...")
        result = subprocess.run(
            ['xelatex', '-interaction=nonstopmode', 'document.tex'],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )

        # Run twice for references
        subprocess.run(
            ['xelatex', '-interaction=nonstopmode', 'document.tex'],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )

        # Copy PDF
        pdf_src = os.path.join(temp_dir, 'document.pdf')
        pdf_dst = 'perfect_manipulation.pdf'

        if os.path.exists(pdf_src):
            shutil.copy(pdf_src, pdf_dst)
            print(f"  ✅ PDF created: {pdf_dst}")
            return pdf_dst
        else:
            print("  ❌ PDF creation failed")
            return None

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    pdf_file = create_perfect_manipulation()

    if pdf_file:
        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"\n📄 PDF: {pdf_file}")
        print(f"🔤 Font: perfect_font.ttf")
        print()
        print("🎯 VERIFY NOW:")
        print("  1. Open the PDF")
        print("  2. You'll see text that LOOKS like 'hello'")
        print("  3. Copy the BIG RED text")
        print("  4. Paste into TextEdit")
        print("  5. You'll see 'world' (not 'hello'!)")
        print()
        print("Opening PDF...")
        os.system(f'open "{pdf_file}"')
