#!/usr/bin/env python3
"""
TRULY SELECTIVE MANIPULATION
Only affects ONE specific word instance, all other text completely normal
Uses MIXED fonts in PDF - manipulated font only for deceptive word
"""

import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.varLib import instancer
import subprocess

def create_two_fonts(visual_word, hidden_word, base_font='Roboto.ttf'):
    """
    Create TWO fonts:
    1. Normal font - unchanged
    2. Deceptive font - maps hidden_word chars to visual_word glyphs

    Then use LaTeX to apply deceptive font ONLY to specific word instance
    """
    print("=" * 70)
    print("  TRULY SELECTIVE MANIPULATION")
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

    # Prepare logging
    logs_root = Path('logs')
    logs_root.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = logs_root / f'truly_selective_{timestamp}'
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / 'steps.log'

    def log(message):
        print(message)
        with open(log_path, 'a', encoding='utf-8') as handle:
            handle.write(message + '\n')

    log(f"Visual word: {visual_word} | Hidden word: {hidden_word}")
    log(f"Base font: {base_font}")

    # Load base font and freeze any variable axes so glyph cloning works reliably
    log(f"\n✅ Creating deceptive font from: {base_font}")
    base_font_tt = TTFont(base_font)
    if 'fvar' in base_font_tt:
        axis_defaults = {axis.axisTag: axis.defaultValue for axis in base_font_tt['fvar'].axes}
        log(f"Detected variable axes; instantiating with defaults: {axis_defaults}")
        base_font_tt = instancer.instantiateVariableFont(base_font_tt, axis_defaults, inplace=False)

    # Font 1: Save static normal font
    normal_font_path = 'normal_font.ttf'
    base_font_tt.save(normal_font_path)
    log(f"✅ Created normal font: {normal_font_path}")

    # Font 2: Clone glyphs into deceptive font
    font = TTFont(normal_font_path)
    source_font = TTFont(normal_font_path)

    cmap = font.getBestCmap()
    if not cmap:
        log("❌ No cmap table found")
        return False

    missing_chars = [c for c in set(visual_word + hidden_word) if ord(c) not in cmap]
    if missing_chars:
        log(f"❌ Characters missing from base font: {', '.join(sorted(missing_chars))}")
        return False

    glyf_table = font.get('glyf')
    hmtx_table = font.get('hmtx')
    if glyf_table is None or hmtx_table is None:
        log("❌ Base font missing glyf/hmtx tables")
        return False

    glyph_set = font.getGlyphSet()
    source_glyph_set = source_font.getGlyphSet()

    log(f"\n📝 Mapping hidden word '{hidden_word}' → '{visual_word}' glyphs:")
    for hidden_char, visual_char in zip(hidden_word, visual_word):
        hidden_glyph = cmap[ord(hidden_char)]
        visual_glyph = cmap[ord(visual_char)]

        if visual_glyph not in glyf_table.glyphs:
            log(f"❌ Glyph '{visual_glyph}' missing in glyf table")
            return False

        pen = TTGlyphPen(source_glyph_set)
        source_glyph_set[visual_glyph].draw(pen)
        new_glyph = pen.glyph()

        visual_tt_glyph = source_font['glyf'][visual_glyph]
        if hasattr(visual_tt_glyph, 'program') and visual_tt_glyph.program:
            new_glyph.program = visual_tt_glyph.program

        glyf_table[hidden_glyph] = new_glyph
        if visual_glyph in source_font['hmtx'].metrics:
            hmtx_table.metrics[hidden_glyph] = source_font['hmtx'].metrics[visual_glyph]

        log(f"  '{hidden_char}' (glyph '{hidden_glyph}') now copies outline from '{visual_char}' (glyph '{visual_glyph}')")

    # Save deceptive font
    deceptive_font_path = 'deceptive_font.ttf'
    font.save(deceptive_font_path)
    log(f"\n✅ Saved deceptive font: {deceptive_font_path}")

    print(f"\n📝 Strategy:")
    print(f"   - Most of PDF uses: {normal_font_path}")
    print(f"   - ONE specific word uses: {deceptive_font_path}")
    print(f"   - That word contains '{hidden_word}' but displays as '{visual_word}'")
    print(f"   - All other text completely normal!")

    return create_mixed_font_pdf(visual_word, hidden_word, normal_font_path, deceptive_font_path)

