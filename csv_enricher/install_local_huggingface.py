#!/usr/bin/env python3
"""
Installation script for using locally downloaded Hugging Face models.
This script sets up the environment to use pre-downloaded models.
"""

import os
import sys
import shutil
import importlib.util
import subprocess
from typing import List, Optional

# Define the model name and local path
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_MODEL_DIR = os.path.join("models", "sentence-transformers", "all-MiniLM-L6-v2")

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

def check_required_packages() -> bool:
    """Check if required packages are installed, install if not."""
    packages = [
        "sentence-transformers",
        "transformers",
        "torch",
        "langchain-huggingface"
    ]
    
    all_installed = True
    for package in packages:
        if not check_package_installed(package.replace("-", "_")):
            print(f"{package} not found. Installing...")
            if not install_package(package):
                print(f"Failed to install {package}")
                all_installed = False
    
    return all_installed

def setup_local_model(model_dir: str = DEFAULT_MODEL_DIR) -> bool:
    """Set up the environment to use a locally downloaded model."""
    try:
        # Create the Hugging Face cache directory if it doesn't exist
        home_dir = os.path.expanduser("~")
        cache_dir = os.path.join(home_dir, ".cache", "huggingface", "hub")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create a symlink or copy the model to the cache directory
        model_cache_dir = os.path.join(cache_dir, "models--sentence-transformers--all-MiniLM-L6-v2")
        os.makedirs(model_cache_dir, exist_ok=True)
        
        # Create snapshots directory
        snapshots_dir = os.path.join(model_cache_dir, "snapshots")
        os.makedirs(snapshots_dir, exist_ok=True)
        
        # Create a snapshot directory with a hash (this is a placeholder)
        snapshot_hash = "abcdef1234567890"  # This would normally be a git hash
        snapshot_dir = os.path.join(snapshots_dir, snapshot_hash)
        
        if os.path.exists(snapshot_dir):
            print(f"Model snapshot already exists at {snapshot_dir}")
        else:
            print(f"Setting up model in {snapshot_dir}")
            os.makedirs(snapshot_dir, exist_ok=True)
            
            # Copy model files to the snapshot directory
            if os.path.exists(model_dir):
                for item in os.listdir(model_dir):
                    src = os.path.join(model_dir, item)
                    dst = os.path.join(snapshot_dir, item)
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
                print(f"Copied model files from {model_dir} to {snapshot_dir}")
            else:
                print(f"Error: Model directory {model_dir} not found")
                return False
        
        # Create a refs directory and add a pointer to the snapshot
        refs_dir = os.path.join(model_cache_dir, "refs")
        os.makedirs(refs_dir, exist_ok=True)
        
        # Create a main file pointing to the snapshot
        with open(os.path.join(refs_dir, "main"), "w") as f:
            f.write(snapshot_hash)
        
        print(f"Model setup complete. The model is now available at {model_cache_dir}")
        return True
    
    except Exception as e:
        print(f"Error setting up local model: {e}")
        return False

def verify_model_works() -> bool:
    """Verify that the model can be loaded and used."""
    try:
        print("Verifying model can be loaded...")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MODEL_NAME)
        
        # Test the model with a simple example
        test_sentences = ["This is a test sentence.", "Another test sentence."]
        embeddings = model.encode(test_sentences)
        
        print(f"Model loaded successfully and generated embeddings of shape {embeddings.shape}")
        return True
    except Exception as e:
        print(f"Error verifying model: {e}")
        return False

def main():
    """Main function to set up local Hugging Face models."""
    print("===== Local Hugging Face Model Setup =====")
    
    # Check and install required packages
    if not check_required_packages():
        print("Failed to install required packages. Please install them manually.")
        sys.exit(1)
    
    # Get model directory from command line argument or use default
    model_dir = DEFAULT_MODEL_DIR
    if len(sys.argv) > 1:
        model_dir = sys.argv[1]
    
    # Setup local model
    if not setup_local_model(model_dir):
        print("Failed to set up local model.")
        sys.exit(1)
    
    # Verify model works
    if not verify_model_works():
        print("Failed to verify model.")
        sys.exit(1)
    
    print("\nLocal Hugging Face model setup successfully!")
    print("\nYou can now use Hugging Face embeddings in your CSV enrichment application.")
    print(f"\nIf you need to use a different model directory, run: python {sys.argv[0]} /path/to/model")

if __name__ == "__main__":
    main() 