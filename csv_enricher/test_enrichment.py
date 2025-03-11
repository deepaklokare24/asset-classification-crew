#!/usr/bin/env python3
"""
Test script for CSV enrichment process.
This script runs the CSV enrichment process on the sample input file and verifies the results.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from agents.csv_enrichment_crew import CSVEnrichmentCrew

def test_enrichment():
    """Test the CSV enrichment process with the sample input file."""
    print("Starting CSV enrichment test...")
    
    # Define paths
    source_csv_path = os.path.join("data", "pricerunner_aggregate.csv")
    input_csv_path = os.path.join("data", "sample_input.csv")
    
    # Check if source CSV exists
    if not os.path.exists(source_csv_path):
        print(f"Error: Source CSV file not found at {source_csv_path}")
        print("Please run setup.py first to copy the source CSV file.")
        return False
    
    # Check if input CSV exists
    if not os.path.exists(input_csv_path):
        print(f"Error: Input CSV file not found at {input_csv_path}")
        return False
    
    # Create CSV enrichment crew
    crew = CSVEnrichmentCrew(
        source_csv_path=source_csv_path,
        input_csv_path=input_csv_path,
        category_columns=["Category ID", "Category Label"]
    )
    
    # Run the enrichment process
    print("Running CSV enrichment process...")
    output_csv_path = crew.run()
    
    # Verify the results
    if not os.path.exists(output_csv_path):
        print(f"Error: Output CSV file not found at {output_csv_path}")
        return False
    
    # Read the input and output CSV files
    input_df = pd.read_csv(input_csv_path)
    output_df = pd.read_csv(output_csv_path)
    
    # Count missing values before and after enrichment
    input_missing_category_id = input_df["Category ID"].isna().sum()
    input_missing_category_label = input_df["Category Label"].isna().sum()
    output_missing_category_id = output_df["Category ID"].isna().sum()
    output_missing_category_label = output_df["Category Label"].isna().sum()
    
    # Print results
    print("\nEnrichment Results:")
    print(f"Input CSV: {input_missing_category_id} missing Category IDs, {input_missing_category_label} missing Category Labels")
    print(f"Output CSV: {output_missing_category_id} missing Category IDs, {output_missing_category_label} missing Category Labels")
    
    # Calculate improvement
    id_improvement = input_missing_category_id - output_missing_category_id
    label_improvement = input_missing_category_label - output_missing_category_label
    
    print(f"\nImprovement: {id_improvement} Category IDs filled, {label_improvement} Category Labels filled")
    
    # Check if there was any improvement
    if id_improvement > 0 or label_improvement > 0:
        print("\nTest PASSED: CSV enrichment process successfully filled missing values.")
        return True
    else:
        print("\nTest FAILED: CSV enrichment process did not fill any missing values.")
        return False

if __name__ == "__main__":
    success = test_enrichment()
    sys.exit(0 if success else 1) 