"""
Main entry point for PerfectCV Backend
Runs Flask server with full CV processing, authentication, and chatbot functionality
"""
import logging
from app import create_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    print("="*70)
    print("Starting PerfectCV Backend Server (Flask)")
    print("="*70)
    print("Server: http://localhost:8000")
    print("Health Check: http://localhost:8000/health")
    print("="*70)
    print("Available endpoints:")
    print("  - Authentication: /auth/login, /auth/register")
    print("  - CV Upload: /api/upload-cv")
    print("  - File Management: /api/files")
    print("  - Chatbot: /api/chatbot/*")
    print("="*70)
    
    app = create_app()
    
    # Fix for Windows WinError 10038 during auto-reload
    # Disable reloader on Windows to prevent socket errors
    import os
    if os.name == 'nt':  # Windows
        app.run(
            host="0.0.0.0",
            port=8000,
            debug=True,
            use_reloader=False,  # Disable reloader to prevent WinError 10038
            threaded=True
        )
    else:  # Linux/Mac
        app.run(
            host="0.0.0.0",
            port=8000,
            debug=True
        )