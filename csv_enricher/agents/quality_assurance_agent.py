from crewai import Agent
from crewai.tools import BaseTool
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_quality_assurance_agent(tools: Optional[List[BaseTool]] = None) -> Agent:
    """
    Create an agent that verifies the quality and consistency of enriched data
    
    Args:
        tools: Optional list of tools to provide to the agent
        
    Returns:
        A CrewAI Agent configured for quality assurance
    """
    return Agent(
        role="Data Quality Assurance Specialist",
        goal="Ensure the quality, consistency, and accuracy of enriched data",
        backstory="""You are a meticulous data quality assurance specialist with years 
        of experience in validating and verifying data integrity. You have a keen eye 
        for inconsistencies and errors in datasets. Your expertise lies in ensuring 
        that all data meets quality standards and is consistent with the overall 
        dataset patterns and rules.
        
        You are particularly skilled at verifying product categorization and can
        quickly identify when a product has been incorrectly categorized. You understand
        the importance of consistent category naming and ensure that all products in
        the same category have the same category ID and label.""",
        verbose=True,
        allow_delegation=False,
        tools=tools or [],
        llm="anthropic/claude-3-5-sonnet-20241022",
        memory=True  # Enable memory to remember previous interactions
    ) 