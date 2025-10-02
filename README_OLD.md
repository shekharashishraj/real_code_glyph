# Font Manipulation Tool

Implementation of the PDF font manipulation strategy described in **arXiv:2505.16957** - "Invisible Prompts, Visible Threats: Malicious Font Injection in External Resources for Large Language Models".

## Overview

This tool implements a font manipulation technique that allows characters to visually appear as one glyph while having different Unicode values. The technique works by modifying TrueType font glyph mappings using the formula:

```
GlyphIndex = idDelta + Code
```

By strategically modifying `idDelta` values, characters can be made to appear visually identical while containing different Unicode content.

## 🚨 Important Disclaimer

This implementation is for **defensive security research and educational purposes only**. It should be used to:
- Understand font-based attack vectors
- Develop detection mechanisms
- Create defensive security tools
- Conduct authorized security research

**Do NOT use this tool for malicious purposes.**

## Features

### Core Functionality
- **Font Loading**: Support for TrueType (.ttf) fonts
- **Glyph Mapping Modification**: Precise idDelta manipulation
- **Word-level Mappings**: Map entire words to different Unicode sequences
- **Binary Font Manipulation**: Low-level font binary modification
- **PDF Integration**: Generate PDFs with manipulated fonts

### GUI Interface
- **Interactive Word Selection**: Click-to-select words from text
- **Visual Preview**: See the difference between original and modified characters
- **Mapping Management**: Add, edit, and remove character mappings
- **Real-time Preview**: Live preview of font manipulation effects

### API Endpoints
- Font uploading and processing
- Text extraction from PDFs
- Font manipulation and generation
- Preview generation for mappings

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (React)                  │
│  ┌─────────────────┐  ┌─────────────────────────────┐│
│  │ Word Selection  │  │    Mapping Preview          ││
│  │ Interface       │  │    Component                ││
│  └─────────────────┘  └─────────────────────────────┘│
└─────────────────────────────────────────────────────┘
                           │
                    API (Flask/Python)
                           │
┌─────────────────────────────────────────────────────┐
│                Backend Components                   │
│  ┌─────────────────┐  ┌─────────────────────────────┐│
│  │ Font            │  │    Enhanced Font             ││
│  │ Manipulator     │  │    Manipulator               ││
│  └─────────────────┘  └─────────────────────────────┘│
│  ┌─────────────────┐  ┌─────────────────────────────┐│
│  │ Binary Font     │  │    PDF Integration           ││
│  │ Manipulator     │  │    Module                    ││
│  └─────────────────┘  └─────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher (for frontend)
- A TrueType font file (.ttf) for testing

### Backend Setup

1. Clone or download the files:
```bash
cd real_code_glyph
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Frontend Setup (Optional)

If you want to run the React GUI:

1. Navigate to the frontend directory and install dependencies:
```bash
npm install react react-dom
npm install --save-dev @babel/core @babel/preset-react
```

2. Set up the build system (webpack, create-react-app, etc.)

## Usage

### 1. Basic Font Manipulation

```python
from font_manipulator import WordMappingManager

# Initialize the manager
manager = WordMappingManager()

# Load a font
manager.load_font('path/to/your/font.ttf')

# Create a word mapping (visually "hello" but Unicode "world")
manager.create_word_mapping("hello", "world")

# Generate modified font
manager.generate_font_with_mappings('modified_font.ttf')
```

### 2. PDF Integration

```python
from pdf_font_integration import PDFFontIntegrator

# Initialize integrator
integrator = PDFFontIntegrator()

# Load base font
integrator.load_base_font('base_font.ttf')

# Create mappings
mappings = [
    {'original': 'hello', 'replacement': 'world'},
    {'original': 'secret', 'replacement': 'public'}
]
integrator.create_word_mappings(mappings)

# Create a demonstration PDF
integrator.create_comparison_pdf(
    "This is a hello secret message",
    "demo_output.pdf",
    show_comparison=True
)
```

### 3. API Server

```bash
# Start the API server
python font_manipulation_api.py
```

Available endpoints:
- `POST /api/load-font` - Upload and load a font
- `POST /api/extract-text` - Extract text from PDF
- `POST /api/preview-mappings` - Preview character mappings
- `POST /api/generate-modified-font` - Generate modified font

### 4. GUI Interface

Open the React frontend in your browser and:

1. **Load a Font**: Upload a TTF font file
2. **Select Text**: Upload a PDF or manually enter text
3. **Create Mappings**: Specify original and replacement words
4. **Preview**: See the visual vs Unicode differences
5. **Generate**: Download the modified font

## Technical Details

### Font Manipulation Algorithm

The core algorithm follows the paper's methodology:

1. **Character Isolation**: Isolate target characters in separate font segments
2. **idDelta Calculation**: Calculate new idDelta values using:
   ```
   New idDelta = target_glyph_id - character_code
   ```
3. **Segment Modification**: Update font's cmap table with new mappings
4. **Font Generation**: Create new font file with modified mappings

### Supported Font Formats
- TrueType (.ttf)
- Limited OpenType (.otf) support

### Cmap Table Formats
- Format 4 (Unicode BMP) - Primary support
- Format 12 (Unicode full range) - Basic support

## Testing

Run the comprehensive test suite:

```bash
python test_font_manipulation.py
```

The test suite includes:
- Unit tests for all components
- Integration tests for complete workflows
- Error handling validation
- Unicode preservation tests

## File Structure

```
real_code_glyph/
├── font_manipulator.py              # Core font manipulation engine
├── enhanced_font_manipulator.py     # Enhanced manipulation with idDelta
├── binary_font_manipulator.py       # Low-level binary manipulation
├── pdf_font_integration.py          # PDF integration module
├── font_manipulation_api.py         # REST API server
├── font_manipulation_gui.js         # React GUI component
├── FontManipulationGUI.css          # GUI styles
├── preview_component.js             # Preview functionality
├── PreviewComponent.css             # Preview styles
├── test_font_manipulation.py        # Test suite
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Security Considerations

### Defensive Use Cases
- **Detection Systems**: Build tools to detect font-based attacks
- **Security Analysis**: Analyze documents for hidden content
- **Research**: Understand attack vectors for better defense

### Potential Risks
- **Content Deception**: Text may appear different from its Unicode content
- **Copy-Paste Attacks**: Clipboard content differs from visual appearance
- **LLM Manipulation**: Language models may process different text than users see

### Mitigation Strategies
- **Font Validation**: Verify font integrity before use
- **Unicode Analysis**: Check actual Unicode content vs visual appearance
- **Consistent Rendering**: Use trusted fonts for security-critical applications

## Contributing

1. Ensure all defensive security guidelines are followed
2. Add comprehensive tests for new functionality
3. Update documentation for any API changes
4. Follow Python PEP 8 and JavaScript ES6 standards

## Research Citation

This implementation is based on research from:

```
@article{xiong2025invisible,
  title={Invisible Prompts, Visible Threats: Malicious Font Injection in External Resources for Large Language Models},
  author={Xiong, Junjie and Zhu, Chengcheng and Lin, Shengchao and Zhang, Cheng and Zhang, Yizheng and Liu, Yiwen and Li, Lei},
  journal={arXiv preprint arXiv:2505.16957},
  year={2025}
}
```

## License

This project is intended for educational and defensive security research purposes. Use responsibly and in accordance with applicable laws and regulations.

## Contact

For questions about defensive security applications or research collaboration, please refer to the original paper's authors or create an issue in the repository.