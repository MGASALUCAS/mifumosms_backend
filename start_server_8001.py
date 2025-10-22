#!/usr/bin/env python3
"""
Start Django server on port 8001 for testing
"""

import os
import sys
import subprocess

def start_server():
    print("🚀 Starting Django server on port 8001...")
    print("=" * 50)
    
    try:
        # Start the Django development server on port 8001
        subprocess.run([
            sys.executable, 
            "manage.py", 
            "runserver", 
            "8001",
            "--settings=mifumo.settings"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    start_server()
