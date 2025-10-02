#!/usr/bin/env python3
"""
Generate a PDF demonstrating font manipulation
"""

from pdf_font_integration import PDFFontIntegrator
import os

def main():
    print("🎯 Generating Font Manipulation PDF Demo")
    print("=" * 50)

    # Check if font exists
    font_path = 'OpenSans-Regular.ttf'
    if not os.path.exists(font_path):
        print(f"❌ Font file not found: {font_path}")
        print("Please run: curl -L -o OpenSans-Regular.ttf ...")
        return False

    print(f"✅ Found font: {font_path}")

    # Initialize integrator
    print("\n1. Initializing PDF integrator...")
    integrator = PDFFontIntegrator()

    # Load font
    print("2. Loading font...")
    if not integrator.load_base_font(font_path):
        print("❌ Failed to load font")
        return False

    print("✅ Font loaded successfully")

    # Create word mappings
    print("\n3. Creating word mappings...")
    mappings = [
        {'original': 'hello', 'replacement': 'world'},
        {'original': 'secret', 'replacement': 'public'},
        {'original': 'hidden', 'replacement': 'visible'}
    ]

    print("   Mappings:")
    for m in mappings:
        print(f"   • '{m['original']}' → '{m['replacement']}' (will look like '{m['original']}')")

    if not integrator.create_word_mappings(mappings):
        print("❌ Failed to create mappings")
        return False

    print("✅ Mappings created")

    # Generate PDF
    print("\n4. Generating PDF...")

    text = "This is a hello message with secret and hidden content!"
    output_pdf = "font_manipulation_demo.pdf"

    print(f"   Text: {text}")
    print(f"   Output: {output_pdf}")

    try:
        success = integrator.create_comparison_pdf(
            text=text,
            output_path=output_pdf,
            show_comparison=True
        )

        if success:
            print(f"\n✅ PDF generated successfully: {output_pdf}")
            print(f"   File size: {os.path.getsize(output_pdf)} bytes")

            # Also generate a simple version
            print("\n5. Generating simple version...")
            simple_pdf = "simple_demo.pdf"

            success2 = integrator.create_comparison_pdf(
                text=text,
                output_path=simple_pdf,
                show_comparison=False
            )

            if success2:
                print(f"✅ Simple PDF generated: {simple_pdf}")

            # Show what happened
            print("\n" + "=" * 50)
            print("📄 PDFs Generated!")
            print("=" * 50)
            print(f"1. {output_pdf} - Full comparison PDF")
            print(f"2. {simple_pdf} - Simple version")
            print()
            print("🔍 What to look for:")
            print("• Visual text appears normal")
            print("• Unicode content is different")
            print("• Copy-paste reveals actual characters")
            print()
            print("📖 Open the PDFs to see the effect:")
            print(f"   open {output_pdf}")

            # Cleanup
            integrator.cleanup()

            return True
        else:
            print("❌ Failed to generate PDF")
            return False

    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Success! Check the generated PDF files.")
    else:
        print("\n❌ Failed to generate PDFs. Check errors above.")
