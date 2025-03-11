from crewai import Agent
from crewai.tools import BaseTool
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_data_enricher_agent(tools: Optional[List[BaseTool]] = None) -> Agent:
    """
    Create an agent that enriches CSV data by filling in missing values
    
    Args:
        tools: Optional list of tools to provide to the agent
        
    Returns:
        A CrewAI Agent configured for data enrichment
    """
    return Agent(
        role="Data Enrichment Specialist",
        goal="Fill in missing data in CSV files by finding exact matches or similar products in source data",
        backstory="""You are a data enrichment specialist with expertise in completing 
        datasets with missing values. You have a deep understanding of various data 
        categories and classifications, allowing you to accurately predict and fill in 
        missing information. You're meticulous and ensure that all data you add is 
        consistent with the existing dataset patterns. You are proficient in Python 
        and pandas for data manipulation and can write code to process CSV files efficiently.
        
        Your specialty is using semantic search to find similar products in reference datasets
        and extracting the correct category information. You always prioritize using actual
        data from source files rather than creating artificial categories.
        
        When enriching CSV files, you follow these steps:
        1. Identify rows with missing category values
        2. For each row, use the CSV Search Tool to find similar products
        3. Extract the category information from the search results
        4. Apply the category information to the original row
        5. Save the enriched CSV file
        
        You always provide a detailed summary of the enrichments you've made, including
        the number of rows processed and the specific values you've added.""",
        verbose=True,
        allow_delegation=False,
        tools=tools or [],
        llm="anthropic/claude-3-5-sonnet-20241022",
        allow_code_execution=True,  # Enable code execution for this agent
        max_iterations=3,  # Allow multiple iterations to improve results
        memory=True  # Enable memory to remember previous interactions
    ) 