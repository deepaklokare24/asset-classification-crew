#!/usr/bin/env python3
"""
Installation script for Hugging Face models.
This script downloads and caches the Hugging Face models locally.
"""

import os
import sys
import subprocess
import importlib.util
from typing import List, Optional

def check_package_installed(package_name: str) -> bool:
    """Check if a package is installed."""
    return importlib.util.find_spec(package_name) is not None

def install_package(package_name: str) -> bool:
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def check_sentence_transformers() -> bool:
    """Check if sentence-transformers is installed, install if not."""
    if not check_package_installed("sentence_transformers"):
        print("sentence-transformers not found. Installing...")
        return install_package("sentence-transformers")
    return True

def check_transformers() -> bool:
    """Check if transformers is installed, install if not."""
    if not check_package_installed("transformers"):
        print("transformers not found. Installing...")
        return install_package("transformers")
    return True

def check_torch() -> bool:
    """Check if torch is installed, install if not."""
    if not check_package_installed("torch"):
        print("torch not found. Installing...")
        return install_package("torch")
    return True

def check_langchain_huggingface() -> bool:
    """Check if langchain-huggingface is installed, install if not."""
    if not check_package_installed("langchain_huggingface"):
        print("langchain-huggingface not found. Installing...")
        return install_package("langchain-huggingface")
    return True

def download_model(model_name: str) -> bool:
    """Download and cache a Hugging Face model."""
    try:
        print(f"Downloading model: {model_name}")
        from sentence_transformers import SentenceTransformer
        # This will download and cache the model
        model = SentenceTransformer(model_name)
        print(f"Model {model_name} downloaded and cached successfully.")
        return True
    except Exception as e:
        print(f"Error downloading model {model_name}: {e}")
        return False

def main():
    """Main function to install Hugging Face models."""
    print("===== Hugging Face Model Installation =====")
    
    # Check and install required packages
    packages_ok = all([
        check_sentence_transformers(),
        check_transformers(),
        check_torch(),
        check_langchain_huggingface()
    ])
    
    if not packages_ok:
        print("Failed to install required packages. Please install them manually.")
        sys.exit(1)
    
    # Download and cache models
    models = [
        "sentence-transformers/all-MiniLM-L6-v2",  # Lightweight model for semantic search
        # Add more models here if needed
    ]
    
    for model in models:
        if not download_model(model):
            print(f"Failed to download model: {model}")
            sys.exit(1)
    
    print("\nAll Hugging Face models installed successfully!")
    print("\nYou can now use Hugging Face embeddings in your CSV enrichment application.")

if __name__ == "__main__":
    main() 