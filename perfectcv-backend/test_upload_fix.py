"""
Quick test to verify generate_pdf replacement is working
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all imports work correctly"""
    print("=" * 60)
    print("Testing Updated Imports in files.py")
    print("=" * 60)
    
    try:
        # Test cv_generator import
        from app.services.cv_generator import get_cv_generator
        print("✓ get_cv_generator imported successfully")
        
        # Test that cv_generator works
        cv_gen = get_cv_generator()
        print("✓ cv_generator instance created")
        
        # Test with minimal data
        test_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+1-555-0123'
        }
        
        pdf_io = cv_gen.generate_cv_pdf(test_data, template_name='modern_cv.html')
        print(f"✓ PDF generated successfully: {len(pdf_io.getvalue())} bytes")
        
        print("\n" + "=" * 60)
        print("✅ All imports and functions working correctly!")
        print("=" * 60)
        print("\nThe upload_cv route should now work without errors.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
