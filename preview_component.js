import React, { useState, useEffect, useRef } from 'react';
import './PreviewComponent.css';

const FontMappingPreview = ({ mappings, fontFile, onMappingUpdate }) => {
    const [previewData, setPreviewData] = useState([]);
    const [selectedMapping, setSelectedMapping] = useState(null);
    const [canvasSize, setCanvasSize] = useState({ width: 400, height: 200 });
    const originalCanvasRef = useRef(null);
    const modifiedCanvasRef = useRef(null);
    const [loadedFont, setLoadedFont] = useState(null);

    useEffect(() => {
        if (fontFile && mappings.length > 0) {
            generatePreview();
        }
    }, [mappings, fontFile]);

    useEffect(() => {
        if (fontFile) {
            loadFontForPreview();
        }
    }, [fontFile]);

    const loadFontForPreview = async () => {
        try {
            const fontUrl = URL.createObjectURL(fontFile);
            const fontFace = new FontFace('PreviewFont', `url(${fontUrl})`);
            const loadedFontFace = await fontFace.load();
            document.fonts.add(loadedFontFace);
            setLoadedFont('PreviewFont');
        } catch (error) {
            console.error('Error loading font for preview:', error);
            setLoadedFont('Arial'); // Fallback
        }
    };

    const generatePreview = async () => {
        try {
            const response = await fetch('/api/generate-preview-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mappings: mappings.map(m => ({
                        original: m.original,
                        replacement: m.replacement
                    })),
                    font_name: fontFile?.name
                })
            });

            if (response.ok) {
                const data = await response.json();
                setPreviewData(data.preview_data);
            }
        } catch (error) {
            console.error('Error generating preview:', error);
        }
    };

    const drawCharacterComparison = (mapping, canvasRef, useModifiedFont = false) => {
        const canvas = canvasRef.current;
        if (!canvas || !loadedFont) return;

        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Set font
        ctx.font = useModifiedFont ? `48px ModifiedFont` : `48px ${loadedFont}`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        // Draw background
        ctx.fillStyle = '#f8f9fa';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw border
        ctx.strokeStyle = '#dee2e6';
        ctx.strokeRect(0, 0, canvas.width, canvas.height);

        // Draw character
        const textToDraw = useModifiedFont ? mapping.replacement : mapping.original;

        ctx.fillStyle = '#2c3e50';
        ctx.fillText(textToDraw, canvas.width / 2, canvas.height / 2);

        // Draw Unicode value
        ctx.font = '12px Arial';
        ctx.fillStyle = '#6c757d';
        const unicodeText = textToDraw.split('').map(char => `U+${char.charCodeAt(0).toString(16).toUpperCase().padStart(4, '0')}`).join(' ');
        ctx.fillText(unicodeText, canvas.width / 2, canvas.height - 20);

        // Draw visual appearance label
        ctx.fillStyle = '#28a745';
        ctx.fillText(`Visual: "${mapping.original}"`, canvas.width / 2, 20);
    };

    const handleMappingSelect = (mapping) => {
        setSelectedMapping(mapping);
        if (originalCanvasRef.current && modifiedCanvasRef.current) {
            drawCharacterComparison(mapping, originalCanvasRef, false);
            drawCharacterComparison(mapping, modifiedCanvasRef, true);
        }
    };

    const CharacterAnalysisTable = () => (
        <div className="character-analysis">
            <h3>Character Mapping Analysis</h3>
            <table className="analysis-table">
                <thead>
                    <tr>
                        <th>Original Character</th>
                        <th>Unicode Value</th>
                        <th>Replacement Character</th>
                        <th>Unicode Value</th>
                        <th>Visual Appearance</th>
                        <th>Deception Level</th>
                    </tr>
                </thead>
                <tbody>
                    {mappings.map((mapping, index) => {
                        const originalUnicode = mapping.original.charCodeAt(0);
                        const replacementUnicode = mapping.replacement.charCodeAt(0);
                        const deceptionLevel = originalUnicode === replacementUnicode ? 'None' : 'High';

                        return (
                            <tr
                                key={index}
                                className={`mapping-row ${selectedMapping === mapping ? 'selected' : ''}`}
                                onClick={() => handleMappingSelect(mapping)}
                            >
                                <td className="character-cell">{mapping.original}</td>
                                <td className="unicode-cell">U+{originalUnicode.toString(16).toUpperCase().padStart(4, '0')}</td>
                                <td className="character-cell">{mapping.replacement}</td>
                                <td className="unicode-cell">U+{replacementUnicode.toString(16).toUpperCase().padStart(4, '0')}</td>
                                <td className="visual-cell">{mapping.original}</td>
                                <td className={`deception-cell ${deceptionLevel.toLowerCase()}`}>{deceptionLevel}</td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );

    const GlyphComparisonView = () => (
        <div className="glyph-comparison">
            <h3>Glyph Comparison</h3>
            {selectedMapping ? (
                <div className="comparison-container">
                    <div className="comparison-item">
                        <h4>Original Font Rendering</h4>
                        <canvas
                            ref={originalCanvasRef}
                            width={canvasSize.width}
                            height={canvasSize.height}
                            className="glyph-canvas original"
                        />
                        <div className="canvas-info">
                            <p><strong>Unicode:</strong> U+{selectedMapping.original.charCodeAt(0).toString(16).toUpperCase().padStart(4, '0')}</p>
                            <p><strong>Character:</strong> "{selectedMapping.original}"</p>
                        </div>
                    </div>

                    <div className="comparison-arrow">
                        <span>→</span>
                        <p>Font Manipulation</p>
                    </div>

                    <div className="comparison-item">
                        <h4>Modified Font Rendering</h4>
                        <canvas
                            ref={modifiedCanvasRef}
                            width={canvasSize.width}
                            height={canvasSize.height}
                            className="glyph-canvas modified"
                        />
                        <div className="canvas-info">
                            <p><strong>Unicode:</strong> U+{selectedMapping.replacement.charCodeAt(0).toString(16).toUpperCase().padStart(4, '0')}</p>
                            <p><strong>Character:</strong> "{selectedMapping.replacement}"</p>
                            <p><strong>Visual Appearance:</strong> "{selectedMapping.original}"</p>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="no-selection">
                    <p>Select a mapping from the table above to see the glyph comparison</p>
                </div>
            )}
        </div>
    );

    const TextPreviewSection = () => {
        const [previewText, setPreviewText] = useState('Hello World');
        const [transformedText, setTransformedText] = useState('');

        useEffect(() => {
            // Transform preview text based on mappings
            let transformed = previewText;
            mappings.forEach(mapping => {
                transformed = transformed.replaceAll(mapping.original, mapping.replacement);
            });
            setTransformedText(transformed);
        }, [previewText, mappings]);

        return (
            <div className="text-preview">
                <h3>Text Preview</h3>
                <div className="preview-input">
                    <label>Enter text to preview:</label>
                    <input
                        type="text"
                        value={previewText}
                        onChange={(e) => setPreviewText(e.target.value)}
                        placeholder="Type text to see the mapping effect"
                        className="preview-text-input"
                    />
                </div>

                <div className="preview-results">
                    <div className="preview-result-item">
                        <h4>Original Text (Normal Font)</h4>
                        <div className="text-display original-text" style={{ fontFamily: loadedFont || 'Arial' }}>
                            {previewText}
                        </div>
                        <div className="unicode-display">
                            Unicode: {previewText.split('').map(char => `U+${char.charCodeAt(0).toString(16).toUpperCase().padStart(4, '0')}`).join(' ')}
                        </div>
                    </div>

                    <div className="preview-result-item">
                        <h4>Modified Text (Manipulated Font)</h4>
                        <div className="text-display modified-text" style={{ fontFamily: 'ModifiedFont, Arial' }}>
                            {transformedText}
                        </div>
                        <div className="unicode-display">
                            Unicode: {transformedText.split('').map(char => `U+${char.charCodeAt(0).toString(16).toUpperCase().padStart(4, '0')}`).join(' ')}
                        </div>
                    </div>
                </div>

                <div className="preview-explanation">
                    <h5>Explanation:</h5>
                    <ul>
                        <li>Both text displays should appear visually identical</li>
                        <li>However, they contain different Unicode characters</li>
                        <li>This demonstrates the font manipulation technique</li>
                        <li>Copy-paste operations will reveal the different Unicode values</li>
                    </ul>
                </div>
            </div>
        );
    };

    const StatisticsPanel = () => {
        const totalMappings = mappings.length;
        const uniqueOriginalChars = new Set(mappings.map(m => m.original)).size;
        const uniqueReplacementChars = new Set(mappings.map(m => m.replacement)).size;
        const identicalMappings = mappings.filter(m => m.original === m.replacement).length;

        return (
            <div className="statistics-panel">
                <h3>Mapping Statistics</h3>
                <div className="stats-grid">
                    <div className="stat-item">
                        <span className="stat-value">{totalMappings}</span>
                        <span className="stat-label">Total Mappings</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-value">{uniqueOriginalChars}</span>
                        <span className="stat-label">Unique Original Characters</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-value">{uniqueReplacementChars}</span>
                        <span className="stat-label">Unique Replacement Characters</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-value">{totalMappings - identicalMappings}</span>
                        <span className="stat-label">Deceptive Mappings</span>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="font-mapping-preview">
            <div className="preview-header">
                <h2>Font Mapping Preview</h2>
                <p>Visual analysis of character mappings and their effects</p>
            </div>

            <StatisticsPanel />
            <CharacterAnalysisTable />
            <GlyphComparisonView />
            <TextPreviewSection />

            <div className="preview-controls">
                <button onClick={generatePreview} className="refresh-preview-btn">
                    Refresh Preview
                </button>
                <button
                    onClick={() => {
                        setCanvasSize(prev => ({
                            width: prev.width === 400 ? 600 : 400,
                            height: prev.height === 200 ? 300 : 200
                        }));
                    }}
                    className="resize-canvas-btn"
                >
                    Toggle Canvas Size
                </button>
            </div>
        </div>
    );
};

export default FontMappingPreview;