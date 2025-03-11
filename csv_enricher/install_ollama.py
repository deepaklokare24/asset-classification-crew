#!/usr/bin/env python
"""
Installation script for Ollama.
This script checks if Ollama is installed and installs the required models.
"""

import subprocess
import sys
import platform
import os
import time
import re

# Required versions
REQUIRED_OLLAMA_VERSION = "0.4.7"

def run_command(command, shell=True):
    """Run a shell command and print output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=shell, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0, result.stdout, result.stderr

def check_ollama_installed():
    """Check if Ollama is installed and get its version"""
    try:
        result = subprocess.run(["ollama", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            # Extract version from output
            version_match = re.search(r'(\d+\.\d+\.\d+)', result.stdout)
            if version_match:
                installed_version = version_match.group(1)
                print(f"Ollama version {installed_version} is installed.")
                return True, installed_version
            return True, "unknown"
        return False, None
    except FileNotFoundError:
        return False, None

def check_python_package_version():
    """Check if the ollama Python package is installed with the correct version"""
    try:
        import ollama
        installed_version = ollama.__version__
        print(f"Ollama Python package version {installed_version} is installed.")
        if installed_version == REQUIRED_OLLAMA_VERSION:
            return True
        else:
            print(f"Warning: Installed ollama Python package version {installed_version} does not match required version {REQUIRED_OLLAMA_VERSION}.")
            print("Attempting to update the package...")
            success, _, _ = run_command(f"{sys.executable} -m pip install ollama=={REQUIRED_OLLAMA_VERSION}")
            return success
    except ImportError:
        print("Ollama Python package is not installed.")
        print("Installing the package...")
        success, _, _ = run_command(f"{sys.executable} -m pip install ollama=={REQUIRED_OLLAMA_VERSION}")
        return success

def check_langchain_anthropic():
    """Check if the langchain-anthropic package is installed"""
    try:
        import langchain_anthropic
        print("langchain-anthropic package is installed.")
        return True
    except ImportError:
        print("langchain-anthropic package is not installed.")
        print("Installing the package...")
        success, _, _ = run_command(f"{sys.executable} -m pip install langchain-anthropic")
        return success

def check_langchain_ollama():
    """Check if the langchain-ollama package is installed"""
    try:
        import langchain_ollama
        print("langchain-ollama package is installed.")
        return True
    except ImportError:
        print("langchain-ollama package is not installed.")
        print("Installing the package...")
        success, _, _ = run_command(f"{sys.executable} -m pip install langchain-ollama")
        return success

def check_litellm():
    """Check if the litellm package is installed"""
    try:
        import litellm
        print("litellm package is installed.")
        return True
    except ImportError:
        print("litellm package is not installed.")
        print("Installing the package...")
        success, _, _ = run_command(f"{sys.executable} -m pip install litellm")
        return success

def install_ollama():
    """Install Ollama based on the operating system"""
    system = platform.system().lower()
    
    print(f"Installing Ollama for {system}...")
    
    if system == "darwin":  # macOS
        success, _, _ = run_command("curl -fsSL https://ollama.com/install.sh | sh")
        return success
    elif system == "linux":
        success, _, _ = run_command("curl -fsSL https://ollama.com/install.sh | sh")
        return success
    elif system == "windows":
        print("For Windows, please download and install Ollama from: https://ollama.com/download/windows")
        print("After installation, please restart this script.")
        return False
    else:
        print(f"Unsupported operating system: {system}")
        print("Please install Ollama manually from: https://ollama.com")
        return False

def start_ollama_service():
    """Start the Ollama service"""
    system = platform.system().lower()
    
    if system == "darwin" or system == "linux":
        # Check if Ollama is already running
        result = subprocess.run(["pgrep", "ollama"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Ollama service is already running.")
            return True
        
        print("Starting Ollama service...")
        # Start Ollama in the background
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Wait for the service to start
        time.sleep(5)
        return True
    elif system == "windows":
        print("For Windows, please start the Ollama service manually.")
        print("After starting the service, press Enter to continue.")
        input()
        return True
    else:
        print(f"Unsupported operating system: {system}")
        return False

def pull_embedding_model():
    """Pull the embedding model"""
    print("Pulling the nomic-embed-text model...")
    success, stdout, stderr = run_command("ollama pull nomic-embed-text")
    
    if not success:
        print("Failed to pull the nomic-embed-text model.")
        print("Checking if the model is already available...")
        
        # Check if the model is already available
        list_success, list_stdout, _ = run_command("ollama list")
        if list_success and "nomic-embed-text" in list_stdout:
            print("The nomic-embed-text model is already available.")
            return True
        return False
    
    return True

def main():
    """Main function"""
    print("Checking if Ollama is installed...")
    
    ollama_installed, installed_version = check_ollama_installed()
    
    if not ollama_installed:
        print("Ollama is not installed. Installing now...")
        if not install_ollama():
            print("Failed to install Ollama. Please install it manually from: https://ollama.com")
            return 1
        print("Ollama installed successfully!")
    
    # Check Python package version
    if not check_python_package_version():
        print(f"Failed to install/update the ollama Python package to version {REQUIRED_OLLAMA_VERSION}.")
        print(f"Please run 'pip install ollama=={REQUIRED_OLLAMA_VERSION}' manually.")
        return 1
    
    # Check langchain-anthropic package
    if not check_langchain_anthropic():
        print("Failed to install the langchain-anthropic package.")
        print("Please run 'pip install langchain-anthropic' manually.")
        return 1
    
    # Check langchain-ollama package
    if not check_langchain_ollama():
        print("Failed to install the langchain-ollama package.")
        print("Please run 'pip install langchain-ollama' manually.")
        return 1
    
    # Check litellm package
    if not check_litellm():
        print("Failed to install the litellm package.")
        print("Please run 'pip install litellm' manually.")
        return 1
    
    if not start_ollama_service():
        print("Failed to start Ollama service. Please start it manually.")
        return 1
    
    if not pull_embedding_model():
        print("Failed to pull the embedding model. Please run 'ollama pull nomic-embed-text' manually.")
        return 1
    
    print("\nOllama setup completed successfully!")
    print("You can now run the application with: python run.py")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 