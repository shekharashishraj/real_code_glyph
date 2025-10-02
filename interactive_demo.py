#!/usr/bin/env python3
"""
Interactive demo for font manipulation system
Works with the running API server
"""

import requests
import json

def interactive_demo():
    """Interactive demonstration of the font manipulation system."""
    print("🎯 Interactive Font Manipulation Demo")
    print("=" * 50)

    # Check API server
    try:
        response = requests.get('http://127.0.0.1:5001/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            server_info = response.json()
            print(f"   Service: {server_info.get('service', 'unknown')}")
        else:
            print("❌ API server not responding correctly")
            return
    except:
        print("❌ Cannot connect to API server")
        print("   Make sure to run: python3 font_manipulation_api.py")
        return

    print("\\n🎮 What would you like to do?")
    print("1. Test text transformation (no font needed)")
    print("2. Test API endpoints")
    print("3. Show font manipulation theory")
    print("4. Exit")

    while True:
        try:
            choice = input("\\nEnter your choice (1-4): ").strip()

            if choice == '1':
                demo_text_transformation()
            elif choice == '2':
                demo_api_endpoints()
            elif choice == '3':
                show_theory()
            elif choice == '4':
                print("👋 Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-4.")

        except KeyboardInterrupt:
            print("\\n👋 Goodbye!")
            break

def demo_text_transformation():
    """Demo text transformation."""
    print("\\n🔄 Text Transformation Demo")
    print("-" * 30)

    # Get user input
    text = input("Enter text to transform: ").strip()
    if not text:
        text = "Hello world, this is a secret message"
        print(f"Using default: {text}")

    # Define mappings
    mappings = {
        'hello': 'greetings',
        'world': 'universe',
        'secret': 'hidden',
        'message': 'content'
    }

    print(f"\\nMappings to apply:")
    for orig, repl in mappings.items():
        print(f"  '{orig}' → '{repl}'")

    # Transform text
    transformed = text.lower()
    for original, replacement in mappings.items():
        transformed = transformed.replace(original, replacement)

    print(f"\\nOriginal:    {text}")
    print(f"Transformed: {transformed}")

    # Show Unicode difference
    print(f"\\nUnicode Analysis:")
    print(f"Original chars:    {[c for c in text[:10]]}")
    print(f"Transformed chars: {[c for c in transformed[:10]]}")

    print(f"\\nOriginal Unicode:    {[f'U+{ord(c):04X}' for c in text[:5]]}")
    print(f"Transformed Unicode: {[f'U+{ord(c):04X}' for c in transformed[:5]]}")

def demo_api_endpoints():
    """Demo API endpoints."""
    print("\\n🌐 API Endpoints Demo")
    print("-" * 30)

    base_url = "http://127.0.0.1:5001/api"

    # Test health
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test validation (this will fail without a font, but shows the interface)
    print("\\n2. Testing validation endpoint...")
    try:
        data = {
            "original": "hello",
            "replacement": "world"
        }
        response = requests.post(f"{base_url}/validate-mapping", json=data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error (expected - no font loaded): {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test get mappings
    print("\\n3. Testing get mappings endpoint...")
    try:
        response = requests.get(f"{base_url}/get-mappings")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

def show_theory():
    """Show the theoretical background."""
    print("\\n📚 Font Manipulation Theory")
    print("-" * 30)

    print("Based on research paper: arXiv:2505.16957")
    print("'Invisible Prompts, Visible Threats: Malicious Font Injection'")
    print()

    print("🔬 Core Technique:")
    print("• Modify TrueType font glyph mappings")
    print("• Formula: GlyphIndex = idDelta + Unicode")
    print("• Change idDelta to point different Unicode → same visual glyph")
    print()

    print("⚙️ Implementation Steps:")
    print("1. Load TrueType font and parse cmap table")
    print("2. Isolate target characters in separate segments")
    print("3. Calculate new idDelta values")
    print("4. Rebuild cmap table with modified mappings")
    print("5. Generate new font file")
    print()

    print("🎯 Result:")
    print("• Text appears visually unchanged")
    print("• Unicode content is different")
    print("• Copy-paste reveals actual characters")
    print("• Useful for security research and detection")
    print()

    print("🛡️ Defensive Applications:")
    print("• Detect font-based attacks")
    print("• Analyze document integrity")
    print("• Research LLM vulnerabilities")
    print("• Build security tools")

def main():
    """Main function."""
    try:
        interactive_demo()
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        print("\\nTroubleshooting:")
        print("1. Make sure the API server is running:")
        print("   python3 font_manipulation_api.py")
        print("2. Check if port 5001 is available")
        print("3. Install required packages:")
        print("   pip3 install requests")

if __name__ == "__main__":
    main()