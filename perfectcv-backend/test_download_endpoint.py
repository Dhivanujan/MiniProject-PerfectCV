"""
Test the download-optimized-cv endpoint
"""

import requests
import json

# Test data that mimics what the frontend sends
test_data = {
    "structured_cv": {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "123-456-7890",
        "summary": "Experienced software developer",
        "skills": ["Python", "JavaScript", "React"],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "dates": "2020 - Present",
                "description": "Developed web applications",
                "points": ["Built features", "Fixed bugs"]
            }
        ],
        "education": [
            {
                "degree": "BS Computer Science",
                "school": "University",
                "year": "2020"
            }
        ]
    },
    "optimized_text": "# Test CV\n\nThis is test content",
    "filename": "Test_CV.pdf"
}

# First, try without authentication (should fail with 401)
print("Test 1: Without authentication (expect 401)...")
try:
    response = requests.post(
        "http://localhost:5000/api/download-optimized-cv",
        json=test_data,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Correctly requires authentication")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*50 + "\n")

# Test 2: With session (requires manual login first)
print("Test 2: With session (you must be logged in via browser first)...")
print("To test with authentication:")
print("1. Log in via browser at http://localhost:5173")
print("2. Open DevTools (F12) > Application > Cookies")
print("3. Copy the 'session' cookie value")
print("4. Run this script with SESSION_COOKIE environment variable:")
print("   $env:SESSION_COOKIE='<your_session_cookie>' ; python test_download_endpoint.py")

import os
session_cookie = os.environ.get('SESSION_COOKIE')
if session_cookie:
    print(f"\nUsing session cookie: {session_cookie[:20]}...")
    cookies = {'session': session_cookie}
    
    try:
        response = requests.post(
            "http://localhost:5000/api/download-optimized-cv",
            json=test_data,
            cookies=cookies,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Download successful!")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            print(f"Content-Length: {len(response.content)} bytes")
            
            # Save to file
            with open("test_download.pdf", "wb") as f:
                f.write(response.content)
            print("Saved to: test_download.pdf")
        else:
            print(f"❌ Failed: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("\nNo session cookie provided. Skipping authenticated test.")

print("\n" + "="*50 + "\n")
print("Test 3: Check if endpoint exists...")
try:
    # Try OPTIONS request to see if endpoint is registered
    response = requests.options(
        "http://localhost:5000/api/download-optimized-cv",
        timeout=5
    )
    print(f"OPTIONS status: {response.status_code}")
    print(f"Allowed methods: {response.headers.get('Allow', 'Not specified')}")
except Exception as e:
    print(f"Error: {e}")
