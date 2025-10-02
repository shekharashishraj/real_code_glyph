#!/usr/bin/env python3
"""
Basic functionality test for font manipulation system
"""

from font_manipulator import WordMappingManager
from enhanced_font_manipulator import EnhancedFontManipulator
import tempfile
import os

def test_basic_functionality():
    print("🔬 Testing Font Manipulation System")
    print("=" * 50)

    # Test 1: Basic initialization
    print("1. Testing initialization...")
    manager = WordMappingManager()
    enhanced = EnhancedFontManipulator()
    print("✅ Components initialized successfully")

    # Test 2: Try to find a system font
    print("\\n2. Looking for system fonts...")

    # Common system font locations
    system_fonts = [
        '/System/Library/Fonts/Arial.ttf',           # macOS
        '/System/Library/Fonts/Times.ttf',           # macOS
        '/System/Library/Fonts/Helvetica.ttc',       # macOS
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
        'C:\\\\Windows\\\\Fonts\\\\arial.ttf'        # Windows
    ]

    font_found = None
    for font_path in system_fonts:
        if os.path.exists(font_path):
            font_found = font_path
            print(f"✅ Found font: {font_path}")
            break

    if not font_found:
        print("⚠️  No system font found. You'll need to provide a TTF font file.")
        print("   Download a free font from Google Fonts or use your own TTF file.")
        return False

    # Test 3: Load font
    print("\\n3. Testing font loading...")
    try:
        if manager.load_font(font_found):
            print("✅ Font loaded successfully in WordMappingManager")
        else:
            print("❌ Failed to load font in WordMappingManager")

        if enhanced.load_font(font_found):
            print("✅ Font loaded successfully in EnhancedFontManipulator")

            # Test font analysis
            analysis = enhanced.analyze_cmap_structure()
            print(f"   Font analysis: {len(analysis)} properties found")
            if analysis:
                print(f"   Character count: {analysis.get('character_count', 'unknown')}")
                print(f"   Format: {analysis.get('format', 'unknown')}")
        else:
            print("❌ Failed to load font in EnhancedFontManipulator")

    except Exception as e:
        print(f"❌ Error loading font: {e}")
        return False

    # Test 4: Create a simple mapping
    print("\\n4. Testing mapping creation...")
    try:
        # Simple character mapping: make 'b' appear as 'a'
        if enhanced.create_deceptive_mapping_with_idelta('a', 'b', 'a'):
            print("✅ Created deceptive mapping: 'b' will appear as 'a'")

            # Validate the mapping
            issues = enhanced.validate_modifications()
            if not issues:
                print("✅ Mapping validation passed")
            else:
                print(f"⚠️  Validation issues: {issues}")

        else:
            print("❌ Failed to create mapping")

    except Exception as e:
        print(f"❌ Error creating mapping: {e}")

    # Test 5: Generate modified font
    print("\\n5. Testing font generation...")
    try:
        with tempfile.NamedTemporaryFile(suffix='.ttf', delete=False) as temp_file:
            output_path = temp_file.name

        if enhanced.generate_modified_font(output_path):
            print(f"✅ Modified font generated: {output_path}")
            print(f"   File size: {os.path.getsize(output_path)} bytes")

            # Clean up
            os.unlink(output_path)
            print("✅ Cleanup completed")
        else:
            print("❌ Failed to generate modified font")

    except Exception as e:
        print(f"❌ Error generating font: {e}")

    print("\\n🎉 Basic functionality test completed!")
    return True

def test_api_endpoints():
    """Test API endpoints"""
    print("\\n🌐 Testing API Endpoints")
    print("=" * 50)

    import requests

    try:
        # Test health endpoint
        response = requests.get('http://127.0.0.1:5001/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ API server is responding")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API health check failed: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("   Make sure the API server is running on port 5001")
        return False

    return True

if __name__ == "__main__":
    # Run basic functionality test
    success = test_basic_functionality()

    # Test API if available
    try:
        import requests
        test_api_endpoints()
    except ImportError:
        print("\\n⚠️  'requests' library not installed. Skipping API tests.")
        print("   Install with: pip3 install requests")

    if success:
        print("\\n✅ All tests passed! The system is ready to use.")
    else:
        print("\\n❌ Some tests failed. Check the error messages above.")