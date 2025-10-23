#!/usr/bin/env python3
"""
Quick fix script to set DEBUG=True for development
"""
import os
import subprocess
import sys

def fix_debug_mode():
    """Set DEBUG=True and run the server"""
    print("Setting DEBUG=True for development...")
    
    # Set environment variable
    os.environ['DJANGO_DEBUG'] = 'True'
    
    print("Starting Django server with DEBUG=True...")
    print("This will use StaticFilesStorage instead of ManifestStaticFilesStorage")
    print("=" * 60)
    
    # Run the server
    try:
        subprocess.run([sys.executable, 'manage.py', 'runserver', '127.0.0.1:8001'], 
                      env=os.environ.copy())
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    fix_debug_mode()
