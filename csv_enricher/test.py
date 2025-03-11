import os
import sys
import pandas as pd
from dotenv import load_dotenv
import time

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import CSVEnrichmentCrew
from utils import FileHandler

def test_csv_enrichment():
    """Test the CSV enrichment functionality"""
    print("Testing CSV enrichment functionality...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if ANTHROPIC_API_KEY is set
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please set it in the .env file.")
        return 1
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if source CSV file exists
    source_csv = os.path.join(current_dir, "data", "pricerunner_aggregate.csv")
    
    if not os.path.exists(source_csv):
        print(f"Error: Source CSV file not found at {source_csv}")
        print("Please run setup.py first to copy the source CSV file.")
        return 1
    
    # Check if sample input CSV file exists
    sample_input = os.path.join(current_dir, "data", "sample_input.csv")
    
    if not os.path.exists(sample_input):
        print(f"Error: Sample input CSV file not found at {sample_input}")
        return 1
    
    try:
        # Read the sample input CSV
        input_df = pd.read_csv(sample_input)
        print(f"Sample input CSV has {len(input_df)} rows and {len(input_df.columns)} columns.")
        
        # Identify category columns
        category_columns = ["category_name", "category_type"]
        
        # Count missing values in category columns
        missing_values = input_df[category_columns].isnull().sum().sum()
        print(f"Sample input CSV has {missing_values} missing values in category columns.")
        
        # Create the enrichment crew
        print("Creating CSV enrichment crew...")
        start_time = time.time()
        crew = CSVEnrichmentCrew(
            source_csv_path=source_csv,
            input_csv_path=sample_input,
            category_columns=category_columns
        )
        
        # Run the enrichment process
        print("Running CSV enrichment process...")
        output_file = crew.run()
        end_time = time.time()
        
        # Calculate execution time
        execution_time = end_time - start_time
        print(f"CSV enrichment process completed in {execution_time:.2f} seconds.")
        
        # Check if output file exists
        if not os.path.exists(output_file):
            print(f"Error: Output file not found at {output_file}")
            return 1
        
        # Read the output CSV
        output_df = pd.read_csv(output_file)
        print(f"Output CSV has {len(output_df)} rows and {len(output_df.columns)} columns.")
        
        # Count missing values in category columns
        missing_values_after = output_df[category_columns].isnull().sum().sum()
        print(f"Output CSV has {missing_values_after} missing values in category columns.")
        
        # Calculate the number of filled values
        filled_values = missing_values - missing_values_after
        print(f"CSV enrichment process filled {filled_values} missing values.")
        
        # Print the enriched values
        if filled_values > 0:
            print("\nEnriched values:")
            for i, row in output_df.iterrows():
                if not pd.isna(row["category_name"]) and not pd.isna(row["category_type"]):
                    if pd.isna(input_df.at[i, "category_name"]) or pd.isna(input_df.at[i, "category_type"]):
                        print(f"Row {i}: {row['product_name']} -> {row['category_name']}, {row['category_type']}")
        
        print("\nTest completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error during test: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_csv_enrichment()) 