def create_mixed_font_pdf(visual_word, hidden_word, normal_font, deceptive_font):
    """Create PDF using BOTH fonts selectively."""
    print("\n📄 Creating PDF with mixed fonts...")

    temp_dir = tempfile.mkdtemp()
    try:
        # Copy both fonts to temp directory
        shutil.copy(normal_font, os.path.join(temp_dir, 'normal_font.ttf'))
        shutil.copy(deceptive_font, os.path.join(temp_dir, 'deceptive_font.ttf'))

        # Create LaTeX document with font switching
        tex_content = r"""\documentclass[12pt]{article}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage[margin=1in]{geometry}

% Define normal font (used for most text)
\setmainfont{normal_font}[
    Path = """ + temp_dir + r"""/,
    Extension = .ttf
]

% Define deceptive font (used only for specific word)
\newfontfamily\deceptivefont{deceptive_font}[
    Path = """ + temp_dir + r"""/,
    Extension = .ttf
]

\begin{document}

\begin{center}
{\Huge \textbf{Truly Selective Manipulation}}\\[0.3cm]
{\large Only ONE word is deceptive, ALL other text is normal}
\end{center}

\vspace{1.5cm}

\section*{Normal Text Everywhere}

This entire paragraph uses the normal font. The word """ + visual_word + r""" appears here
and is completely normal. All letters work perfectly: a b c d e f g h i j k l m n o p q r s t u v w x y z.

The quick brown fox jumps over the lazy dog. Everything renders correctly with no artifacts!

\vspace{1cm}

\section*{Deceptive Word Test}

\begin{center}
\fbox{\parbox{0.9\textwidth}{
\textbf{INSTRUCTIONS:}
\begin{enumerate}
    \item Look at the three instances of """ + visual_word + r"""" below
    \item First: NORMAL (using normal font)
    \item Second (RED): DECEPTIVE (using deceptive font)
    \item Third: NORMAL (using normal font again)
    \item Copy the RED word - you'll get: \texttt{""" + hidden_word + r"""}
    \item Copy first or third - you'll get: \texttt{""" + visual_word + r"""}
\end{enumerate}
}}
\end{center}

\vspace{1.5cm}

\begin{center}
% Normal instance
{\LARGE Normal: \textbf{""" + visual_word + r"""}}\\[1cm]

% Deceptive instance (font switch!)
{\Huge \textcolor{red}{Deceptive: {\deceptivefont\textbf{""" + hidden_word + r"""}}}}\\[1cm]

% Normal instance again
{\LARGE Normal: \textbf{""" + visual_word + r"""}}
\end{center}

\vspace{1.5cm}

\section*{More Normal Text}

Here's another paragraph with completely normal text. The word """ + visual_word + r"""
appears here naturally and looks correct. Nothing is broken!

All characters from the English alphabet work perfectly:
a b c d e f g h i j k l m n o p q r s t u v w x y z

And all digits: 0 1 2 3 4 5 6 7 8 9

\subsection*{Technical Details:}

\begin{itemize}
    \item Main font: normal\_font.ttf (unmodified)
    \item Deceptive font: deceptive\_font.ttf (modified mappings)
    \item Visual word: \textbf{""" + visual_word + r"""}
    \item Hidden word: \texttt{""" + hidden_word + r"""}
    \item Only the RED word uses the deceptive font
    \item Everything else: COMPLETELY NORMAL
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

        for i in range(2):
            result = subprocess.run(
                ['xelatex', '-interaction=nonstopmode', 'document.tex'],
                cwd=temp_dir,
                capture_output=True,
                text=True
            )
            if result.returncode != 0 and i == 1:
                print(f"  ⚠️  LaTeX warnings (this is normal)")

        pdf_src = os.path.join(temp_dir, 'document.pdf')
        pdf_dst = f'truly_selective_{visual_word}_hides_{hidden_word}.pdf'

        if os.path.exists(pdf_src):
            shutil.copy(pdf_src, pdf_dst)
            print(f"  ✅ PDF created: {pdf_dst}")

            create_verification_file(visual_word, hidden_word, pdf_dst)

            return pdf_dst
        else:
            print("  ❌ PDF creation failed")
            print("  LaTeX output:")
            print(result.stdout[-500:] if result.stdout else "No output")
            return None

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def create_verification_file(visual_word, hidden_word, pdf_name):
    """Create verification file."""
    with open('truly_selective_verification.txt', 'w', encoding='utf-8') as f:
        f.write("TRULY SELECTIVE MANIPULATION VERIFICATION\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"PDF: {pdf_name}\n\n")
        f.write(f"Visual word: {visual_word}\n")
        f.write(f"Hidden word: {hidden_word}\n\n")
        f.write("The RED word should:\n")
        f.write(f"  - Look like: {visual_word}\n")
        f.write(f"  - Copy as: {hidden_word}\n\n")
        f.write("All other text should be COMPLETELY NORMAL!\n\n")
        f.write("Test:\n")
        f.write("-" * 70 + "\n")
        f.write(f"1. Copy the FIRST '{visual_word}' (normal):\n\n\n")
        f.write(f"   Expected: {visual_word}\n\n")
        f.write(f"2. Copy the RED '{visual_word}' (deceptive):\n\n\n")
        f.write(f"   Expected: {hidden_word}\n\n")
        f.write(f"3. Copy the THIRD '{visual_word}' (normal):\n\n\n")
        f.write(f"   Expected: {visual_word}\n")
        f.write("-" * 70 + "\n")

    print(f"  ✅ Created: truly_selective_verification.txt")

if __name__ == "__main__":
    visual_word = "hello"
    hidden_word = "world"

    print(f"\n🎯 Configuration:")
    print(f"   Visual: {visual_word}")
    print(f"   Hidden: {hidden_word}\n")

    pdf_file = create_two_fonts(visual_word, hidden_word)

    if pdf_file:
        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"\n📄 PDF: {pdf_file}")
        print(f"🔤 Normal font: normal_font.ttf")
        print(f"🔤 Deceptive font: deceptive_font.ttf")
        print(f"📝 Verification: truly_selective_verification.txt")
        print()
        print("🎯 KEY FEATURES:")
        print("   ✅ Only ONE specific word instance is deceptive")
        print("   ✅ All other text uses normal font")
        print("   ✅ No corruption or artifacts anywhere")
        print(f"   ✅ Deceptive word contains '{hidden_word}' but looks like '{visual_word}'")
        print()
        print("💡 To customize:")
        print("   Edit lines 267-268 in the script:")
        print("   visual_word = 'your_visual_word'")
        print("   hidden_word = 'your_hidden_word'")
        print()

        os.system(f'open "{pdf_file}"')
        os.system('open truly_selective_verification.txt')
