import React, { useState, useEffect } from 'react';
import './FontManipulationGUI.css';

const FontManipulationGUI = () => {
    const [pdfText, setPdfText] = useState('');
    const [selectedWords, setSelectedWords] = useState([]);
    const [currentMapping, setCurrentMapping] = useState({ original: '', replacement: '' });
    const [wordMappings, setWordMappings] = useState([]);
    const [loadedFont, setLoadedFont] = useState(null);
    const [fontFile, setFontFile] = useState(null);
    const [previewMappings, setPreviewMappings] = useState([]);
    const [isProcessing, setIsProcessing] = useState(false);

    // Extract text from uploaded PDF
    const extractPDFText = async (file) => {
        const formData = new FormData();
        formData.append('pdf', file);

        try {
            const response = await fetch('/api/extract-text', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                setPdfText(data.text);
            } else {
                console.error('Failed to extract PDF text');
            }
        } catch (error) {
            console.error('Error extracting PDF text:', error);
        }
    };

    // Handle word selection in the text
    const handleTextSelection = () => {
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();

        if (selectedText && !selectedWords.includes(selectedText)) {
            setSelectedWords([...selectedWords, selectedText]);
            setCurrentMapping({ ...currentMapping, original: selectedText });
        }
    };

    // Add a new word mapping
    const addWordMapping = () => {
        if (currentMapping.original && currentMapping.replacement) {
            const newMapping = {
                id: Date.now(),
                original: currentMapping.original,
                replacement: currentMapping.replacement,
                status: 'pending'
            };

            setWordMappings([...wordMappings, newMapping]);
            setCurrentMapping({ original: '', replacement: '' });
        }
    };

    // Remove a word mapping
    const removeWordMapping = (id) => {
        setWordMappings(wordMappings.filter(mapping => mapping.id !== id));
    };

    // Upload and load font file
    const handleFontUpload = async (event) => {
        const file = event.target.files[0];
        if (file && file.name.endsWith('.ttf')) {
            setFontFile(file);

            const formData = new FormData();
            formData.append('font', file);

            try {
                const response = await fetch('/api/load-font', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();
                    setLoadedFont(data.font_info);
                } else {
                    console.error('Failed to load font');
                }
            } catch (error) {
                console.error('Error loading font:', error);
            }
        }
    };

    // Generate modified font with mappings
    const generateModifiedFont = async () => {
        if (!fontFile || wordMappings.length === 0) {
            alert('Please load a font and add at least one mapping');
            return;
        }

        setIsProcessing(true);

        try {
            const response = await fetch('/api/generate-modified-font', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    font_name: fontFile.name,
                    mappings: wordMappings.map(m => ({
                        original: m.original,
                        replacement: m.replacement
                    }))
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `modified_${fontFile.name}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                // Update mapping status
                setWordMappings(wordMappings.map(m => ({ ...m, status: 'completed' })));
            } else {
                console.error('Failed to generate modified font');
            }
        } catch (error) {
            console.error('Error generating modified font:', error);
        } finally {
            setIsProcessing(false);
        }
    };

    // Get preview of character mappings
    const getPreview = async () => {
        if (wordMappings.length === 0) return;

        try {
            const response = await fetch('/api/preview-mappings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    font_name: fontFile?.name,
                    mappings: wordMappings.map(m => ({
                        original: m.original,
                        replacement: m.replacement
                    }))
                })
            });

            if (response.ok) {
                const data = await response.json();
                setPreviewMappings(data.preview);
            }
        } catch (error) {
            console.error('Error getting preview:', error);
        }
    };

    useEffect(() => {
        if (wordMappings.length > 0) {
            getPreview();
        }
    }, [wordMappings]);

    return (
        <div className="font-manipulation-container">
            <h1>Font Manipulation Tool</h1>
            <p className="subtitle">Create visually identical characters with different Unicode mappings</p>

            {/* Font Upload Section */}
            <div className="section">
                <h2>1. Load Font</h2>
                <div className="upload-area">
                    <input
                        type="file"
                        accept=".ttf"
                        onChange={handleFontUpload}
                        id="font-upload"
                        className="file-input"
                    />
                    <label htmlFor="font-upload" className="upload-label">
                        {fontFile ? `Loaded: ${fontFile.name}` : 'Choose TTF Font File'}
                    </label>
                </div>
                {loadedFont && (
                    <div className="font-info">
                        <p><strong>Font loaded:</strong> {loadedFont.name}</p>
                        <p><strong>Characters available:</strong> {loadedFont.character_count}</p>
                    </div>
                )}
            </div>

            {/* PDF Text Display Section */}
            <div className="section">
                <h2>2. Select Text (Optional)</h2>
                <div className="file-upload">
                    <input
                        type="file"
                        accept=".pdf"
                        onChange={(e) => {
                            const file = e.target.files[0];
                            if (file) extractPDFText(file);
                        }}
                        id="pdf-upload"
                        className="file-input"
                    />
                    <label htmlFor="pdf-upload" className="upload-label">
                        Upload PDF to extract text
                    </label>
                </div>

                {pdfText && (
                    <div
                        className="text-display"
                        onMouseUp={handleTextSelection}
                    >
                        {pdfText}
                    </div>
                )}

                <div className="manual-input">
                    <h3>Or manually enter word:</h3>
                    <input
                        type="text"
                        placeholder="Enter word to manipulate"
                        value={currentMapping.original}
                        onChange={(e) => setCurrentMapping({
                            ...currentMapping,
                            original: e.target.value
                        })}
                        className="word-input"
                    />
                </div>
            </div>

            {/* Word Mapping Section */}
            <div className="section">
                <h2>3. Configure Word Mappings</h2>

                <div className="mapping-input">
                    <div className="input-group">
                        <label>Original Word (Visual Appearance):</label>
                        <input
                            type="text"
                            value={currentMapping.original}
                            onChange={(e) => setCurrentMapping({
                                ...currentMapping,
                                original: e.target.value
                            })}
                            placeholder="e.g., hello"
                        />
                    </div>

                    <div className="input-group">
                        <label>Replacement Word (Unicode Value):</label>
                        <input
                            type="text"
                            value={currentMapping.replacement}
                            onChange={(e) => setCurrentMapping({
                                ...currentMapping,
                                replacement: e.target.value
                            })}
                            placeholder="e.g., world"
                        />
                    </div>

                    <button onClick={addWordMapping} className="add-mapping-btn">
                        Add Mapping
                    </button>
                </div>

                {/* Display Current Mappings */}
                <div className="mappings-list">
                    <h3>Current Mappings:</h3>
                    {wordMappings.length === 0 ? (
                        <p className="no-mappings">No mappings added yet</p>
                    ) : (
                        wordMappings.map((mapping) => (
                            <div key={mapping.id} className={`mapping-item ${mapping.status}`}>
                                <div className="mapping-info">
                                    <span className="visual">Looks like: <strong>{mapping.original}</strong></span>
                                    <span className="unicode">Unicode: <strong>{mapping.replacement}</strong></span>
                                    <span className={`status ${mapping.status}`}>{mapping.status}</span>
                                </div>
                                <button
                                    onClick={() => removeWordMapping(mapping.id)}
                                    className="remove-btn"
                                >
                                    Remove
                                </button>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Preview Section */}
            {previewMappings.length > 0 && (
                <div className="section">
                    <h2>4. Preview Character Mappings</h2>
                    <div className="preview-grid">
                        {previewMappings.map((preview, index) => (
                            <div key={index} className="preview-item">
                                <div className="character-info">
                                    <span className="unicode-code">U+{preview.unicode_value.toString(16).toUpperCase()}</span>
                                    <span className="character">{preview.character}</span>
                                    <span className="visual">→ {preview.visual_appearance}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Generate Font Section */}
            <div className="section">
                <h2>5. Generate Modified Font</h2>
                <button
                    onClick={generateModifiedFont}
                    disabled={!fontFile || wordMappings.length === 0 || isProcessing}
                    className="generate-btn"
                >
                    {isProcessing ? 'Generating...' : 'Generate Modified Font'}
                </button>

                <div className="instructions">
                    <h3>Usage Instructions:</h3>
                    <ol>
                        <li>Download the generated font file</li>
                        <li>Install it on your system or embed it in your PDF</li>
                        <li>Text with the replacement Unicode values will visually appear as the original words</li>
                        <li>The actual Unicode content will be different from the visual appearance</li>
                    </ol>
                </div>
            </div>
        </div>
    );
};

export default FontManipulationGUI;