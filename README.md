# Font Manipulation for Deceptive PDFs

A research implementation of font manipulation techniques for creating deceptive PDFs where text displays differently from what it copies as. Based on arXiv:2505.16957.

## 🎯 Project Overview

This project demonstrates how font manipulation can be used to create PDFs where:
- **Visual Text**: What the user sees on screen
- **Hidden Text**: What gets copied to clipboard or extracted by text tools

**Example**: Display "hello" but copy as "anita"

## 📁 Project Structure

```
real_code_glyph/
├── backend/              # Flask API server
│   ├── app.py           # Main API server
│   ├── manipulators/    # Font manipulation modules
│   │   ├── truly_selective.py          # V1 - Basic
│   │   ├── truly_selective_v3.py       # V3 - OpenType (experimental)
│   │   ├── truly_selective_v4.py       # V4 - Unicode alternates (RECOMMENDED)
│   │   ├── unicode_alternates.json     # 700+ character mappings
│   │   ├── cyrillic.py                 # Cyrillic homoglyphs
│   │   └── pua.py                      # Private Use Area
│   ├── test_v4.py       # Comprehensive test suite
│   └── README.md        # Detailed API documentation
│
├── frontend/            # React UI (Vite + React)
│   ├── src/
│   │   ├── App.jsx      # Main application
│   │   └── ...
│   └── package.json
│
├── docs/                # Documentation
│   ├── backend.md
│   ├── frontend.md
│   └── repository-overview.md
│
└── tests/               # Integration tests
    └── test_truly_selective.py
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- XeLaTeX (for PDF generation)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Server runs on `http://localhost:5001`

**API Endpoints:**
- `GET /api/health` - Health check
- `GET /api/modes` - Available manipulation modes
- `POST /api/manipulate` - Create manipulated PDF
- `GET /api/download/<filename>` - Download files

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

UI runs on `http://localhost:5173`

## 🎯 Manipulation Modes

### V4: Unicode Alternates (⭐ RECOMMENDED)
Uses visually similar Unicode characters to handle repeated characters with different visuals.

**Example:**
- Visual: "unidirectional"
- Hidden: "biidirectional"
- Copies as: "biıdіrectïonal" (using ı U+0131, і U+0456, ï U+00EF)

**Supports:**
- ✅ 700+ Unicode alternate mappings
- ✅ Up to 10 occurrences per character
- ✅ All character types (letters, numbers, punctuation)

### V1: Basic (Limited)
Simple two-font approach. Cannot handle repeated characters needing different visuals.

### V3: OpenType (Experimental)
Uses contextual alternates. Not truly selective - affects all pattern instances globally.

### Cyrillic & PUA
Alternative techniques with different trade-offs.

## 📊 Testing

### Run Backend Tests
```bash
cd backend
python test_v4.py
```

**Latest Results:** 17/19 tests passing (89% success rate)

### Test API Manually
```bash
curl -X POST http://localhost:5001/api/manipulate \
  -H "Content-Type: application/json" \
  -d '{"mode": "truly_selective_v4", "visual_word": "hello", "hidden_word": "anita"}'
```

## 📖 Documentation

- **Backend API**: See `backend/README.md` for complete API documentation
- **Technical Details**: See `backend/SOLUTION_SUMMARY.md` for implementation details
- **Architecture**: See `docs/` for project architecture and design decisions

## 🔬 Research Context

This implementation is based on research into font manipulation techniques for deceptive documents. The project demonstrates:

1. **Glyph Cloning**: Copying glyph outlines from visual characters to hidden characters
2. **Unicode Alternates**: Using lookalike characters from different Unicode blocks
3. **OpenType Features**: GSUB table manipulation for contextual substitution
4. **PDF Generation**: Creating documents with embedded deceptive fonts

## ⚠️ Limitations

1. **Word Length**: Both words must be exactly the same length
2. **Character Occurrences**: Maximum 10 occurrences of same character (V4 mode)
3. **XeLaTeX Required**: PDF generation requires XeLaTeX installed
4. **Detection**: Unicode alternates may be detectable under close inspection

## 🛠️ Development

### Current Branch Structure
- `main` - Stable version with V1, V3, V4 manipulators
- `feature_pdf_of_choice` - Clean codebase for new features

### Running in Development

**Backend:**
```bash
cd backend
python app.py  # Runs on port 5001 with hot reload
```

**Frontend:**
```bash
cd frontend
npm run dev  # Runs on port 5173 with hot reload
```

## 📝 License

For educational and research purposes only.

## 🙏 Acknowledgments

Based on research from arXiv:2505.16957 - Font Manipulation for Deceptive Documents.

## 📧 Support

For detailed technical documentation, see:
- Backend: `backend/README.md`
- Frontend: `docs/frontend.md`
- Testing: `docs/testing-and-verification.md`
