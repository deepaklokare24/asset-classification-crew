#!/usr/bin/env python3
"""
Script to download Hugging Face models for offline use.
Run this script on a machine with internet access to download the models.
"""

import os
import sys
import shutil
import zipfile
import argparse
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

def check_required_packages() -> bool:
    """Check if required packages are installed, install if not."""
    packages = [
        "sentence-transformers",
        "transformers",
        "torch",
        "requests"
    ]
    
    all_installed = True
    for package in packages:
        if not check_package_installed(package.replace("-", "_")):
            print(f"{package} not found. Installing...")
            if not install_package(package):
                print(f"Failed to install {package}")
                all_installed = False
    
    return all_installed

def download_model(model_name: str, output_dir: str) -> bool:
    """Download a Hugging Face model for offline use."""
    try:
        print(f"Downloading model: {model_name}")
        
        # Import here to ensure the package is installed
        from sentence_transformers import SentenceTransformer
        
        # This will download the model to the Hugging Face cache
        model = SentenceTransformer(model_name)
        
        # Get the model directory from the cache
        home_dir = os.path.expanduser("~")
        cache_dir = os.path.join(home_dir, ".cache", "huggingface", "hub")
        
        # The model directory follows a specific naming convention
        model_dir_name = f"models--{model_name.replace('/', '--')}"
        model_cache_dir = os.path.join(cache_dir, model_dir_name)
        
        if not os.path.exists(model_cache_dir):
            print(f"Error: Model cache directory not found at {model_cache_dir}")
            return False
        
        # Create the output directory
        model_output_dir = os.path.join(output_dir, model_name.replace("/", os.sep))
        os.makedirs(model_output_dir, exist_ok=True)
        
        # Copy the model files to the output directory
        print(f"Copying model files to {model_output_dir}")
        
        # Find the latest snapshot
        snapshots_dir = os.path.join(model_cache_dir, "snapshots")
        if not os.path.exists(snapshots_dir):
            print(f"Error: Snapshots directory not found at {snapshots_dir}")
            return False
        
        # Get the main ref
        refs_dir = os.path.join(model_cache_dir, "refs")
        main_ref_file = os.path.join(refs_dir, "main")
        
        if os.path.exists(main_ref_file):
            with open(main_ref_file, "r") as f:
                snapshot_hash = f.read().strip()
        else:
            # If no main ref, use the first snapshot
            snapshots = os.listdir(snapshots_dir)
            if not snapshots:
                print(f"Error: No snapshots found in {snapshots_dir}")
                return False
            snapshot_hash = snapshots[0]
        
        snapshot_dir = os.path.join(snapshots_dir, snapshot_hash)
        
        # Copy all files from the snapshot directory
        for item in os.listdir(snapshot_dir):
            src = os.path.join(snapshot_dir, item)
            dst = os.path.join(model_output_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        
        print(f"Model files copied to {model_output_dir}")
        
        # Create a zip file for easy transfer
        zip_file = os.path.join(output_dir, f"{model_name.replace('/', '_')}.zip")
        print(f"Creating zip file: {zip_file}")
        
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(model_output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)
        
        print(f"Zip file created: {zip_file}")
        print(f"Model downloaded and packaged successfully.")
        
        # Test the model
        test_sentences = ["This is a test sentence.", "Another test sentence."]
        embeddings = model.encode(test_sentences)
        print(f"Model tested successfully. Generated embeddings of shape {embeddings.shape}")
        
        return True
    except Exception as e:
        print(f"Error downloading model: {e}")
        return False

def main():
    """Main function to download Hugging Face models."""
    parser = argparse.ArgumentParser(description="Download Hugging Face models for offline use")
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2", 
                        help="Model name (default: sentence-transformers/all-MiniLM-L6-v2)")
    parser.add_argument("--output", default="models", 
                        help="Output directory (default: models)")
    args = parser.parse_args()
    
    print("===== Hugging Face Model Download =====")
    
    # Check and install required packages
    if not check_required_packages():
        print("Failed to install required packages. Please install them manually.")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Download the model
    if not download_model(args.model, args.output):
        print("Failed to download model.")
        sys.exit(1)
    
    print("\nModel download complete!")
    print(f"\nThe model has been downloaded to: {args.output}")
    print(f"A zip file has been created for easy transfer.")
    print("\nTo use this model in an offline environment:")
    print(f"1. Copy the entire '{args.model.replace('/', os.sep)}' directory to your offline machine")
    print(f"2. Run: python install_local_huggingface.py {args.model.replace('/', os.sep)}")

if __name__ == "__main__":
    main() 