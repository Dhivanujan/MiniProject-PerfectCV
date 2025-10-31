"""Small script to test the upload-cv endpoint using Flask test client.

Usage: run from the backend folder:
    python tools/test_upload.py

This script will:
- create the Flask app
- register a temporary user
- log in the user
- upload a small sample CV (text) as multipart/form-data
- print the JSON response

Note: This uses the app's test client and does not require running the server.
"""

import io
import json
from app import create_app

app = create_app()

SAMPLE_EMAIL = "test_upload@example.com"
SAMPLE_PASS = "Password123!"

with app.app_context():
    client = app.test_client()

    # Try to register the user (ignore if already exists)
    res = client.post('/auth/register', json={'email': SAMPLE_EMAIL, 'password': SAMPLE_PASS})
    print('register:', res.status_code, res.get_json())

    # Login
    res = client.post('/auth/login', json={'email': SAMPLE_EMAIL, 'password': SAMPLE_PASS})
    print('login:', res.status_code, res.get_json())

    # Prepare sample CV content
    sample_cv = b"""John Doe\nemail@example.com | +1-555-555-5555\n\nPROFESSIONAL SUMMARY\nExperienced engineer...\n\nEXPERIENCE\nAcme Corp (2019-2022)\n- Developed features in Python\n- Improved performance by 30%\n\nSKILLS\nPython, SQL, AWS\n"""

    data = {
        'cv_file': (io.BytesIO(sample_cv), 'sample_cv.pdf'),
        'job_domain': 'software'
    }

    # Upload CV (test client maintains cookies)
    res = client.post('/api/upload-cv', data=data, content_type='multipart/form-data')
    print('upload:', res.status_code)
    try:
        print(json.dumps(res.get_json(), indent=2))
    except Exception:
        print('No JSON response')
