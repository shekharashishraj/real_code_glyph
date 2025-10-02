#!/usr/bin/env python3
"""
TRUE COPY MANIPULATION - Copies exactly what you specify
Maps hidden_word characters to display as visual_word characters
When you copy, you get the actual hidden_word characters!
"""

import os
import shutil
import tempfile
from fontTools.ttLib import TTFont
import subprocess

def create_true_copy_manipulation(visual_word, hidden_word):
    """
    Create font where typing hidden_word displays as visual_word.
    When copied, you get the actual hidden_word characters.

    Example:
        visual_word = "hello"
        hidden_word = "world"

        PDF contains: w o r l d (actual characters)
        PDF displays: h e l l o (what you see)
        Copy gives: world (actual characters!)
    """
    print("=" * 70)
    print("  TRUE COPY MANIPULATION")
    print(f"  Type: {hidden_word}")
    print(f"  See:  {visual_word}")
    print(f"  Copy: {hidden_word}")
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

    print("\n📝 Creating glyph mappings:")
    print(f"   Strategy: Map '{hidden_word}' chars → '{visual_word}' glyphs")
    print()

    # For each character position:
    # Map hidden_char to display visual_char's glyph
    for hidden_char, visual_char in zip(hidden_word, visual_word):
        hidden_code = ord(hidden_char)
        visual_code = ord(visual_char)

        # Get the glyph for the visual character
        if visual_code in unicode_cmap.cmap:
            target_glyph = unicode_cmap.cmap[visual_code]

            # Map hidden character to this glyph
            unicode_cmap.cmap[hidden_code] = target_glyph

            print(f"  '{hidden_char}' (U+{hidden_code:04X}) → displays as '{visual_char}' glyph")

    # Save modified font
    output_font = 'true_copy_font.ttf'
    font.save(output_font)
    print(f"\n✅ Saved font: {output_font}")

    print(f"\n📝 String for PDF:")
    print(f"   Actual text: {hidden_word}")
    print(f"   Will display: {visual_word}")
    print(f"   Will copy: {hidden_word}")

    # Create LaTeX PDF
    print("\n📄 Creating PDF with LaTeX...")

    temp_dir = tempfile.mkdtemp()
    try:
        shutil.copy(output_font, os.path.join(temp_dir, 'true_copy_font.ttf'))

        # Build mapping table
        mapping_table = ""
        for hidden_char, visual_char in zip(hidden_word, visual_word):
            mapping_table += f"{hidden_char} & {visual_char} & U+{ord(hidden_char):04X} \\\\\\n"

        tex_content = r"""\documentclass[12pt]{article}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage[margin=1in]{geometry}

\setmainfont{true_copy_font}[
    Path = """ + temp_dir + r"""/,
    Extension = .ttf
]

\begin{document}

\begin{center}
{\Huge \textbf{True Copy Manipulation}}\\[0.5cm]
{\large Type one word, see another, copy the original}
\end{center}

\vspace{2cm}

\section*{Your Custom Settings}

\begin{center}
\fbox{\parbox{0.9\textwidth}{
\textbf{CONFIGURATION:}
\begin{itemize}
    \item Actual text in PDF: \texttt{""" + hidden_word + r"""}
    \item Displays as: \textbf{""" + visual_word + r"""}
    \item Copies as: \texttt{""" + hidden_word + r"""}
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
    \item You should see: \texttt{""" + hidden_word + r"""}
\end{enumerate}

\vspace{2cm}

\begin{center}
{\LARGE Normal """ + visual_word + r""": \textbf{""" + visual_word + r"""}}\\[1cm]
{\Huge \textcolor{red}{Manipulated: \textbf{""" + hidden_word + r"""}}}\\[1cm]
{\LARGE Normal """ + visual_word + r""": \textbf{""" + visual_word + r"""}}
\end{center}

\vspace{2cm}

\subsection*{Character Mapping:}

\begin{center}
\begin{tabular}{lll}
\textbf{Actual Char} & \textbf{Displays As} & \textbf{Unicode} \\
\hline
""" + mapping_table + r"""
\end{tabular}
\end{center}

\vspace{1cm}

\subsection*{How It Works:}

\begin{itemize}
    \item The PDF literally contains: """ + hidden_word + r"""
    \item The font makes it display as: """ + visual_word + r"""
    \item When you copy-paste, you get: """ + hidden_word + r"""
    \item This is TRUE font manipulation!
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
            result = subprocess.run(
                ['xelatex', '-interaction=nonstopmode', 'document.tex'],
                cwd=temp_dir,
                capture_output=True,
                text=True
            )

        pdf_src = os.path.join(temp_dir, 'document.pdf')
        pdf_dst = f'true_copy_{visual_word}_hides_{hidden_word}.pdf'

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
    """Create a text file for manual verification."""
    with open('true_copy_verification.txt', 'w', encoding='utf-8') as f:
        f.write("TRUE COPY MANIPULATION VERIFICATION\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"PDF File: {pdf_name}\n\n")
        f.write(f"What you SEE in PDF:  {visual_word}\n")
        f.write(f"What you COPY:        {hidden_word}\n\n")
        f.write("Expected Unicode values when copying:\n")
        for i, char in enumerate(hidden_word):
            f.write(f"  Position {i}: '{char}' = U+{ord(char):04X}\n")
        f.write("\n")
        f.write("PASTE TEST:\n")
        f.write("-" * 70 + "\n")
        f.write("Copy the RED word from the PDF and paste below:\n\n\n\n")
        f.write("-" * 70 + "\n")
        f.write(f"\nExpected result: {hidden_word}\n")
        f.write("This proves the actual text is different from visual appearance!\n")

    print(f"  ✅ Created verification file: true_copy_verification.txt")

if __name__ == "__main__":
    # CUSTOMIZE THESE:
    visual_word = "hello"   # What it LOOKS like
    hidden_word = "world"   # What you WANT to copy

    print("\n🎯 CUSTOMIZATION:")
    print(f"   Visual: {visual_word}")
    print(f"   Hidden: {hidden_word}")
    print()
    print("   Both words must be same length!")
    print(f"   PDF will contain: {hidden_word}")
    print(f"   PDF will display: {visual_word}")
    print(f"   Copy will give: {hidden_word}")
    print()

    pdf_file = create_true_copy_manipulation(visual_word, hidden_word)

    if pdf_file:
        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"\n📄 PDF: {pdf_file}")
        print(f"🔤 Font: true_copy_font.ttf")
        print(f"📝 Verification: true_copy_verification.txt")
        print()
        print("🎯 TEST NOW:")
        print(f"  1. Open the PDF")
        print(f"  2. You'll see '{visual_word}' in three places")
        print(f"  3. Copy the RED '{visual_word}' (middle one)")
        print(f"  4. Paste into true_copy_verification.txt")
        print(f"  5. Result: You should see '{hidden_word}'!")
        print()
        print("⚠️  NOTE: This affects ALL instances of these characters")
        print(f"   Every '{hidden_word[0]}' will look like '{visual_word[0]}'")
        print(f"   Every '{hidden_word[1]}' will look like '{visual_word[1]}'")
        print("   etc...")
        print()

        os.system(f'open "{pdf_file}"')
        os.system('open true_copy_verification.txt')
