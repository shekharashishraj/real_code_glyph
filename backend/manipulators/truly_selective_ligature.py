"""
Word-Level Ligature Manipulation
Creates a custom font where the entire hidden word becomes a ligature displaying the visual word
"""

import os
import shutil
import tempfile
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeatures
import subprocess
from pathlib import Path
import uuid
from datetime import datetime
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.varLib import instancer

class LigatureManipulator:
    def __init__(self, fonts_folder, output_folder):
        self.fonts_folder = Path(fonts_folder)
        self.output_folder = Path(output_folder)
        self.base_font = self.fonts_folder / 'Roboto.ttf'

    def create_manipulation(self, visual_word, hidden_word):
        """
        Create ligature-based manipulation.
        The hidden_word text will be replaced by a ligature that looks like visual_word.
        """
        try:
            if not self.base_font.exists():
                return {
                    'success': False,
                    'error': f'Base font not found: {self.base_font}'
                }

            # Generate unique ID
            job_id = str(uuid.uuid4())[:8]

            # Prepare logging
            logs_root = self.output_folder / 'logs'
            logs_root.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_dir = logs_root / f'{timestamp}_{job_id}'
            log_dir.mkdir(exist_ok=True)
            log_entries = [
                f"Job ID: {job_id}",
                f"Timestamp: {timestamp}",
                f"Visual word: {visual_word}",
                f"Hidden word: {hidden_word}",
                f"Strategy: Word-level ligature substitution"
            ]

            # Create fonts
            normal_font_path = self.output_folder / f'{job_id}_normal.ttf'
            deceptive_font_path = self.output_folder / f'{job_id}_deceptive_lig.ttf'

            # Load and instantiate base font if variable
            base_font_tt = TTFont(str(self.base_font))
            if 'fvar' in base_font_tt:
                axis_defaults = {axis.axisTag: axis.defaultValue for axis in base_font_tt['fvar'].axes}
                log_entries.append(f"Instantiating variable font with: {axis_defaults}")
                base_font_tt = instancer.instantiateVariableFont(base_font_tt, axis_defaults, inplace=False)

            # Save normal font
            base_font_tt.save(str(normal_font_path))
            log_entries.append(f"Saved normal font: {normal_font_path.name}")

            # Create deceptive font with ligature
            font = TTFont(str(normal_font_path))
            source_font = TTFont(str(normal_font_path))  # Pristine copy

            glyf_table = font.get('glyf')
            hmtx_table = font.get('hmtx')
            cmap = font.getBestCmap()
            source_glyph_set = source_font.getGlyphSet()

            if not cmap:
                return {'success': False, 'error': 'No cmap in font'}

            # Validate all characters exist
            for char in set(visual_word + hidden_word):
                if ord(char) not in cmap:
                    return {'success': False, 'error': f"Character '{char}' not in font"}

            # Create ligature glyph name
            lig_name = f"lig_{hidden_word.replace(' ', '_')}"

            # Combine visual glyphs into one ligature glyph
            # For simplicity, concatenate the glyphs horizontally
            log_entries.append(f"Creating ligature glyph '{lig_name}' for '{hidden_word}' → '{visual_word}'")

            # Build the ligature by combining visual character glyphs
            from fontTools.pens.boundsPen import BoundsPen
            from fontTools.pens.transformPen import TransformPen

            # Create a new composite glyph
            pen = TTGlyphPen(source_glyph_set)
            x_offset = 0
            total_width = 0

            for visual_char in visual_word:
                visual_glyph_name = cmap.get(ord(visual_char))
                if not visual_glyph_name:
                    continue

                # Get the glyph and its width
                visual_glyph = source_glyph_set[visual_glyph_name]
                width = source_font['hmtx'].metrics[visual_glyph_name][0]

                # Draw the glyph with horizontal offset
                transform_pen = TransformPen(pen, (1, 0, 0, 1, x_offset, 0))
                visual_glyph.draw(transform_pen)

                x_offset += width
                total_width += width

            new_glyph = pen.glyph()

            # Add the ligature glyph to the font
            glyf_table[lig_name] = new_glyph
            hmtx_table.metrics[lig_name] = (total_width, 0)  # Total width, left side bearing

            log_entries.append(f"Ligature glyph width: {total_width}")

            # Create OpenType ligature feature
            # The liga feature will substitute hidden_word characters with the ligature
            hidden_glyphs = [cmap.get(ord(c)) for c in hidden_word if ord(c) in cmap]

            fea_code = f"""languagesystem DFLT dflt;
languagesystem latn dflt;

feature liga {{
    sub {' '.join(hidden_glyphs)} by {lig_name};
}} liga;
"""

            log_entries.append(f"OpenType feature code:")
            log_entries.append(fea_code)

            # Write feature code to a temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.fea', delete=False) as fea_file:
                fea_file.write(fea_code)
                fea_path = fea_file.name

            # Add the feature to the font
            try:
                addOpenTypeFeatures(font, fea_path)
                log_entries.append("Successfully added liga feature")
                os.unlink(fea_path)  # Clean up temp file
            except Exception as e:
                log_entries.append(f"Feature addition failed: {e}")
                if os.path.exists(fea_path):
                    os.unlink(fea_path)
                return {'success': False, 'error': f'Feature addition failed: {e}'}

            # Save deceptive font
            font.save(str(deceptive_font_path))
            log_entries.append(f"Saved deceptive font: {deceptive_font_path.name}")

            # Create PDF
            pdf_file = self._create_pdf(
                visual_word,
                hidden_word,
                normal_font_path,
                deceptive_font_path,
                job_id
            )

            # Save log
            log_file = log_dir / 'steps.log'
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_entries) + '\n')

            if pdf_file:
                return {
                    'success': True,
                    'pdf_file': pdf_file,
                    'font_file': deceptive_font_path.name,
                    'log_dir': str(log_dir.relative_to(self.output_folder)),
                    'message': 'Ligature manipulation successful'
                }
            else:
                return {'success': False, 'error': 'PDF creation failed'}

        except Exception as e:
            import traceback
            return {
                'success': False,
                'error': f'{str(e)}\n{traceback.format_exc()}'
            }

    def _create_pdf(self, visual_word, hidden_word, normal_font, deceptive_font, job_id):
        """Create PDF demonstrating ligature"""
        temp_dir = tempfile.mkdtemp()
        try:
            shutil.copy(normal_font, os.path.join(temp_dir, 'normal.ttf'))
            shutil.copy(deceptive_font, os.path.join(temp_dir, 'deceptive.ttf'))

            tex_content = r"""\documentclass[12pt]{article}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage[margin=1in]{geometry}

\setmainfont{normal}[
    Path = """ + temp_dir + r"""/,
    Extension = .ttf
]

\newfontfamily\deceptivefont{deceptive}[
    Path = """ + temp_dir + r"""/,
    Extension = .ttf,
    Ligatures=Common
]

\begin{document}

\begin{center}
{\Huge \textbf{Font Ligature Manipulation}}\\[0.3cm]
{\large Word-Level Substitution}
\end{center}

\vspace{1.5cm}

\section*{Normal Text}

This paragraph uses normal font. The word """ + visual_word + r""" appears here naturally.
All text renders correctly.

\vspace{1cm}

\section*{Ligature Test}

\begin{center}
\fbox{\parbox{0.9\textwidth}{
\textbf{INSTRUCTIONS:}
\begin{enumerate}
    \item First line: NORMAL font
    \item Second line (RED): DECEPTIVE font with ligature
    \item Third line: NORMAL font
    \item Copy the RED word and paste to see the hidden text
\end{enumerate}
}}
\end{center}

\vspace{1.5cm}

\begin{center}
{\LARGE Normal: \textbf{""" + visual_word + r"""}}\\[1cm]
{\Huge \textcolor{red}{Deceptive: {\deceptivefont\textbf{""" + hidden_word + r"""}}}}\\[1cm]
{\LARGE Normal: \textbf{""" + visual_word + r"""}}
\end{center}

\vspace{1.5cm}

\section*{Technical Details}

\begin{itemize}
    \item Visual: \textbf{""" + visual_word + r"""}
    \item Hidden: \texttt{""" + hidden_word + r"""}
    \item Mode: Word-Level Ligature
    \item The deceptive font replaces the entire word with a single ligature glyph
\end{itemize}

\begin{center}
\small{\textit{arXiv:2505.16957 - Font Manipulation Research}}
\end{center}

\end{document}
"""

            tex_file = os.path.join(temp_dir, 'document.tex')
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(tex_content)

            # Compile with LuaLaTeX
            for _ in range(2):
                subprocess.run(
                    ['lualatex', '-interaction=nonstopmode', 'document.tex'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )

            pdf_src = os.path.join(temp_dir, 'document.pdf')
            pdf_dst = self.output_folder / f'{job_id}.pdf'

            if os.path.exists(pdf_src):
                shutil.copy(pdf_src, pdf_dst)
                # Copy tex for debugging
                tex_dst = self.output_folder / f'{job_id}.tex'
                shutil.copy(tex_file, tex_dst)
                return pdf_dst.name
            else:
                return None

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
