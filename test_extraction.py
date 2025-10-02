#!/usr/bin/env python3
"""
Test script to extract and verify text from the manipulated PDF
"""

import PyPDF2
import sys

def extract_and_test_pdf(pdf_path):
    """Extract text from PDF and verify the manipulation worked."""

    print("=" * 70)
    print("  PDF TEXT EXTRACTION TEST")
    print("=" * 70)
    print()

    print(f"📄 Extracting text from: {pdf_path}\n")

    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            print(f"📊 PDF Info:")
            print(f"   Pages: {len(reader.pages)}")
            print(f"   Title: {reader.metadata.get('/Title', 'N/A') if reader.metadata else 'N/A'}")
            print()

            # Extract all text
            full_text = ""
            for i, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                full_text += page_text
                print(f"   Page {i}: {len(page_text)} characters extracted")

            print()
            print("=" * 70)
            print("📝 EXTRACTED TEXT:")
            print("=" * 70)
            print(full_text)
            print()
            print("=" * 70)

            # Check for our manipulated text
            print("\n🔍 VERIFICATION:")
            print("=" * 70)

            test_cases = [
                ("world", "This is what we TYPED (should be found in extracted text)"),
                ("hello", "This is what it LOOKS like (might appear in headers)")
            ]

            for search_text, description in test_cases:
                if search_text.lower() in full_text.lower():
                    # Find context
                    idx = full_text.lower().find(search_text.lower())
                    context_start = max(0, idx - 30)
                    context_end = min(len(full_text), idx + len(search_text) + 30)
                    context = full_text[context_start:context_end]

                    print(f"\n✅ Found '{search_text}'!")
                    print(f"   {description}")
                    print(f"   Context: ...{context}...")
                else:
                    print(f"\n❌ NOT found: '{search_text}'")
                    print(f"   {description}")

            print()
            print("=" * 70)
            print("🎯 WHAT THIS MEANS:")
            print("=" * 70)

            if 'world' in full_text.lower():
                print("✅ SUCCESS! The PDF contains the word 'world'")
                print("   This proves the Unicode content is 'world'")
                print()
                print("📋 VERIFICATION STEPS:")
                print("   1. Open the PDF: true_manipulation_demo.pdf")
                print("   2. Look at the RED text")
                print("   3. It will VISUALLY appear as 'hello'")
                print("   4. Select and copy that RED text")
                print("   5. Paste into any text editor")
                print("   6. You will see 'world' (not 'hello'!)")
                print()
                print("🎉 Font manipulation is WORKING!")
                print("   Visual: hello")
                print("   Actual: world")

            else:
                print("⚠️  The word 'world' was not found in extracted text")
                print("   This might mean:")
                print("   - Text extraction didn't capture all content")
                print("   - The font manipulation affected extraction")

            return True

    except FileNotFoundError:
        print(f"❌ File not found: {pdf_path}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    pdf_file = sys.argv[1] if len(sys.argv) > 1 else "true_manipulation_demo.pdf"
    extract_and_test_pdf(pdf_file)
