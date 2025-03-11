import os
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import uuid

class FileHandler:
    """Utility class for handling CSV files"""
    
    @staticmethod
    def save_uploaded_file(file_content: bytes, filename: str) -> str:
        """
        Save an uploaded file to the data directory
        
        Args:
            file_content: The content of the uploaded file
            filename: The name of the file
            
        Returns:
            The path to the saved file
        """
        # Create a unique filename to avoid collisions
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join("data", unique_filename)
        
        # Ensure the data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Write the file
        with open(file_path, "wb") as f:
            f.write(file_content)
            
        return file_path
    
    @staticmethod
    def read_csv(file_path: str) -> pd.DataFrame:
        """
        Read a CSV file into a pandas DataFrame
        
        Args:
            file_path: The path to the CSV file
            
        Returns:
            A pandas DataFrame containing the CSV data
        """
        return pd.read_csv(file_path)
    
    @staticmethod
    def save_csv(df: pd.DataFrame, file_path: str) -> str:
        """
        Save a pandas DataFrame to a CSV file
        
        Args:
            df: The DataFrame to save
            file_path: The path to save the CSV file
            
        Returns:
            The path to the saved file
        """
        df.to_csv(file_path, index=False)
        return file_path
    
    @staticmethod
    def analyze_csv(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze a CSV file to identify missing values and column types
        
        Args:
            df: The DataFrame to analyze
            
        Returns:
            A dictionary containing analysis results
        """
        # Get basic information
        num_rows = len(df)
        num_cols = len(df.columns)
        columns = list(df.columns)
        
        # Analyze missing values
        missing_values = df.isnull().sum().to_dict()
        missing_percentage = {col: (count / num_rows) * 100 for col, count in missing_values.items()}
        
        # Identify columns with missing values
        columns_with_missing = [col for col, count in missing_values.items() if count > 0]
        
        # Get column data types
        column_types = df.dtypes.astype(str).to_dict()
        
        return {
            "num_rows": num_rows,
            "num_cols": num_cols,
            "columns": columns,
            "missing_values": missing_values,
            "missing_percentage": missing_percentage,
            "columns_with_missing": columns_with_missing,
            "column_types": column_types
        }
    
    @staticmethod
    def identify_missing_categories(df: pd.DataFrame, category_columns: List[str]) -> Tuple[pd.DataFrame, List[int]]:
        """
        Identify rows with missing category values
        
        Args:
            df: The DataFrame to analyze
            category_columns: List of column names that contain category information
            
        Returns:
            Tuple containing the DataFrame with only rows that have missing categories,
            and a list of the original indices of these rows
        """
        # Create a mask for rows with any missing category values
        mask = df[category_columns].isnull().any(axis=1)
        
        # Get the indices of rows with missing categories
        missing_indices = df[mask].index.tolist()
        
        # Return the filtered DataFrame and the original indices
        return df[mask], missing_indices 