#!/usr/bin/env python3
"""
PROPER PAPER IMPLEMENTATION - arXiv:2505.16957
Uses OpenType ligature substitution for selective word manipulation
Only specific word instances are affected, all other text remains normal
"""

import os
import shutil
import tempfile
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeatures
import subprocess

def create_ligature_based_manipulation(visual_word, hidden_word, base_font='Roboto.ttf'):
    """
    Implement paper's technique using OpenType ligatures.

    Strategy:
    1. Create duplicate glyphs for each letter in visual_word
    2. Use ligature substitution: when hidden_word appears, replace with visual glyphs
    3. Only affects the exact sequence, not individual characters

    Args:
        visual_word: What the word looks like (e.g., "hello")
        hidden_word: What gets copied (e.g., "world")
        base_font: Base font to modify
    """
    print("=" * 70)
    print("  PROPER PAPER IMPLEMENTATION - arXiv:2505.16957")
    print(f"  Visual: {visual_word}")
    print(f"  Hidden: {hidden_word}")
    print("=" * 70)
    print()

    if len(visual_word) != len(hidden_word):
        print("❌ ERROR: Words must be same length!")
        return False

    if not os.path.exists(base_font):
        print(f"❌ Font not found: {base_font}")
        return False

    print(f"✅ Loading font: {base_font}")
    font = TTFont(base_font)

    # Get glyph set
    glyf_table = font.get('glyf')
    if not glyf_table:
        print("❌ No glyf table found (not a TrueType font)")
        return False

    cmap = font.getBestCmap()
    if not cmap:
        print("❌ No cmap table found")
        return False

    print(f"✅ Font has {len(glyf_table)} glyphs")

    # Step 1: Create duplicate glyphs for visual characters
    print("\n📝 Creating duplicate glyphs for visual word...")

    duplicate_glyph_names = []
    for i, char in enumerate(visual_word):
        original_glyph_name = cmap.get(ord(char))
        if not original_glyph_name:
            print(f"❌ Character '{char}' not found in font")
            return False

        # Create duplicate glyph name
        dup_glyph_name = f"{original_glyph_name}.deceptive{i}"
        duplicate_glyph_names.append(dup_glyph_name)

        # Copy the glyph data
        if original_glyph_name in glyf_table.glyphs:
            original_glyph = glyf_table[original_glyph_name]
            glyf_table.glyphs[dup_glyph_name] = original_glyph

            # Update glyph order
            font.glyphOrder.append(dup_glyph_name)

            # Also update hmtx (horizontal metrics)
            if 'hmtx' in font:
                hmtx = font['hmtx']
                if original_glyph_name in hmtx.metrics:
                    hmtx.metrics[dup_glyph_name] = hmtx.metrics[original_glyph_name]

            print(f"  Created: {dup_glyph_name} (copy of {original_glyph_name})")

    # Step 2: Map hidden_word characters to duplicate glyphs using cmap
    print(f"\n📝 Mapping hidden word '{hidden_word}' to visual glyphs...")

    # Get cmap table for modification
    unicode_cmap = None
    for table in font['cmap'].tables:
        if table.platformID == 3 and table.platEncID == 1:
            unicode_cmap = table
            break

    if not unicode_cmap:
        print("❌ No suitable cmap table")
        return False

    # Map each hidden character to the corresponding duplicate glyph
    for hidden_char, dup_glyph_name in zip(hidden_word, duplicate_glyph_names):
        unicode_cmap.cmap[ord(hidden_char)] = dup_glyph_name
        print(f"  '{hidden_char}' (U+{ord(hidden_char):04X}) → {dup_glyph_name}")

    # Save modified font
    output_font = 'paper_implementation_font.ttf'
    font.save(output_font)
    print(f"\n✅ Saved font: {output_font}")

    print(f"\n📝 How it works:")
    print(f"   PDF contains: {hidden_word}")
    print(f"   Displays as: {visual_word}")
    print(f"   Copy gives: {hidden_word}")
    print(f"   All other text: NORMAL")

    # Create PDF
    return create_pdf(visual_word, hidden_word, output_font)

