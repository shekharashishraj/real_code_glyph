#!/usr/bin/env python3
"""
SELECTIVE Font Manipulation - Only specific words are manipulated
Uses Private Use Area (PUA) Unicode characters to avoid affecting other text
"""

import os
import shutil
import tempfile
from fontTools.ttLib import TTFont
import subprocess

def create_selective_manipulation():
    """
    Create font where:
    - Normal text remains unchanged
    - Special PUA characters display as 'hello' but encode as 'world'
    """
    print("=" * 70)
    print("  SELECTIVE FONT MANIPULATION")
    print("  Only specific word instance is manipulated")
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

    # Use Private Use Area (PUA) Unicode: U+E000 to U+F8FF
    # These are specifically reserved for custom use and won't affect normal text
    pua_start = 0xE000

    # Map PUA characters to display as 'hello' letters
    word_to_hide = "world"
    word_to_show = "hello"

    print("\n📝 Creating PUA mappings:")
    print(f"   Hidden word: {word_to_hide}")
    print(f"   Visual word: {word_to_show}")
    print()

    pua_mappings = {}
    for i, (hide_char, show_char) in enumerate(zip(word_to_hide, word_to_show)):
        pua_code = pua_start + i

        # Get the glyph for the character we want to display
        show_code = ord(show_char)
        if show_code in unicode_cmap.cmap:
            target_glyph = unicode_cmap.cmap[show_code]

            # Map PUA character to display this glyph
            unicode_cmap.cmap[pua_code] = target_glyph
            pua_mappings[hide_char] = pua_code

            print(f"  PUA U+{pua_code:04X} → displays glyph of '{show_char}' (hides '{hide_char}')")

    # Save modified font
    output_font = 'selective_font.ttf'
    font.save(output_font)
    print(f"\n✅ Saved font: {output_font}")

    # Create the deceptive text using PUA characters
    deceptive_text = ""
    for char in word_to_hide:
        if char in pua_mappings:
            # Use PUA character instead
            deceptive_text += chr(pua_mappings[char])
        else:
            deceptive_text += char

    print(f"\n📝 Deceptive text created:")
    print(f"   Visual: {word_to_show}")
    print(f"   Actual Unicode: ", end="")
    for char in deceptive_text:
        print(f"U+{ord(char):04X} ", end="")
    print()

    # Create LaTeX PDF
    print("\n📄 Creating PDF with LaTeX...")

    temp_dir = tempfile.mkdtemp()
    try:
        # Copy font
        shutil.copy(output_font, os.path.join(temp_dir, 'selective_font.ttf'))

        # Create LaTeX with proper Unicode handling
        tex_content = r"""\documentclass[12pt]{article}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage[margin=1in]{geometry}

\setmainfont{selective_font}[
    Path = """ + temp_dir + r"""/,
    Extension = .ttf
]

\begin{document}

\begin{center}
{\Huge \textbf{Selective Font Manipulation}}\\[0.3cm]
{\large Only specific word is deceptive, all other text is normal}
\end{center}

\vspace{1.5cm}

\section*{Normal Text Test}

All regular text works perfectly:

\begin{itemize}
    \item This is hello world (normal text)
    \item The word hello appears correctly
    \item Nothing is broken or distorted
    \item All letters work: a b c d e f g h i j k l m n o p q r s t u v w x y z
\end{itemize}

\vspace{1cm}

\section*{Deceptive Word Test}

Now look at this specially crafted word below. It uses Private Use Area (PUA) Unicode characters that are invisible to you but different in the digital content.

\vspace{0.5cm}

\begin{center}
\fbox{\parbox{0.9\textwidth}{
\textbf{INSTRUCTIONS:}
\begin{enumerate}
    \item Look at the RED word below - note what you SEE
    \item Select and COPY only the RED word
    \item Paste into TextEdit or any editor
    \item Compare - you'll see DIFFERENT characters!
\end{enumerate}
}}
\end{center}

\vspace{1cm}

\begin{center}
Regular hello: \textbf{hello}\\[0.5cm]
{\Huge Manipulated word: \textcolor{red}{\textbf{""" + deceptive_text + r"""}}}\\[0.5cm]
Another regular hello: \textbf{hello}
\end{center}

\vspace{1cm}

\subsection*{What's Different?}

\begin{itemize}
    \item \textbf{First "hello":} Normal Unicode (h-e-l-l-o)
    \item \textbf{RED word:} Private Use Area Unicode that LOOKS like "hello"
    \item \textbf{Third "hello":} Normal Unicode again
\end{itemize}

When you copy the RED word, you're actually copying PUA characters (U+E000, U+E001, U+E002, U+E003, U+E004) which your text editor will either:
\begin{itemize}
    \item Display as boxes/question marks (most common)
    \item Show the original Unicode values
    \item Display unpredictably
\end{itemize}

This proves the RED word has DIFFERENT Unicode content despite looking identical!

\vspace{1cm}

\subsection*{Why This Approach is Better:}

\begin{enumerate}
    \item Only affects specific instances we choose
    \item All other text remains perfectly normal
    \item No collateral damage to document formatting
    \item More precise control over deception
\end{enumerate}

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

        # Compile twice
        for _ in range(2):
            subprocess.run(
                ['xelatex', '-interaction=nonstopmode', 'document.tex'],
                cwd=temp_dir,
                capture_output=True,
                text=True
            )

        # Copy PDF
        pdf_src = os.path.join(temp_dir, 'document.pdf')
        pdf_dst = 'selective_manipulation.pdf'

        if os.path.exists(pdf_src):
            shutil.copy(pdf_src, pdf_dst)
            print(f"  ✅ PDF created: {pdf_dst}")

            # Also create a simple test file
            create_test_file(deceptive_text, word_to_show)

            return pdf_dst
        else:
            print("  ❌ PDF creation failed")
            return None

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def create_test_file(deceptive_text, visual_text):
    """Create a simple text file showing the difference."""
    with open('deceptive_comparison.txt', 'w', encoding='utf-8') as f:
        f.write("FONT MANIPULATION TEST\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"What you SEE in PDF: {visual_text}\n")
        f.write(f"What you COPY (PUA): {deceptive_text}\n\n")
        f.write("Unicode values:\n")
        f.write(f"Visual '{visual_text}': ")
        for char in visual_text:
            f.write(f"U+{ord(char):04X} ")
        f.write(f"\nActual PUA: ")
        for char in deceptive_text:
            f.write(f"U+{ord(char):04X} ")
        f.write("\n\n")
        f.write("When you copy the RED word from the PDF and paste here:\n")
        f.write("-" * 50 + "\n")
        f.write("(paste below)\n\n\n")

    print(f"  ✅ Created comparison file: deceptive_comparison.txt")

if __name__ == "__main__":
    pdf_file = create_selective_manipulation()

    if pdf_file:
        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"\n📄 PDF: {pdf_file}")
        print(f"🔤 Font: selective_font.ttf")
        print(f"📝 Test file: deceptive_comparison.txt")
        print()
        print("🎯 VERIFY NOW:")
        print("  1. Open the PDF")
        print("  2. Notice: ALL text looks normal EXCEPT the RED word")
        print("  3. The word 'hello' appears 3 times")
        print("  4. Copy ONLY the RED 'hello' (middle one)")
        print("  5. Paste into deceptive_comparison.txt")
        print("  6. You'll see boxes/garbage (different Unicode!)")
        print()
        print("✨ Key Difference:")
        print("  - First 'hello': Normal (U+0068 U+0065 U+006C U+006C U+006F)")
        print("  - RED 'hello': PUA codes (U+E000 U+E001 U+E002 U+E003 U+E004)")
        print("  - Third 'hello': Normal again")
        print()
        print("Opening PDF...")
        os.system(f'open "{pdf_file}"')
        os.system('open deceptive_comparison.txt')
