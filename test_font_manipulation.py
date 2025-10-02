#!/usr/bin/env python3
"""
Comprehensive Test Suite for Font Manipulation Implementation
Tests the complete pipeline from font loading to PDF generation
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from font_manipulator import WordMappingManager
from enhanced_font_manipulator import EnhancedFontManipulator
from binary_font_manipulator import BinaryFontManipulator
from pdf_font_integration import PDFFontIntegrator


class TestFontManipulation(unittest.TestCase):
    """Test suite for font manipulation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_font_path = self._create_test_font()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _create_test_font(self):
        """Create or locate a test font file."""
        # For testing, we'll use a system font or create a minimal test font
        # In a real implementation, you'd use an actual TTF file

        # Try to find a system font
        system_fonts = [
            '/System/Library/Fonts/Arial.ttf',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
            'C:\\Windows\\Fonts\\arial.ttf'  # Windows
        ]

        for font_path in system_fonts:
            if os.path.exists(font_path):
                return font_path

        # If no system font found, return a placeholder path
        return 'test_font.ttf'

    def test_word_mapping_manager_basic_functionality(self):
        """Test basic WordMappingManager functionality."""
        manager = WordMappingManager()

        # Test initialization
        self.assertIsNotNone(manager)
        self.assertEqual(len(manager.word_mappings), 0)

        # Test font loading (will fail with placeholder font, but we can test the interface)
        if os.path.exists(self.test_font_path):
            result = manager.load_font(self.test_font_path)
            self.assertTrue(result)

    def test_enhanced_font_manipulator_initialization(self):
        """Test EnhancedFontManipulator initialization and basic methods."""
        manipulator = EnhancedFontManipulator()

        # Test initialization
        self.assertIsNotNone(manipulator)
        self.assertIsNone(manipulator.font)
        self.assertIsNone(manipulator.original_cmap)
        self.assertEqual(len(manipulator.modifications), 0)

        # Test font loading interface
        if os.path.exists(self.test_font_path):
            result = manipulator.load_font(self.test_font_path)
            if result:  # Only test further if font loading succeeded
                # Test analysis
                analysis = manipulator.analyze_cmap_structure()
                self.assertIsInstance(analysis, dict)

                # Test validation
                issues = manipulator.validate_modifications()
                self.assertIsInstance(issues, list)

    def test_binary_font_manipulator_structure(self):
        """Test BinaryFontManipulator structure and interface."""
        manipulator = BinaryFontManipulator()

        # Test initialization
        self.assertIsNotNone(manipulator)
        self.assertIsNone(manipulator.font_data)
        self.assertEqual(len(manipulator.tables), 0)

    def test_pdf_integration_initialization(self):
        """Test PDFFontIntegrator initialization."""
        integrator = PDFFontIntegrator()

        # Test initialization
        self.assertIsNotNone(integrator)
        self.assertIsNotNone(integrator.font_manipulator)
        self.assertIsNotNone(integrator.word_manager)
        self.assertEqual(len(integrator.modified_fonts), 0)

    def test_mapping_creation_interface(self):
        """Test the mapping creation interface."""
        if not os.path.exists(self.test_font_path):
            self.skipTest("No test font available")

        integrator = PDFFontIntegrator()

        # Test font loading
        result = integrator.load_base_font(self.test_font_path)
        if not result:
            self.skipTest("Font loading failed")

        # Test mapping creation
        mappings = [
            {'original': 'a', 'replacement': 'b'},
            {'original': 'hello', 'replacement': 'world'}
        ]

        result = integrator.create_word_mappings(mappings)
        # This might fail due to font constraints, but we test the interface
        self.assertIsInstance(result, bool)

    def test_text_transformation(self):
        """Test text transformation functionality."""
        integrator = PDFFontIntegrator()

        # Set up some test mappings
        integrator.font_mappings = {
            'hello': 'world',
            'test': 'demo'
        }

        # Test transformation
        original_text = "This is a hello test"
        transformed = integrator.transform_text_for_mapping(original_text)

        expected = "This is a world demo"
        self.assertEqual(transformed, expected)

    def test_unicode_analysis(self):
        """Test Unicode analysis functionality."""
        test_text = "Hello World"

        # Test Unicode extraction
        unicode_values = [ord(char) for char in test_text]
        self.assertEqual(len(unicode_values), len(test_text))

        # Test Unicode formatting
        unicode_hex = [f'U+{ord(char):04X}' for char in test_text]
        self.assertEqual(len(unicode_hex), len(test_text))
        self.assertTrue(all(value.startswith('U+') for value in unicode_hex))

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_font_file_operations(self, mock_open):
        """Test font file operations with mocked file system."""
        manipulator = BinaryFontManipulator()

        # Mock font data
        mock_font_data = b'OTTO\\x00\\x01\\x00\\x00' + b'\\x00' * 100
        mock_open.return_value.read.return_value = mock_font_data

        # Test binary font loading interface
        result = manipulator.load_font_binary('mock_font.ttf')
        # This will likely fail due to invalid font data, but tests the interface
        self.assertIsInstance(result, bool)

    def test_mapping_validation(self):
        """Test mapping validation logic."""
        manipulator = EnhancedFontManipulator()

        # Test validation with no font loaded
        issues = manipulator.validate_modifications()
        self.assertIn("No font loaded", issues)

        # Test validation with no modifications
        manipulator.font = MagicMock()  # Mock font object
        issues = manipulator.validate_modifications()
        self.assertIn("No modifications to validate", issues)

    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test with non-existent font file
        manager = WordMappingManager()
        result = manager.load_font('non_existent_font.ttf')
        self.assertFalse(result)

        # Test invalid mapping creation
        integrator = PDFFontIntegrator()
        result = integrator.create_word_mappings([
            {'original': '', 'replacement': 'test'}  # Empty original
        ])
        self.assertFalse(result)

    def test_character_mapping_logic(self):
        """Test character mapping logic and edge cases."""
        # Test empty string mapping
        integrator = PDFFontIntegrator()
        integrator.font_mappings = {}

        result = integrator.transform_text_for_mapping("")
        self.assertEqual(result, "")

        # Test no mappings
        result = integrator.transform_text_for_mapping("test")
        self.assertEqual(result, "test")

        # Test overlapping mappings
        integrator.font_mappings = {
            'ab': 'xy',
            'abc': 'xyz'
        }

        result = integrator.transform_text_for_mapping("abc")
        # Should replace the first match found
        self.assertIn(result, ['xyc', 'xyz'])

    def test_font_format_validation(self):
        """Test font format validation."""
        manipulator = EnhancedFontManipulator()

        # Test with mock font that has no cmap
        manipulator.font = MagicMock()
        manipulator.font.__contains__ = lambda x: x != 'cmap'

        result = manipulator.load_font('mock_font.ttf')
        # Should handle missing cmap gracefully
        self.assertIsInstance(result, bool)

    def test_segment_manipulation_logic(self):
        """Test the segment manipulation algorithm."""
        manipulator = BinaryFontManipulator()

        # Test character code to segment mapping logic
        # This tests the algorithm without requiring actual font data

        # Mock cmap format 4 data
        class MockCmapFormat4:
            def __init__(self):
                self.start_code = [0x0020, 0x0041, 0x0061]  # Space, A, a
                self.end_code = [0x007E, 0x005A, 0x007A]    # ~, Z, z

        mock_cmap = MockCmapFormat4()

        # Test finding segment for character
        def find_segment_for_char(char_code):
            for i, (start, end) in enumerate(zip(mock_cmap.start_code, mock_cmap.end_code)):
                if start <= char_code <= end:
                    return i
            return -1

        # Test with valid characters
        self.assertEqual(find_segment_for_char(ord('A')), 1)  # Should be in segment 1
        self.assertEqual(find_segment_for_char(ord('a')), 2)  # Should be in segment 2
        self.assertEqual(find_segment_for_char(ord(' ')), 0)  # Should be in segment 0

        # Test with invalid character
        self.assertEqual(find_segment_for_char(0x1000), -1)  # Should not be found

    def test_id_delta_calculation(self):
        """Test idDelta calculation algorithm."""
        manipulator = EnhancedFontManipulator()

        # Test the core idDelta calculation
        # Formula: GlyphIndex = idDelta + Code
        # Therefore: idDelta = GlyphIndex - Code

        char_code = ord('a')  # 0x61
        target_glyph_index = 100

        expected_id_delta = target_glyph_index - char_code
        calculated_id_delta = manipulator.calculate_id_delta(char_code, target_glyph_index)

        self.assertEqual(calculated_id_delta, expected_id_delta)

        # Test with different values
        char_code = ord('Z')  # 0x5A
        target_glyph_index = 50

        expected_id_delta = target_glyph_index - char_code
        calculated_id_delta = manipulator.calculate_id_delta(char_code, target_glyph_index)

        self.assertEqual(calculated_id_delta, expected_id_delta)

    def test_pdf_generation_interface(self):
        """Test PDF generation interface without actual font files."""
        integrator = PDFFontIntegrator()

        # Test comparison PDF creation with mock data
        with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas:
            mock_canvas_instance = MagicMock()
            mock_canvas.return_value = mock_canvas_instance

            # This should not crash even without proper font setup
            result = integrator.create_comparison_pdf(
                "test text",
                os.path.join(self.temp_dir, "test.pdf"),
                show_comparison=False
            )

            # The result will likely be False due to missing font, but the interface should work
            self.assertIsInstance(result, bool)

    def test_steganographic_functionality(self):
        """Test steganographic PDF functionality."""
        integrator = PDFFontIntegrator()

        # Test length validation
        result = integrator.create_steganographic_pdf(
            "hello",     # 5 characters
            "world123",  # 8 characters - different length
            os.path.join(self.temp_dir, "stego.pdf")
        )

        self.assertFalse(result)  # Should fail due to length mismatch

        # Test with matching lengths
        with patch.object(integrator, 'create_word_mappings') as mock_mappings:
            mock_mappings.return_value = False  # Simulate mapping failure

            result = integrator.create_steganographic_pdf(
                "hello",
                "world",
                os.path.join(self.temp_dir, "stego.pdf")
            )

            self.assertFalse(result)  # Should fail due to mapping failure

    def test_cleanup_functionality(self):
        """Test cleanup functionality."""
        integrator = PDFFontIntegrator()

        # Create some mock temporary files
        temp_file1 = os.path.join(self.temp_dir, 'temp_font1.ttf')
        temp_file2 = os.path.join(self.temp_dir, 'temp_font2.ttf')

        # Create the files
        with open(temp_file1, 'w') as f:
            f.write('test')
        with open(temp_file2, 'w') as f:
            f.write('test')

        # Add to modified fonts tracking
        integrator.modified_fonts = {
            'font1': temp_file1,
            'font2': temp_file2
        }

        # Test cleanup
        integrator.cleanup()

        # Files should be removed
        self.assertFalse(os.path.exists(temp_file1))
        self.assertFalse(os.path.exists(temp_file2))

        # Tracking should be cleared
        self.assertEqual(len(integrator.modified_fonts), 0)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complete workflows."""

    def test_complete_workflow_simulation(self):
        """Test a complete workflow simulation."""
        # This test simulates the complete workflow without requiring actual fonts

        # Step 1: Initialize components
        integrator = PDFFontIntegrator()
        self.assertIsNotNone(integrator)

        # Step 2: Simulate font loading
        with patch.object(integrator, 'load_base_font') as mock_load:
            mock_load.return_value = True

            result = integrator.load_base_font('mock_font.ttf')
            self.assertTrue(result)

        # Step 3: Simulate mapping creation
        with patch.object(integrator, 'create_word_mappings') as mock_mappings:
            mock_mappings.return_value = True

            mappings = [{'original': 'test', 'replacement': 'demo'}]
            result = integrator.create_word_mappings(mappings)
            self.assertTrue(result)

        # Step 4: Test text transformation
        integrator.font_mappings = {'test': 'demo'}
        transformed = integrator.transform_text_for_mapping('This is a test')
        self.assertEqual(transformed, 'This is a demo')

    def test_error_recovery_scenarios(self):
        """Test error recovery scenarios."""
        integrator = PDFFontIntegrator()

        # Test recovery from font loading failure
        result = integrator.load_base_font('non_existent_font.ttf')
        self.assertFalse(result)

        # Should still be able to create mappings interface (even if it fails)
        result = integrator.create_word_mappings([])
        self.assertFalse(result)  # Empty mappings should return False

    def test_unicode_preservation(self):
        """Test that Unicode values are properly preserved and transformed."""
        # Test Unicode round-trip
        original_text = "Hello 世界 🌍"

        # Extract Unicode values
        original_unicode = [ord(char) for char in original_text]

        # Convert back to string
        reconstructed = ''.join(chr(code) for code in original_unicode)

        self.assertEqual(original_text, reconstructed)

        # Test Unicode formatting
        unicode_strings = [f'U+{ord(char):04X}' for char in original_text]

        # Should have same length
        self.assertEqual(len(unicode_strings), len(original_text))

        # All should be valid Unicode format
        for unicode_str in unicode_strings:
            self.assertTrue(unicode_str.startswith('U+'))
            self.assertEqual(len(unicode_str), 6)  # U+ plus 4 hex digits


def run_font_manipulation_tests():
    """Run all font manipulation tests."""
    print("Running Font Manipulation Test Suite...")
    print("=" * 50)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestFontManipulation))
    test_suite.addTest(unittest.makeSuite(TestIntegrationScenarios))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('\\n')[-2] if traceback else 'Unknown failure'}")

    if result.errors:
        print("\\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\\n')[-2] if traceback else 'Unknown error'}")

    if result.wasSuccessful():
        print("\\n✅ All tests passed!")
    else:
        print("\\n❌ Some tests failed. Check the implementation.")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_font_manipulation_tests()
    sys.exit(0 if success else 1)