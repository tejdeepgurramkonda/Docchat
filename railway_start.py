#!/usr/bin/env python3
"""
Startup script for ChatDocs AI on Railway
Handles port configuration and starts the uvicorn server
"""
import os
import sys
import subprocess

def main():
    # Get port from environment variable, default to 8000
    port = os.getenv("PORT", "8000")
    
    print(f"Starting ChatDocs AI on port {port}")
    
    # Build the command
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app:app", 
        "--host", "0.0.0.0", 
        "--port", port,
        "--workers", "1"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Execute the command
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
