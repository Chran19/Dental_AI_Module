"""
Start the FastAPI server for Image Analysis testing
Launches on http://localhost:8000
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_server():
    """Start the FastAPI server"""
    print("=" * 80)
    print("  DENTAL AI MODULE - FASTAPI SERVER STARTUP")
    print("=" * 80)
    
    # Check if backend directory exists
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("[ERROR] backend/ directory not found")
        print("Make sure you're running this from the Dental_AI_Module root directory")
        sys.exit(1)
    
    # Set environment
    env = os.environ.copy()
    env['PYTHONPATH'] = str(backend_dir)
    
    # Start server
    print("\n[STARTING] FastAPI server...")
    print("  Command: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("  Location: backend/app/main.py")
    print("  Docs: http://localhost:8000/docs")
    print("\n" + "=" * 80 + "\n")
    
    try:
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Start uvicorn
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app.main:app", 
             "--reload", "--host", "0.0.0.0", "--port", "8000"],
            env=env,
            cwd="."
        )
    
    except KeyboardInterrupt:
        print("\n\n[STOPPED] Server stopped by user")
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    start_server()
