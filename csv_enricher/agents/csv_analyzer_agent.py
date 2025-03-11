from crewai import Agent
from crewai.tools import BaseTool
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_csv_analyzer_agent(tools: Optional[List[BaseTool]] = None) -> Agent:
    """
    Create an agent that analyzes CSV files and identifies missing data
    
    Args:
        tools: Optional list of tools to provide to the agent
        
    Returns:
        A CrewAI Agent configured for CSV analysis
    """
    return Agent(
        role="CSV Data Analyzer",
        goal="Analyze CSV files to identify missing data and understand the data structure",
        backstory="""You are an expert data analyst specializing in CSV data analysis. 
        Your expertise lies in understanding data structures, identifying patterns, 
        and detecting missing or inconsistent data. You have years of experience 
        working with various datasets and can quickly understand the relationships 
        between different data fields.
        
        You are particularly skilled at identifying patterns in product data and
        understanding how products are categorized. You can recognize when products
        belong to the same category even if they have different names or descriptions.""",
        verbose=True,
        allow_delegation=False,
        tools=tools or [],
        llm="anthropic/claude-3-5-sonnet-20241022",
        memory=True  # Enable memory to remember previous interactions
    ) 