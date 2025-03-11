from crewai import Crew, Task, Process
from crewai_tools import CSVSearchTool
from typing import Dict, Any, List, Optional
import pandas as pd
import os
import uuid
import json
import sys
import time
import re

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import ProgressTracker
from .csv_analyzer_agent import create_csv_analyzer_agent
from .data_enricher_agent import create_data_enricher_agent
from .quality_assurance_agent import create_quality_assurance_agent

class CSVEnrichmentCrew:
    """Orchestrates a crew of agents to enrich CSV data"""
    
    def __init__(
        self, 
        source_csv_path: str,
        input_csv_path: str,
        category_columns: List[str],
        progress_tracker: Optional[ProgressTracker] = None
    ):
        """
        Initialize the CSV enrichment crew
        
        Args:
            source_csv_path: Path to the source CSV file with complete data
            input_csv_path: Path to the input CSV file with missing data
            category_columns: List of column names that contain category information
            progress_tracker: Optional progress tracker
        """
        self.source_csv_path = source_csv_path
        self.input_csv_path = input_csv_path
        self.category_columns = category_columns
        self.progress_tracker = progress_tracker
        self.output_csv_path = os.path.join(
            "data", 
            f"enriched_{uuid.uuid4().hex}_{os.path.basename(input_csv_path)}"
        )
        
        # Create CSV search tool with proper configuration
        self.csv_search_tool = CSVSearchTool(
            csv=source_csv_path,
            description="Search for information in the source CSV file to find matching categories for products. Use this tool to find similar products and extract their category information.",
            config=dict(
                llm=dict(
                    provider="anthropic",
                    config=dict(
                        model="claude-3-5-sonnet-20241022",
                        temperature=0.2  # Lower temperature for more deterministic results
                    )
                ),
                embedder=dict(
                    provider="huggingface",
                    config=dict(
                        model="sentence-transformers/all-MiniLM-L6-v2"  # Lightweight, fast model that works well for semantic search
                    )
                )
            )
        )
        
        # Create agents
        self.analyzer_agent = create_csv_analyzer_agent(tools=[self.csv_search_tool])
        self.enricher_agent = create_data_enricher_agent(tools=[self.csv_search_tool])
        self.qa_agent = create_quality_assurance_agent(tools=[self.csv_search_tool])
    
    def _update_progress(self, progress: float, message: str):
        """Update progress if a tracker is available"""
        if self.progress_tracker:
            self.progress_tracker.update(progress, message)
    
    def run(self) -> str:
        """
        Run the CSV enrichment crew
        
        Returns:
            The path to the enriched CSV file
        """
        # Create a unique ID for this run
        run_id = str(uuid.uuid4())
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(self.output_csv_path), exist_ok=True)
        
        # Update progress
        self._update_progress(0.1, "Initializing CSV enrichment crew")
        
        # No need to recreate the CSV search tool or agents - use the ones from __init__
        self._update_progress(0.2, "Creating tasks")
        
        # Task 1: Analyze the CSV file
        analyze_task = Task(
            description=f"""
            Analyze the CSV file to identify missing values in the following columns: {', '.join(self.category_columns)}.
            
            The CSV file is located at: {self.input_csv_path}
            
            Your analysis should include:
            1. The number of rows with missing values in each column
            2. Patterns or trends in the data that could help with filling in the missing values
            3. Recommendations for how to fill in the missing values
            
            Be thorough and detailed in your analysis.
            """,
            expected_output="A detailed analysis of the CSV file with recommendations for filling in missing values",
            agent=self.analyzer_agent
        )
        
        # Task 2: Enrich the CSV file
        enrich_task = Task(
            description=f"""
            Enrich the CSV file by filling in missing values in the following columns: {', '.join(self.category_columns)}.
            
            The input CSV file is located at: {self.input_csv_path}
            The output CSV file should be saved to: {self.output_csv_path}
            
            Use the analysis from the previous task to guide your enrichment process.
            
            IMPORTANT: You MUST use the CSV Search Tool to find matching products in the source CSV file.
            The source CSV file contains complete category information for similar products.
            
            Follow these steps:
            1. Read the input CSV file using pandas
            2. For each row with missing category values:
               a. Extract the product name or standardized product name
               b. Use the CSV Search Tool to search for similar products in the source CSV file
               c. Extract the actual Category ID and Category Label from the search results
               d. Use these EXACT values from the source data (not made-up values)
            3. Fill in the missing values with the actual category information from the source data
            4. Save the enriched CSV file to the output path
            
            Your code should:
            - Use semantic search to find the most similar products
            - Extract REAL category values from the source data, not create artificial ones
            - Handle cases where no match is found by searching for similar product types
            - Prioritize exact matches when available
            
            Here's an example of how to use the CSV Search Tool in your code:
            ```python
            import pandas as pd
            import json
            
            # Read the input CSV
            df = pd.read_csv('{self.input_csv_path}')
            
            # Function to search for similar products and extract category info
            def find_category_info(product_name):
                # Use the CSV Search Tool to find similar products
                search_query = product_name
                search_result = csv_search_tool(search_query=search_query, csv='{self.source_csv_path}')
                
                # Parse the search results to extract category information
                # The search results contain relevant matches from the source CSV
                # Look for rows that have category information
                
                # Example parsing logic (adjust based on actual results format)
                for line in search_result.split('\\n'):
                    if 'Category ID:' in line and 'Category Label:' in line:
                        # Extract the category information
                        category_id = line.split('Category ID:')[1].split(',')[0].strip()
                        category_label = line.split('Category Label:')[1].strip()
                        if category_id and category_label:
                            return category_id, category_label
                
                # If no match found, return None
                return None, None
            
            # Process each row with missing category information
            for idx, row in df.iterrows():
                if pd.isna(row['Category ID']) or pd.isna(row['Category Label']):
                    product_name = row['Product Title']
                    category_id, category_label = find_category_info(product_name)
                    
                    if category_id and category_label:
                        df.at[idx, 'Category ID'] = category_id
                        df.at[idx, 'Category Label'] = category_label
            
            # Save the enriched CSV
            df.to_csv('{self.output_csv_path}', index=False)
            ```
            
            After executing your code, provide a summary of the enrichments you made.
            """,
            expected_output="A summary of the enrichments made to the CSV file",
            agent=self.enricher_agent,
            context=[analyze_task]
        )
        
        # Task 3: Quality assurance
        qa_task = Task(
            description=f"""
            Perform quality assurance on the enriched CSV file.
            
            The enriched CSV file is located at: {self.output_csv_path}
            
            Your quality assurance should include:
            1. Verification that all missing values have been filled in
            2. Validation that the filled values are appropriate and consistent
            3. Identification of any anomalies or issues in the enriched data
            
            Be thorough and detailed in your quality assurance.
            """,
            expected_output="A quality assurance report for the enriched CSV file",
            agent=self.qa_agent,
            context=[analyze_task, enrich_task]
        )
        
        # Create the crew
        self._update_progress(0.4, "Creating crew")
        crew = Crew(
            agents=[self.analyzer_agent, self.enricher_agent, self.qa_agent],
            tasks=[analyze_task, enrich_task, qa_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Run the crew
        self._update_progress(0.5, "Running crew")
        crew_result = crew.kickoff()
        
        # Update progress
        self._update_progress(0.9, "Finalizing results")
        
        # Check if the output file exists
        if not os.path.exists(self.output_csv_path):
            print(f"Warning: Output file {self.output_csv_path} was not created by the agent.")
            print("Falling back to manual enrichment processing...")
            self._apply_enrichments_fallback(crew_result)
        else:
            print(f"Output file {self.output_csv_path} was successfully created by the agent.")
        
        # Update progress
        self._update_progress(1.0, "CSV enrichment complete")
        
        return self.output_csv_path

    def _apply_enrichments_fallback(self, crew_result: str) -> None:
        """
        Fallback method to apply enrichments if the agent didn't create the output file
        
        Args:
            crew_result: The result from the crew execution
        """
        print("Applying enrichments using fallback method...")
        
        # Read the input CSV
        df = pd.read_csv(self.input_csv_path)
        
        # Track enrichment statistics
        enrichment_count = 0
        rows_processed = 0
        
        try:
            # Group by Cluster ID to find matching products
            cluster_groups = df.groupby('Cluster ID')
            
            # For each cluster, find rows with category information and apply to rows without
            for cluster_id, group in cluster_groups:
                # Skip clusters with only one row
                if len(group) <= 1:
                    continue
                
                # Find rows with category information
                category_rows = group[~group['Category Label'].isna()]
                
                # If we have rows with category information
                if not category_rows.empty:
                    # Get the first row with category information
                    category_row = category_rows.iloc[0]
                    category_id = category_row['Category ID']
                    category_label = category_row['Category Label']
                    
                    # Apply to rows without category information
                    for idx in group.index:
                        rows_processed += 1
                        
                        # If Category ID is missing, fill it
                        if pd.isna(df.at[idx, 'Category ID']):
                            df.at[idx, 'Category ID'] = category_id
                            enrichment_count += 1
                            print(f"Applied Category ID {category_id} to row {idx}")
                        
                        # If Category Label is missing, fill it
                        if pd.isna(df.at[idx, 'Category Label']):
                            df.at[idx, 'Category Label'] = category_label
                            enrichment_count += 1
                            print(f"Applied Category Label '{category_label}' to row {idx}")
            
            # For any remaining rows with missing category information, try to use the CSV Search Tool
            for idx, row in df.iterrows():
                if pd.isna(row['Category ID']) or pd.isna(row['Category Label']):
                    rows_processed += 1
                    product_title = row['Product Title']
                    
                    try:
                        # Use the CSV Search Tool to find similar products
                        print(f"Searching for similar products to: {product_title}")
                        search_result = self.csv_search_tool(search_query=product_title)
                        
                        # Parse the search results to extract category information
                        category_id_match = re.search(r'Category ID:\s*(\d+)', search_result)
                        category_label_match = re.search(r'Category Label:\s*([^,\n]+)', search_result)
                        
                        if category_id_match and pd.isna(row['Category ID']):
                            category_id = category_id_match.group(1).strip()
                            df.at[idx, 'Category ID'] = category_id
                            enrichment_count += 1
                            print(f"Applied Category ID {category_id} to row {idx} from search")
                        
                        if category_label_match and pd.isna(row['Category Label']):
                            category_label = category_label_match.group(1).strip()
                            df.at[idx, 'Category Label'] = category_label
                            enrichment_count += 1
                            print(f"Applied Category Label '{category_label}' to row {idx} from search")
                    except Exception as e:
                        print(f"Error using CSV Search Tool for row {idx}: {e}")
            
            print(f"Processed {rows_processed} rows and applied {enrichment_count} enrichments")
            
        except Exception as e:
            print(f"Error in fallback enrichment method: {e}")
            import traceback
            traceback.print_exc()
        
        # Save the enriched CSV
        df.to_csv(self.output_csv_path, index=False)
        print(f"Saved enriched CSV to {self.output_csv_path}") 