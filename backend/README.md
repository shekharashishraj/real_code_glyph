# Font Manipulation Backend API

Flask API for PDF font manipulation based on arXiv:2505.16957.

## Setup

```bash
cd backend
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Server runs on `http://localhost:5001`

## API Endpoints

### `GET /api/health`
Health check

### `GET /api/modes`
Get available manipulation modes

### `POST /api/manipulate`
Create manipulated PDF

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
  "font_file": "abc123_deceptive.ttf",
  "message": "Success"
}
```

### `GET /api/download/<filename>`
Download generated files

## Manipulation Modes

1. **truly_selective** - Recommended, clean output
2. **cyrillic** - Uses Cyrillic homoglyphs
3. **pua** - Private Use Area characters
