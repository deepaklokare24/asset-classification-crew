#!/usr/bin/env python
"""
Run script for the CSV Enrichment application.
This script starts both the backend and frontend servers.
"""

import os
import sys
import subprocess
import time
import signal
import argparse

def run_backend():
    """Start the backend server"""
    print("Starting backend server...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    backend_process = subprocess.Popen(
        backend_cmd,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    return backend_process

def run_frontend():
    """Start the frontend application"""
    print("Starting frontend application...")
    frontend_cmd = [sys.executable, "-m", "streamlit", "run", "frontend/app.py"]
    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    return frontend_process

def handle_shutdown(processes):
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
    
    processes = []
    
    try:
        # Start backend if requested or if running both
        if not args.frontend_only:
            backend_process = run_backend()
            processes.append(backend_process)
            # Wait a moment for the backend to start
            time.sleep(2)
        
        # Start frontend if requested or if running both
        if not args.backend_only:
            frontend_process = run_frontend()
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