#!/usr/bin/env python3
"""
Verify the PUA manipulation by analyzing the PDF at byte level
"""

import PyPDF2

def analyze_pdf_unicode(pdf_path):
    """Analyze actual Unicode in PDF."""
    print("=" * 70)
    print("  UNICODE ANALYSIS - Finding PUA Characters")
    print("=" * 70)
    print()

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()

            print(f"Page {page_num}:")
            print("-" * 70)

            # Find PUA characters (U+E000 to U+F8FF)
            pua_found = []
            for i, char in enumerate(text):
                code = ord(char)
                if 0xE000 <= code <= 0xF8FF:
                    # Found a PUA character
                    context_start = max(0, i - 10)
                    context_end = min(len(text), i + 10)
                    context = text[context_start:context_end]

                    pua_found.append({
                        'position': i,
                        'char': char,
                        'code': code,
                        'context': context
                    })

            if pua_found:
                print(f"✅ Found {len(pua_found)} PUA characters:")
                for pua in pua_found:
                    print(f"\n  Position {pua['position']}:")
                    print(f"    Unicode: U+{pua['code']:04X}")
                    print(f"    Character: '{pua['char']}' (may show as box)")
                    print(f"    Context: ...{repr(pua['context'])}...")
            else:
                print("  ℹ️  No PUA characters found in this page")

            print()

            # Show some regular "hello" instances for comparison
            hello_count = text.count('hello')
            if hello_count > 0:
                print(f"  Regular 'hello' count: {hello_count}")

                # Find first occurrence and show its Unicode
                hello_pos = text.find('hello')
                if hello_pos != -1:
                    hello_text = text[hello_pos:hello_pos+5]
                    print(f"  First 'hello' Unicode:")
                    for char in hello_text:
                        print(f"    '{char}' = U+{ord(char):04X}")

    print()
    print("=" * 70)
    print("🎯 SUMMARY:")
    print("=" * 70)
    print()
    print("If PUA characters were found:")
    print("  ✅ Selective manipulation WORKED!")
    print("  ✅ Only specific word uses different Unicode")
    print("  ✅ All other text remains normal")
    print()
    print("PUA (Private Use Area) characters U+E000-E004 were mapped to")
    print("display as 'hello' glyphs, but they're actually different Unicode!")
    print()

if __name__ == "__main__":
    analyze_pdf_unicode('selective_manipulation.pdf')