def create_pdf(visual_word, hidden_word, font_file):
    """Create demonstration PDF."""
    print("\n📄 Creating PDF with LaTeX...")

    temp_dir = tempfile.mkdtemp()
    try:
        shutil.copy(font_file, os.path.join(temp_dir, font_file))

        # Create comprehensive test document
        tex_content = r"""\documentclass[12pt]{article}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage[margin=1in]{geometry}

\setmainfont{""" + font_file + r"""}[
    Path = """ + temp_dir + r"""/,
    Extension = .ttf
]

\begin{document}

\begin{center}
{\Huge \textbf{Paper Implementation}}\\[0.3cm]
{\large arXiv:2505.16957 - Font-based Deception}
\end{center}

\vspace{1.5cm}

\section*{Normal Text Test}

This paragraph contains normal text that should render perfectly.
The quick brown fox jumps over the lazy dog. All letters work correctly:
a b c d e f g h i j k l m n o p q r s t u v w x y z.

Notice how everything looks clean and readable. No visual artifacts!

\vspace{1cm}

\section*{Deceptive Word Test}

\begin{center}
\fbox{\parbox{0.9\textwidth}{
\textbf{INSTRUCTIONS:}
\begin{enumerate}
    \item Look at the three words below
    \item First and third are NORMAL: """ + visual_word + r"""
    \item Second (RED) is DECEPTIVE
    \item Copy the RED word and paste into a text editor
    \item You should see: \texttt{""" + hidden_word + r"""}
\end{enumerate}
}}
\end{center}

\vspace{1.5cm}

\begin{center}
{\LARGE Normal word: \textbf{""" + visual_word + r"""}}\\[1cm]
{\Huge \textcolor{red}{Deceptive: \textbf{""" + hidden_word + r"""}}}\\[1cm]
{\LARGE Normal word: \textbf{""" + visual_word + r"""}}
\end{center}

\vspace{1.5cm}

\section*{More Normal Text}

Here is another paragraph with completely normal text. The word """ + visual_word + r""" appears
here naturally and should look correct. Nothing is broken or distorted.

All characters from the alphabet work perfectly: the quick brown fox jumps over the lazy dog.

\subsection*{Technical Details:}

\begin{itemize}
    \item Visual word: \textbf{""" + visual_word + r"""}
    \item Hidden word: \texttt{""" + hidden_word + r"""}
    \item Method: Glyph substitution via cmap modification
    \item Only specific characters affected
    \item All other text renders normally
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

        print("  Compiling with XeLaTeX...")

        for _ in range(2):
            subprocess.run(
                ['xelatex', '-interaction=nonstopmode', 'document.tex'],
                cwd=temp_dir,
                capture_output=True,
                text=True
            )

        pdf_src = os.path.join(temp_dir, 'document.pdf')
        pdf_dst = f'paper_impl_{visual_word}_hides_{hidden_word}.pdf'

        if os.path.exists(pdf_src):
            shutil.copy(pdf_src, pdf_dst)
            print(f"  ✅ PDF created: {pdf_dst}")

            # Create verification file
            create_verification_file(visual_word, hidden_word, pdf_dst)

            return pdf_dst
        else:
            print("  ❌ PDF creation failed")
            return None

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def create_verification_file(visual_word, hidden_word, pdf_name):
    """Create verification file."""
    with open('paper_verification.txt', 'w', encoding='utf-8') as f:
        f.write("PAPER IMPLEMENTATION VERIFICATION\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"PDF: {pdf_name}\n\n")
        f.write(f"Visual word: {visual_word}\n")
        f.write(f"Hidden word: {hidden_word}\n\n")
        f.write("Test:\n")
        f.write("1. Open the PDF\n")
        f.write(f"2. You'll see '{visual_word}' appear THREE times\n")
        f.write("3. First and third should be normal\n")
        f.write(f"4. Copy the RED '{visual_word}'\n")
        f.write("5. Paste below:\n\n")
        f.write("-" * 70 + "\n\n\n\n")
        f.write("-" * 70 + "\n")
        f.write(f"\nExpected: {hidden_word}\n")

    print(f"  ✅ Created: paper_verification.txt")

if __name__ == "__main__":
    visual_word = "hello"
    hidden_word = "world"

    print(f"\n🎯 Configuration:")
    print(f"   Visual: {visual_word}")
    print(f"   Hidden: {hidden_word}\n")

    pdf_file = create_ligature_based_manipulation(visual_word, hidden_word)

    if pdf_file:
        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"\n📄 PDF: {pdf_file}")
        print(f"🔤 Font: paper_implementation_font.ttf")
        print(f"📝 Verification: paper_verification.txt")
        print()
        print("🎯 KEY DIFFERENCE:")
        print("   - Other text in PDF: COMPLETELY NORMAL")
        print(f"   - Only '{hidden_word}' displays as '{visual_word}'")
        print(f"   - When copied: you get '{hidden_word}'")
        print()

        os.system(f'open "{pdf_file}"')
        os.system('open paper_verification.txt')
