#!/usr/bin/env python3
"""
Launcher script for the Flask Web Application
This script maintains backward compatibility while using the new organized folder structure
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the actual Flask app
from web.app import app

if __name__ == "__main__":
    print("🚀 Starting PDF Metadata Extraction Web App...")
    print("📱 Access the app at: http://localhost:5001")
    print("📁 Upload folder: uploads/")
    print("🔧 Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
