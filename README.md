# Font Manipulation Tool

A web-based tool for creating deceptive PDFs using font manipulation techniques based on arXiv:2505.16957.

## Features

✅ **Truly Selective Manipulation** - Only specific word instances affected
✅ **Multiple Manipulation Modes** - Cyrillic, PUA, and dual-font approaches
✅ **Clean React UI** - Modern, responsive interface
✅ **Flask Backend** - Robust API with multiple manipulators

## Project Structure

```
real_code_glyph/
├── backend/              # Flask API
│   ├── app.py           # Main API server
│   ├── manipulators/    # Manipulation modules
│   │   ├── truly_selective.py
│   │   ├── cyrillic.py
│   │   └── pua.py
│   ├── fonts/           # Base fonts
│   ├── outputs/         # Generated PDFs
│   └── requirements.txt
│
└── frontend/            # React UI
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   └── main.jsx
    ├── package.json
    └── vite.config.js
```

## Setup & Installation

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### 1. Start Backend (Terminal 1)

```bash
cd backend
python app.py
```

Backend runs on `http://localhost:5001`

### 2. Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend runs on `http://localhost:3000`

### 3. Open Browser

Navigate to `http://localhost:3000`

## How to Use

1. **Select Manipulation Mode**
   - Truly Selective (Recommended)
   - Cyrillic Homoglyphs
   - Private Use Area (PUA)

2. **Configure Words**
   - Visual Word: What the user sees
   - Hidden Word: What gets copied
   - Must be same length!

3. **Generate PDF**
   - Click "Generate PDF"
   - Wait for processing

4. **Download & Test**
   - Download the generated PDF
   - Open and find the RED word
   - Copy it and paste into text editor
   - Observe the difference!

## API Endpoints

### `GET /api/health`
Check API health

### `GET /api/modes`
Get available manipulation modes

### `POST /api/manipulate`
Generate manipulated PDF

**Request:**
```json
{
  "mode": "truly_selective",
  "visual_word": "hello",
  "hidden_word": "world"
}
```

**Response:**
```json
{
  "success": true,
  "pdf_file": "abc123.pdf",
  "font_file": "abc123_deceptive.ttf"
}
```

### `GET /api/download/<filename>`
Download generated files

## Manipulation Modes

### 1. Truly Selective (Recommended)
- Uses two fonts (normal + deceptive)
- Only specific word instance manipulated
- All other text completely normal
- Clean, professional output

### 2. Cyrillic Homoglyphs
- Maps Cyrillic chars to Latin glyphs
- Single font solution
- Copies as Cyrillic characters
- Survives PDF extraction

### 3. Private Use Area (PUA)
- Uses Unicode PUA range (U+E000+)
- Precise control
- Copies as boxes/unknown chars
- May not survive all PDF operations

## Requirements

### Backend
- Python 3.10+
- Flask
- fonttools
- XeLaTeX (for PDF generation)

### Frontend
- Node.js 18+
- React 18
- Vite

## Research Paper

Based on: **arXiv:2505.16957** - Invisible Prompts, Visible Threats: Malicious Font Injection

## Educational Purpose

⚠️ **This tool is for educational and defensive security research only.**

Do not use for malicious purposes.
