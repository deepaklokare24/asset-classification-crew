import os
import subprocess
import sys
import time
import argparse
import signal
import shutil
from typing import List, Optional

def find_executable(name: str) -> Optional[str]:
    """Find the path to an executable"""
    return shutil.which(name)

def start_backend():
    """Start the backend server"""
    print("Starting backend server...")
    backend_cmd = [sys.executable, "backend/main.py"]
    backend_process = subprocess.Popen(
        backend_cmd,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    return backend_process

def start_frontend():
    """Start the frontend application"""
    print("Starting frontend application...")
    frontend_cmd = [sys.executable, "-m", "streamlit", "run", "frontend/app.py"]
    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    return frontend_process

def handle_shutdown(processes: List[subprocess.Popen]):
    """Shutdown all processes"""
    print("\nShutting down...")
    for process in processes:
        if process.poll() is None:  # If process is still running
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    print("All processes terminated.")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="CSV Data Enrichment Application")
    parser.add_argument("--backend-only", action="store_true", help="Start only the backend server")
    parser.add_argument("--frontend-only", action="store_true", help="Start only the frontend application")
    args = parser.parse_args()
    
    # Check for required executables
    if not find_executable("python") and not find_executable("python3"):
        print("Error: Python executable not found.")
        return 1
    
    if not args.backend_only and not find_executable("streamlit"):
        print("Error: Streamlit not found. Please install it with 'pip install streamlit'.")
        return 1
    
    processes = []
    
    try:
        # Start backend if requested or if running both
        if not args.frontend_only:
            backend_process = start_backend()
            processes.append(backend_process)
            # Wait a moment for the backend to start
            time.sleep(2)
        
        # Start frontend if requested or if running both
        if not args.backend_only:
            frontend_process = start_frontend()
            processes.append(frontend_process)
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, lambda sig, frame: handle_shutdown(processes))
        signal.signal(signal.SIGTERM, lambda sig, frame: handle_shutdown(processes))
        
        # Wait for processes to complete
        for process in processes:
            process.wait()
        
    except KeyboardInterrupt:
        handle_shutdown(processes)
    except Exception as e:
        print(f"Error: {e}")
        handle_shutdown(processes)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 