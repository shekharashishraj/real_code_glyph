#!/usr/bin/env python3
"""
CUSTOMIZABLE Font Manipulation - You choose what appears vs what copies
Allows full control over visual text and hidden text
"""

import os
import shutil
import tempfile
from fontTools.ttLib import TTFont
import subprocess

def create_custom_manipulation(visual_word, hidden_word):
    """
    Create font manipulation where:
    - User sees: visual_word
    - User copies: hidden_word

    Args:
        visual_word: What the word looks like (e.g., "hello")
        hidden_word: What gets copied (e.g., "world")
    """
    print("=" * 70)
    print("  CUSTOMIZABLE FONT MANIPULATION")
    print(f"  Visual: {visual_word}")
    print(f"  Hidden: {hidden_word}")
    print("=" * 70)
    print()

    if len(visual_word) != len(hidden_word):
        print("❌ ERROR: visual_word and hidden_word must be same length!")
        return False

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

    # Use Private Use Area (PUA) for custom mappings
    # PUA range: U+E000 to U+F8FF (safe, won't affect other text)
    pua_start = 0xE000

    print("\n📝 Creating custom character mappings:")

    # For each position in the word:
    # - Map a PUA character to display as visual_word[i] glyph
    # - Store what character from hidden_word it represents

    pua_string = ""  # The actual string to use in PDF
    mapping_info = []

    for i, (visual_char, hidden_char) in enumerate(zip(visual_word, hidden_word)):
        pua_code = pua_start + i
        visual_code = ord(visual_char)

        # Get the glyph for the visual character
        if visual_code in unicode_cmap.cmap:
            target_glyph = unicode_cmap.cmap[visual_code]

            # Map PUA character to this glyph
            unicode_cmap.cmap[pua_code] = target_glyph

            # Build the PUA string
            pua_string += chr(pua_code)

            mapping_info.append({
                'pua': f"U+{pua_code:04X}",
                'visual': visual_char,
                'hidden': hidden_char
            })

            print(f"  {chr(pua_code)} (U+{pua_code:04X}) → displays '{visual_char}' (represents '{hidden_char}')")

    # Save modified font
    output_font = 'custom_font.ttf'
    font.save(output_font)
    print(f"\n✅ Saved font: {output_font}")

    print(f"\n📝 Deceptive string created:")
    print(f"   Looks like: {visual_word}")
    print(f"   Represents: {hidden_word}")
    print(f"   PUA codes: ", end="")
    for char in pua_string:
        print(f"U+{ord(char):04X} ", end="")
    print()

    # Create LaTeX PDF
    print("\n📄 Creating PDF with LaTeX...")

    temp_dir = tempfile.mkdtemp()
    try:
        shutil.copy(output_font, os.path.join(temp_dir, 'custom_font.ttf'))

        # Create mapping table for PDF
        mapping_table = ""
        for info in mapping_info:
            mapping_table += f"{info['visual']} & {info['hidden']} & {info['pua']} \\\\\n"

        tex_content = r"""\documentclass[12pt]{article}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage[margin=1in]{geometry}

\setmainfont{custom_font}[
    Path = """ + temp_dir + r"""/,
    Extension = .ttf
]

\begin{document}

\begin{center}
{\Huge \textbf{Custom Font Manipulation}}\\[0.5cm]
{\large Control what you see vs what you copy}
\end{center}

\vspace{2cm}

\section*{Your Custom Manipulation}

\begin{center}
\fbox{\parbox{0.9\textwidth}{
\textbf{SETTINGS:}
\begin{itemize}
    \item Visual word: \textbf{""" + visual_word + r"""}
    \item Hidden word: \textbf{""" + hidden_word + r"""}
\end{itemize}
}}
\end{center}

\vspace{1cm}

\subsection*{Test Instructions:}

\begin{enumerate}
    \item Look at the RED word below
    \item It LOOKS like: \textbf{""" + visual_word + r"""}
    \item Copy the RED word
    \item Paste into a text editor
    \item You should see: boxes/garbage (PUA characters)
\end{enumerate}

\vspace{2cm}

\begin{center}
{\LARGE Normal text: \textbf{""" + visual_word + r"""}}\\[1cm]
{\Huge \textcolor{red}{Manipulated: \textbf{""" + pua_string + r"""}}}\\[1cm]
{\LARGE Normal text: \textbf{""" + visual_word + r"""}}
\end{center}

\vspace{2cm}

\subsection*{Character Mapping:}

\begin{center}
\begin{tabular}{lll}
\textbf{Visual} & \textbf{Hidden} & \textbf{PUA Code} \\
\hline
""" + mapping_table + r"""
\end{tabular}
\end{center}

\vspace{1cm}

\subsection*{How It Works:}

\begin{itemize}
    \item The font maps Private Use Area (PUA) Unicode characters
    \item PUA characters display as your chosen visual letters
    \item When copied, they remain as PUA (shown as boxes)
    \item Normal text is completely unaffected
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
        pdf_dst = f'custom_{visual_word}_to_{hidden_word}.pdf'

        if os.path.exists(pdf_src):
            shutil.copy(pdf_src, pdf_dst)
            print(f"  ✅ PDF created: {pdf_dst}")

            # Create verification file
            create_verification_file(visual_word, hidden_word, pua_string, pdf_dst)

            return pdf_dst
        else:
            print("  ❌ PDF creation failed")
            return None

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def create_verification_file(visual_word, hidden_word, pua_string, pdf_name):
    """Create a text file for manual verification."""
    with open('verification.txt', 'w', encoding='utf-8') as f:
        f.write("CUSTOM FONT MANIPULATION VERIFICATION\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"PDF File: {pdf_name}\n\n")
        f.write(f"What you SEE:  {visual_word}\n")
        f.write(f"What you WANT: {hidden_word}\n")
        f.write(f"PUA string:    {pua_string}\n\n")
        f.write("PUA Unicode values:\n")
        for i, char in enumerate(pua_string):
            f.write(f"  Position {i}: U+{ord(char):04X}\n")
        f.write("\n")
        f.write("PASTE TEST:\n")
        f.write("-" * 70 + "\n")
        f.write("Copy the RED word from the PDF and paste below:\n\n\n\n")
        f.write("-" * 70 + "\n")
        f.write("\nNote: PUA characters may appear as boxes (□) or question marks (?)\n")
        f.write("This proves the Unicode is different from the visual appearance!\n")

    print(f"  ✅ Created verification file: verification.txt")

if __name__ == "__main__":
    # CUSTOMIZE THESE:
    visual_word = "hello"   # What it LOOKS like
    hidden_word = "world"   # What you WANT it to copy as (semantically)

    print("\n🎯 CUSTOMIZATION:")
    print(f"   Visual: {visual_word}")
    print(f"   Hidden: {hidden_word}")
    print()
    print("   Note: Both words must be same length!")
    print("   The hidden word is conceptually what it represents,")
    print("   but due to PUA limitations, it will copy as boxes/PUA chars.")
    print()

    pdf_file = create_custom_manipulation(visual_word, hidden_word)

    if pdf_file:
        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"\n📄 PDF: {pdf_file}")
        print(f"🔤 Font: custom_font.ttf")
        print(f"📝 Verification: verification.txt")
        print()
        print("🎯 TEST NOW:")
        print(f"  1. Open the PDF")
        print(f"  2. You'll see '{visual_word}' appear 3 times")
        print(f"  3. Copy the RED '{visual_word}' (middle one)")
        print(f"  4. Paste into verification.txt")
        print(f"  5. Result: PUA characters (boxes/garbage)")
        print()
        print("💡 To change words, edit the script:")
        print("   visual_word = 'hello'  # What it looks like")
        print("   hidden_word = 'world'  # What it represents")
        print()

        os.system(f'open "{pdf_file}"')
        os.system('open verification.txt')
