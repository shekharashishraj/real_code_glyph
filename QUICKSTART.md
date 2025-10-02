# 🚀 Quick Start Guide - Font Manipulation Tool

## ✅ Current Status
Your API server is **already running** on http://127.0.0.1:5001

## 📋 Step-by-Step Guide

### **Option 1: Test with Example Script (No font needed)**

Run the demonstration script:
```bash
python3 demo_with_sample_font.py
```

This will show you:
- Font manipulation theory
- Text transformation examples
- Unicode analysis
- API connectivity test

### **Option 2: Use with Your Own Font**

#### Step 1: Get a TTF font file

Download a free font:
```bash
# Download Open Sans (recommended)
curl -L -o OpenSans-Regular.ttf \
  "https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Regular.ttf"
```

Or use any `.ttf` font file you have.

#### Step 2: Run the example script

Create `test_with_font.py`:
```python
from pdf_font_integration import PDFFontIntegrator

# Initialize
integrator = PDFFontIntegrator()

# Load your font
if integrator.load_base_font('OpenSans-Regular.ttf'):
    print("✅ Font loaded!")

    # Create mappings
    mappings = [
        {'original': 'hello', 'replacement': 'world'}
    ]

    if integrator.create_word_mappings(mappings):
        print("✅ Mappings created!")

        # Generate PDF
        text = "This is a hello message"
        integrator.create_comparison_pdf(text, 'output.pdf', True)
        print("✅ PDF generated: output.pdf")
```

Run it:
```bash
python3 test_with_font.py
```

### **Option 3: Use the API**

The API server is running. Test it with curl:

#### Health Check:
```bash
curl http://127.0.0.1:5001/api/health
```

#### Upload a Font:
```bash
curl -X POST \
  -F "font=@OpenSans-Regular.ttf" \
  http://127.0.0.1:5001/api/load-font
```

#### Create Mappings and Generate Font:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "font_name": "OpenSans-Regular.ttf",
    "mappings": [
      {"original": "hello", "replacement": "world"},
      {"original": "test", "replacement": "demo"}
    ]
  }' \
  http://127.0.0.1:5001/api/generate-modified-font \
  --output modified_font.ttf
```

## 🎯 What This Tool Does

**Implements the technique from arXiv:2505.16957**

1. **Modifies font glyph mappings** so characters look identical but have different Unicode values
2. **Creates deceptive fonts** where visual appearance ≠ digital content
3. **Generates PDFs** with manipulated fonts for security research

### Example:
- You type: `world` (Unicode: w-o-r-l-d)
- It looks like: `hello` (visually appears as h-e-l-l-o)
- Copy-paste reveals: `world` (actual Unicode)

## 🛠️ Available Components

### Python Modules:
1. **`font_manipulator.py`** - Core font manipulation
2. **`enhanced_font_manipulator.py`** - Advanced glyph mapping
3. **`binary_font_manipulator.py`** - Low-level font editing
4. **`pdf_font_integration.py`** - PDF generation with modified fonts
5. **`font_manipulation_api.py`** - REST API server *(currently running)*

### Demo Scripts:
- **`demo_with_sample_font.py`** - Theory and examples (no font needed)
- **`test_basic_functionality.py`** - Test all components
- **`test_font_manipulation.py`** - Comprehensive test suite

## 📖 Full Documentation

See `README.md` for:
- Complete API documentation
- Security considerations
- Technical implementation details
- Research citations

## ⚠️ Important Notes

### This tool is for DEFENSIVE SECURITY RESEARCH ONLY:
- ✅ Detect font-based attacks
- ✅ Analyze document integrity
- ✅ Research LLM vulnerabilities
- ❌ Do not use maliciously

### Limitations:
- Requires actual `.ttf` font files (not `.ttc` collections)
- Works best with Unicode BMP characters
- Some complex fonts may not be supported

## 🔍 Troubleshooting

### "Font loading failed"
- Make sure you're using a `.ttf` file, not `.ttc`
- Try downloading a simple font from Google Fonts
- Check file permissions

### "API not responding"
- Server is running on port 5001
- Check if port is available: `lsof -i :5001`
- Restart server: Kill and run `python3 font_manipulation_api.py`

### "No module named..."
- Install dependencies: `pip3 install fonttools PyPDF2 reportlab Flask Flask-CORS`

## 🎓 Learn More

**Research Paper:** arXiv:2505.16957
"Invisible Prompts, Visible Threats: Malicious Font Injection in External Resources for Large Language Models"

**Key Concept:**
```
GlyphIndex = idDelta + Unicode
```

By modifying `idDelta`, we change which glyph (visual shape) a Unicode character points to.

## 💡 Quick Examples

### Example 1: Text Transformation
```python
text = "hello world"
mappings = {'hello': 'goodbye', 'world': 'universe'}

for orig, repl in mappings.items():
    text = text.replace(orig, repl)

print(text)  # Output: "goodbye universe"
# But with modified font, still looks like "hello world"!
```

### Example 2: Unicode Analysis
```python
text = "hello"
for char in text:
    print(f"{char} = U+{ord(char):04X}")

# Output:
# h = U+0068
# e = U+0065
# l = U+006C
# l = U+006C
# o = U+006F
```

## 🚀 Next Steps

1. **Download a font** (see Step 1 above)
2. **Run the example** with your font
3. **Experiment** with different mappings
4. **Generate PDFs** to see the effect
5. **Build detection tools** for security research

---

**API Server Status:** ✅ Running on http://127.0.0.1:5001

For questions or issues, check the main README.md or the research paper.