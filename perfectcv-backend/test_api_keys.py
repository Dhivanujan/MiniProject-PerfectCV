#!/usr/bin/env python
"""Test script to verify API keys are loaded correctly."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Test 1: Check environment loading
print("=" * 60)
print("TEST 1: Environment Variables")
print("=" * 60)
from dotenv import load_dotenv
load_dotenv('.env')
print(f"✓ GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY')[:20]}..." if os.getenv('GOOGLE_API_KEY') else "✗ GOOGLE_API_KEY not found")
print(f"✓ GROQ_API_KEY: {os.getenv('GROQ_API_KEY')[:20]}..." if os.getenv('GROQ_API_KEY') else "✗ GROQ_API_KEY not found")
print(f"✓ OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')[:20]}..." if os.getenv('OPENAI_API_KEY') else "ℹ OPENAI_API_KEY not configured (optional)")

# Test 2: Check Config class
print("\n" + "=" * 60)
print("TEST 2: Config Class")
print("=" * 60)
from config.config import Config
print(f"✓ Config.API_KEY: {Config.API_KEY[:20]}..." if Config.API_KEY else "✗ Config.API_KEY not set")
print(f"✓ Config.GROQ_API_KEY: {Config.GROQ_API_KEY[:20]}..." if Config.GROQ_API_KEY else "✗ Config.GROQ_API_KEY not set")
print(f"✓ Config.OPENAI_API_KEY: {Config.OPENAI_API_KEY[:20]}..." if Config.OPENAI_API_KEY else "ℹ Config.OPENAI_API_KEY not set (optional)")

# Test 3: Test Gemini setup
print("\n" + "=" * 60)
print("TEST 3: Gemini AI Setup")
print("=" * 60)
try:
    from app.utils.ai_utils import setup_gemini
    result = setup_gemini()
    if result:
        print("✓ Gemini AI configured successfully!")
    else:
        print("✗ Gemini AI configuration failed")
except Exception as e:
    print(f"✗ Error setting up Gemini: {e}")

# Test 4: Test optimize_cv function
print("\n" + "=" * 60)
print("TEST 4: CV Optimization Function")
print("=" * 60)
try:
    from app.utils.cv_utils import optimize_cv
    
    test_cv = """
    John Doe
    Email: john.doe@example.com
    Phone: +1-555-1234
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with 5 years of Python development.
    
    SKILLS
    Python, JavaScript, React, Flask, MongoDB
    
    EXPERIENCE
    Senior Developer at Tech Corp (2020-2023)
    - Developed web applications
    - Led team of 5 developers
    """
    
    print("Testing optimize_cv with AI enabled...")
    result = optimize_cv(test_cv, use_ai=True, job_domain="software_engineering")
    
    if result and isinstance(result, dict):
        print(f"✓ optimize_cv returned successfully")
        print(f"  - Keys: {', '.join(list(result.keys())[:10])}")
        print(f"  - ATS Score: {result.get('ats_score', 'N/A')}")
        print(f"  - AI Enhanced: {result.get('ai_enhanced', False)}")
        print(f"  - Optimized text length: {len(result.get('optimized_text', ''))} chars")
    else:
        print("✗ optimize_cv returned unexpected result")
        
except Exception as e:
    print(f"✗ Error testing optimize_cv: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TESTS COMPLETE")
print("=" * 60)
