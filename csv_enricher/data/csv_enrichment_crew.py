from crewai import Crew, Task, Process
from crewai_tools import CSVSearchTool
from typing import Dict, Any, List, Optional
import pandas as pd
import os
import uuid
import json
import sys
import time

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
            csv_file=source_csv_path,
            description="Search for information in the source CSV file to find matching categories for products",
            config=dict(
                llm=dict(
                    provider="ollama",  # Using Ollama as primary provider since Anthropic is overloaded
                    config=dict(
                        model="llama2",
                        temperature=0.2
                    )
                ),
                embedder=dict(
                    provider="ollama",
                    config=dict(
                        model="nomic-embed-text",
                        base_url="http://localhost:11434"
                    )
                )
            )
        )
        
        # Create agents
        # use this for llama model: llm="ollama/llama2"
        self.analyzer_agent = create_csv_analyzer_agent(tools=[self.csv_search_tool])
        self.enricher_agent = create_data_enricher_agent(tools=[self.csv_search_tool])
        self.qa_agent = create_quality_assurance_agent(tools=[self.csv_search_tool])
    
    def _update_progress(self, progress: float, message: str):
        """Update progress if a tracker is available"""
        if self.progress_tracker:
            self.progress_tracker.update(progress, message)
    
    def run(self) -> str:
        """
        Run the CSV enrichment process
        
        Returns:
            Path to the enriched CSV file
        """
        # Create tasks
        self._update_progress(0.1, "Analyzing input CSV file...")
        
        analysis_task = Task(
            description=f"""
            Analyze the input CSV file at {self.input_csv_path} and identify rows with missing category values.
            The category columns are: {', '.join(self.category_columns)}.
            Provide a detailed analysis of the data structure and patterns.
            
            Specifically:
            1. Identify how many rows have missing category values
            2. Look for patterns in the product names that might help determine their categories
            3. Analyze the relationship between product names and their categories in rows where categories are present
            """,
            agent=self.analyzer_agent,
            expected_output="A detailed analysis of the CSV file structure and missing data"
        )
        
        self._update_progress(0.3, "Enriching data with missing categories...")
        
        enrichment_task = Task(
            description=f"""
            Use the CSV search tool to find appropriate category values for rows with missing data.
            The input CSV file is at {self.input_csv_path}.
            The category columns that may have missing values are: {', '.join(self.category_columns)}.
            
            For each row with missing category values:
            1. Extract key information from the product name and standardized product name
            2. Use the CSV search tool to search for similar products in the source CSV file
            3. Determine the appropriate category values based on the search results
            4. Return a list of row indices and the values that should be filled in
            
            Format your response as follows for each row:
            Row X: Column "category_name": "value", Column "category_type": "value"
            """,
            agent=self.enricher_agent,
            expected_output="A list of row indices and the category values to fill in",
            context=[analysis_task]
        )
        
        self._update_progress(0.6, "Verifying data quality...")
        
        qa_task = Task(
            description=f"""
            Verify the quality and consistency of the enriched data.
            Ensure that all filled category values are consistent with the overall dataset patterns.
            Check for any anomalies or inconsistencies in the enriched data.
            The input CSV file is at {self.input_csv_path}.
            The category columns are: {', '.join(self.category_columns)}.
            
            Specifically:
            1. Verify that the category values assigned to each product make sense given the product name
            2. Check for consistency in category assignments across similar products
            3. Identify any potential errors or inconsistencies in the enriched data
            4. Provide recommendations for any corrections needed
            """,
            agent=self.qa_agent,
            expected_output="A verification report confirming the quality of the enriched data or highlighting issues",
            context=[analysis_task, enrichment_task]
        )
        
        # Create crew
        crew = Crew(
            agents=[self.analyzer_agent, self.enricher_agent, self.qa_agent],
            tasks=[analysis_task, enrichment_task, qa_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Run crew with retry logic for API overload errors
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self._update_progress(0.7, "Running CrewAI agents to process data...")
                result = crew.kickoff()
                
                # Process results and update the CSV file
                self._update_progress(0.9, "Applying enrichments to the CSV file...")
                self._apply_enrichments(result.raw)
                
                self._update_progress(1.0, "CSV enrichment completed successfully")
                return self.output_csv_path
            
            except Exception as e:
                retry_count += 1
                error_message = str(e)
                
                if "overloaded_error" in error_message and retry_count < max_retries:
                    wait_time = 5 * retry_count  # Exponential backoff
                    self._update_progress(0.7, f"Anthropic API overloaded. Retrying in {wait_time} seconds... (Attempt {retry_count}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    if retry_count >= max_retries:
                        self._update_progress(0.7, f"Failed after {max_retries} attempts. Last error: {error_message}")
                    else:
                        self._update_progress(0.7, f"Error: {error_message}")
                    raise
    
    def _apply_enrichments(self, crew_result: str) -> None:
        """
        Apply the enrichments to the CSV file
        
        Args:
            crew_result: The result from the crew execution
        """
        # Read the input CSV
        df = pd.read_csv(self.input_csv_path)
        
        # Parse the enrichment results from the crew output
        # This is a simplified implementation - in a real application,
        # you would need more robust parsing of the crew's output
        try:
            # Look for patterns like "Row X: Column Y should be Z"
            import re
            
            # Find all instances of row indices and values to fill
            # This regex pattern is a simplified example and may need adjustment
            pattern = r"Row (\d+).*?Column ['\"](.*?)['\"]:?\s*['\"](.*?)['\"]"
            matches = re.findall(pattern, crew_result)
            
            enrichment_count = 0
            for row_idx_str, column, value in matches:
                try:
                    row_idx = int(row_idx_str)
                    if 0 <= row_idx < len(df) and column in df.columns:
                        df.at[row_idx, column] = value
                        enrichment_count += 1
                except (ValueError, KeyError) as e:
                    print(f"Error applying enrichment: {e}")
            
            print(f"Applied {enrichment_count} enrichments to the CSV file")
        
        except Exception as e:
            print(f"Error parsing crew results: {e}")
        
        # Save the enriched CSV
        df.to_csv(self.output_csv_path, index=False)