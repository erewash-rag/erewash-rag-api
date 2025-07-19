#!/usr/bin/env python3
"""
Local development server for Erewash RAG API
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Flask if not already installed"""
    try:
        import flask
        print("✓ Flask is already installed")
    except ImportError:
        print("Installing Flask...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Flask installed successfully")

def run_server():
    """Run the Flask development server"""
    print("Starting Erewash RAG API on http://localhost:8080")
    print("Available endpoints:")
    print("  GET http://localhost:8080/articles")
    print("  GET http://localhost:8080/articles/{id}")
    print("  GET http://localhost:8080/health")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run the Flask app
    subprocess.run([sys.executable, "app.py"])

if __name__ == "__main__":
    install_requirements()
    run_server() 