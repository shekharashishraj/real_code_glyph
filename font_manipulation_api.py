#!/usr/bin/env python3
"""
Font Manipulation API Server
Provides REST endpoints for the font manipulation GUI
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile
import os
import io
from werkzeug.utils import secure_filename
import PyPDF2
from font_manipulator import WordMappingManager

app = Flask(__name__)
CORS(app)

# Global storage for font managers (in production, use proper session management)
font_managers = {}

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_FONT_EXTENSIONS = {'ttf', 'otf'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_font_manager(session_id='default'):
    """Get or create a font manager for the session."""
    if session_id not in font_managers:
        font_managers[session_id] = WordMappingManager()
    return font_managers[session_id]

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'font-manipulation-api'})

@app.route('/api/extract-text', methods=['POST'])
def extract_pdf_text():
    """Extract text from uploaded PDF."""
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF file uploaded'}), 400

    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
        return jsonify({'error': 'Invalid file type. Only PDF files allowed'}), 400

    try:
        # Read PDF content
        pdf_content = io.BytesIO(file.read())
        pdf_reader = PyPDF2.PdfReader(pdf_content)

        # Extract text from all pages
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() + '\\n'

        return jsonify({
            'text': text.strip(),
            'page_count': len(pdf_reader.pages),
            'filename': file.filename
        })

    except Exception as e:
        return jsonify({'error': f'Failed to extract text from PDF: {str(e)}'}), 500

@app.route('/api/load-font', methods=['POST'])
def load_font():
    """Load a TrueType font for manipulation."""
    if 'font' not in request.files:
        return jsonify({'error': 'No font file uploaded'}), 400

    file = request.files['font']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename, ALLOWED_FONT_EXTENSIONS):
        return jsonify({'error': 'Invalid file type. Only TTF/OTF files allowed'}), 400

    try:
        # Save uploaded font temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Load font in the manager
        session_id = request.form.get('session_id', 'default')
        manager = get_font_manager(session_id)

        if manager.load_font(filepath):
            # Get basic font information
            font_info = {
                'name': filename,
                'path': filepath,
                'character_count': len(manager.font_manipulator.original_cmap) if manager.font_manipulator.original_cmap else 0,
                'loaded': True
            }

            return jsonify({
                'success': True,
                'font_info': font_info,
                'message': f'Font {filename} loaded successfully'
            })
        else:
            return jsonify({'error': 'Failed to load font file'}), 500

    except Exception as e:
        return jsonify({'error': f'Failed to load font: {str(e)}'}), 500

@app.route('/api/preview-mappings', methods=['POST'])
def preview_mappings():
    """Preview character mappings for given word mappings."""
    try:
        data = request.get_json()
        font_name = data.get('font_name')
        mappings = data.get('mappings', [])

        if not font_name or not mappings:
            return jsonify({'error': 'Font name and mappings required'}), 400

        session_id = data.get('session_id', 'default')
        manager = get_font_manager(session_id)

        # Clear existing mappings and add new ones
        manager.clear_all_mappings()

        for mapping in mappings:
            original = mapping.get('original', '')
            replacement = mapping.get('replacement', '')

            if original and replacement:
                if not manager.create_word_mapping(original, replacement):
                    return jsonify({
                        'error': f'Failed to create mapping: {original} -> {replacement}'
                    }), 400

        # Get preview of all mappings
        all_mappings = manager.get_all_mappings()
        preview = all_mappings.get('character_mappings', [])

        return jsonify({
            'preview': preview,
            'word_mappings': all_mappings.get('word_mappings', {}),
            'total_character_mappings': len(preview)
        })

    except Exception as e:
        return jsonify({'error': f'Failed to generate preview: {str(e)}'}), 500

@app.route('/api/generate-modified-font', methods=['POST'])
def generate_modified_font():
    """Generate a modified font with all the specified mappings."""
    try:
        data = request.get_json()
        font_name = data.get('font_name')
        mappings = data.get('mappings', [])

        if not font_name or not mappings:
            return jsonify({'error': 'Font name and mappings required'}), 400

        session_id = data.get('session_id', 'default')
        manager = get_font_manager(session_id)

        # Clear existing mappings and add new ones
        manager.clear_all_mappings()

        for mapping in mappings:
            original = mapping.get('original', '')
            replacement = mapping.get('replacement', '')

            if original and replacement:
                if not manager.create_word_mapping(original, replacement):
                    return jsonify({
                        'error': f'Failed to create mapping: {original} -> {replacement}'
                    }), 400

        # Generate modified font
        with tempfile.NamedTemporaryFile(suffix='.ttf', delete=False) as temp_file:
            output_path = temp_file.name

        if manager.generate_font_with_mappings(output_path):
            # Return the modified font file
            return send_file(
                output_path,
                as_attachment=True,
                download_name=f'modified_{font_name}',
                mimetype='application/font-sfnt'
            )
        else:
            return jsonify({'error': 'Failed to generate modified font'}), 500

    except Exception as e:
        return jsonify({'error': f'Failed to generate modified font: {str(e)}'}), 500

@app.route('/api/get-mappings', methods=['GET'])
def get_current_mappings():
    """Get all current mappings for a session."""
    try:
        session_id = request.args.get('session_id', 'default')
        manager = get_font_manager(session_id)

        all_mappings = manager.get_all_mappings()

        return jsonify({
            'word_mappings': all_mappings.get('word_mappings', {}),
            'character_mappings': all_mappings.get('character_mappings', []),
            'total_mappings': len(all_mappings.get('character_mappings', []))
        })

    except Exception as e:
        return jsonify({'error': f'Failed to get mappings: {str(e)}'}), 500

@app.route('/api/clear-mappings', methods=['POST'])
def clear_mappings():
    """Clear all mappings for a session."""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        manager = get_font_manager(session_id)

        manager.clear_all_mappings()

        return jsonify({
            'success': True,
            'message': 'All mappings cleared successfully'
        })

    except Exception as e:
        return jsonify({'error': f'Failed to clear mappings: {str(e)}'}), 500

@app.route('/api/validate-mapping', methods=['POST'])
def validate_mapping():
    """Validate if a specific mapping is possible with the loaded font."""
    try:
        data = request.get_json()
        original = data.get('original', '')
        replacement = data.get('replacement', '')
        session_id = data.get('session_id', 'default')

        if not original or not replacement:
            return jsonify({'error': 'Both original and replacement text required'}), 400

        manager = get_font_manager(session_id)

        if not manager.font_manipulator.font:
            return jsonify({'error': 'No font loaded'}), 400

        # Check if all characters exist in the font
        missing_chars = []
        for char in original + replacement:
            if ord(char) not in manager.font_manipulator.original_cmap:
                missing_chars.append(char)

        if missing_chars:
            return jsonify({
                'valid': False,
                'error': f'Characters not found in font: {missing_chars}'
            })

        return jsonify({
            'valid': True,
            'message': 'Mapping is valid'
        })

    except Exception as e:
        return jsonify({'error': f'Failed to validate mapping: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Font Manipulation API Server...")
    print("Available endpoints:")
    print("  GET  /api/health - Health check")
    print("  POST /api/extract-text - Extract text from PDF")
    print("  POST /api/load-font - Load TrueType font")
    print("  POST /api/preview-mappings - Preview character mappings")
    print("  POST /api/generate-modified-font - Generate modified font")
    print("  GET  /api/get-mappings - Get current mappings")
    print("  POST /api/clear-mappings - Clear all mappings")
    print("  POST /api/validate-mapping - Validate mapping possibility")

    app.run(host='0.0.0.0', port=5001, debug=True)