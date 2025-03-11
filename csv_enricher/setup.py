import os
import shutil
import sys

def setup():
    """Set up the application by copying the source CSV file"""
    print("Setting up CSV Enricher application...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(current_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Create progress directory if it doesn't exist
    progress_dir = os.path.join(data_dir, "progress")
    os.makedirs(progress_dir, exist_ok=True)
    
    # Check if source CSV file exists in the parent directory
    source_csv = os.path.join(os.path.dirname(current_dir), "pricerunner_aggregate.csv")
    
    if not os.path.exists(source_csv):
        print(f"Error: Source CSV file not found at {source_csv}")
        print("Please place the pricerunner_aggregate.csv file in the parent directory.")
        return 1
    
    # Copy the source CSV file to the data directory
    target_csv = os.path.join(data_dir, "pricerunner_aggregate.csv")
    
    try:
        shutil.copy2(source_csv, target_csv)
        print(f"Source CSV file copied to {target_csv}")
    except Exception as e:
        print(f"Error copying source CSV file: {e}")
        return 1
    
    print("Setup completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(setup()) 