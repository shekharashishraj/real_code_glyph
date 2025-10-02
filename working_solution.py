#!/usr/bin/env python3
"""
WORKING SOLUTION - Real character substitution that survives PDF encoding
Creates actual different Unicode that looks the same
"""

import os
import shutil
import tempfile
from fontTools.ttLib import TTFont
import subprocess

def create_working_manipulation():
    """
    Use homoglyphs approach: characters that naturally look similar
    but have different Unicode values that SURVIVE PDF encoding.
    """
    print("=" * 70)
    print("  WORKING FONT MANIPULATION")
    print("  Using real Unicode substitution that survives PDF")
    print("=" * 70)
    print()

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

    # Strategy: Map Cyrillic/Greek characters to Latin glyphs
    # These SURVIVE PDF encoding and extraction

    # Cyrillic/Greek letters that look like Latin:
    # а (Cyrillic a U+0430) → looks like 'a'
    # е (Cyrillic ye U+0435) → looks like 'e'
    # о (Cyrillic o U+043E) → looks like 'o'
    # р (Cyrillic er U+0440) → looks like 'p'
    # с (Cyrillic es U+0441) → looks like 'c'
    # у (Cyrillic u U+0443) → looks like 'y'
    # х (Cyrillic kha U+0445) → looks like 'x'

    # For "world" -> "hello" we need:
    # Map Cyrillic chars to display as English "hello" letters

    mappings = {
        # Cyrillic char → should display as English char
        0x0443: ord('h'),  # у (Cyrillic u) → displays 'h'
        0x043E: ord('e'),  # о (Cyrillic o) → displays 'e'
        0x0440: ord('l'),  # р (Cyrillic er) → displays 'l'
        0x0441: ord('l'),  # с (Cyrillic es) → displays 'l'
        0x0430: ord('o'),  # а (Cyrillic a) → displays 'o'
    }

    print("\n📝 Creating Cyrillic → Latin glyph mappings:")
    for cyrillic_code, latin_code in mappings.items():
        cyrillic_char = chr(cyrillic_code)
        latin_char = chr(latin_code)

        if latin_code in unicode_cmap.cmap:
            target_glyph = unicode_cmap.cmap[latin_code]
            unicode_cmap.cmap[cyrillic_code] = target_glyph

            print(f"  '{cyrillic_char}' (U+{cyrillic_code:04X}) → glyph of '{latin_char}'")

    # Save font
    output_font = 'working_font.ttf'
    font.save(output_font)
    print(f"\n✅ Saved font: {output_font}")

    # Create the deceptive word using Cyrillic
    # We want it to LOOK like "hello" but BE Cyrillic chars
    deceptive_word = "уорса"  # Cyrillic: у о р с а
    # This will display as: h e l l o

    print(f"\n📝 Deceptive word created:")
    print(f"   Visual: hello")
    print(f"   Actual: {deceptive_word}")
    print(f"   Unicode: ", end="")
    for char in deceptive_word:
        print(f"U+{ord(char):04X} ", end="")
    print()

    # Create LaTeX PDF
    print("\n📄 Creating PDF with LaTeX...")

    temp_dir = tempfile.mkdtemp()
    try:
        shutil.copy(output_font, os.path.join(temp_dir, 'working_font.ttf'))

        tex_content = r"""\documentclass[12pt]{article}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage[margin=1in]{geometry}

\setmainfont{working_font}[
    Path = """ + temp_dir + r"""/,
    Extension = .ttf
]

\begin{document}

\begin{center}
{\Huge \textbf{Working Font Manipulation}}\\[0.5cm]
{\large Cyrillic characters display as English}
\end{center}

\vspace{2cm}

\section*{Verification Test}

Below you'll see the word "hello" appear THREE times.

\begin{itemize}
    \item First is NORMAL English (h-e-l-l-o)
    \item Second is CYRILLIC but LOOKS like English
    \item Third is NORMAL English again
\end{itemize}

\vspace{1cm}

\begin{center}
\fbox{\parbox{0.9\textwidth}{
\textbf{TEST:}
\begin{enumerate}
    \item Copy the RED word below
    \item Paste into a text editor
    \item You'll see Cyrillic characters (or boxes)!
\end{enumerate}
}}
\end{center}

\vspace{2cm}

\begin{center}
{\LARGE Normal English: \textbf{hello}}\\[1cm]
{\Huge \textcolor{red}{Manipulated: \textbf{""" + deceptive_word + r"""}}}\\[1cm]
{\LARGE Normal English: \textbf{hello}}
\end{center}

\vspace{2cm}

\subsection*{What's Happening:}

\begin{itemize}
    \item The RED word contains Cyrillic Unicode: у о р с а
    \item But the font makes them display as: h e l l o
    \item When you copy-paste, you get Cyrillic characters!
    \item Visual appearance $\neq$ Digital content
\end{itemize}

\subsection*{Unicode Breakdown:}

\begin{tabular}{lll}
\textbf{Visual} & \textbf{Actual Char} & \textbf{Unicode} \\
\hline
h & у (Cyrillic u) & U+0443 \\
e & о (Cyrillic o) & U+043E \\
l & р (Cyrillic er) & U+0440 \\
l & с (Cyrillic es) & U+0441 \\
o & а (Cyrillic a) & U+0430 \\
\end{tabular}

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

        print("  Compiling with XeLaTeX...")

        for _ in range(2):
            subprocess.run(
                ['xelatex', '-interaction=nonstopmode', 'document.tex'],
                cwd=temp_dir,
                capture_output=True,
                text=True
            )

        pdf_src = os.path.join(temp_dir, 'document.pdf')
        pdf_dst = 'working_manipulation.pdf'

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
    pdf_file = create_working_manipulation()

    if pdf_file:
        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"\n📄 PDF: {pdf_file}")
        print(f"🔤 Font: working_font.ttf")
        print()
        print("🎯 TEST NOW:")
        print("  1. Open the PDF")
        print("  2. See 3 'hello' words - all look identical")
        print("  3. Copy the RED 'hello' (middle one)")
        print("  4. Paste into text editor")
        print("  5. You'll see: уорса (Cyrillic!) or boxes")
        print()
        print("This PROVES the Unicode is different!")
        print()

        os.system(f'open "{pdf_file}"')
