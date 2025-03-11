import streamlit as st
import pandas as pd
import requests
import time
import os
import io
import base64
from typing import Optional

# API endpoint
API_URL = "http://localhost:8000"

# Set page config
st.set_page_config(
    page_title="CSV Data Enrichment",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4B8BBE;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #306998;
        margin-bottom: 1rem;
    }
    .info-text {
        font-size: 1rem;
        color: #333;
    }
    .success-text {
        color: #28a745;
        font-weight: bold;
    }
    .error-text {
        color: #dc3545;
        font-weight: bold;
    }
    .progress-container {
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_download_link(file_content, filename):
    """Generate a download link for a file"""
    b64 = base64.b64encode(file_content).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

def check_task_status(task_id: str) -> Optional[dict]:
    """Check the status of a task"""
    try:
        response = requests.get(f"{API_URL}/tasks/{task_id}/status")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error checking task status: {e}")
        return None

def download_file(task_id: str):
    """Download the enriched file"""
    try:
        response = requests.get(f"{API_URL}/tasks/{task_id}/download", stream=True)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        st.error(f"Error downloading file: {e}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">CSV Data Enrichment with CrewAI</h1>', unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    <p class="info-text">
    This application uses CrewAI agents with CSV RAG Search to fill missing data in your CSV files.
    Upload a CSV file with missing category values, and our AI agents will analyze it and fill in the missing information.
    </p>
    """, unsafe_allow_html=True)
    
    # File upload section
    st.markdown('<h2 class="sub-header">Upload Your CSV File</h2>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    # Category columns input
    category_columns = st.text_input(
        "Category Columns (comma-separated)",
        help="Enter the names of the columns that contain category information, separated by commas."
    )
    
    # Process button
    process_button = st.button("Process File", disabled=not uploaded_file)
    
    # Session state for task tracking
    if "task_id" not in st.session_state:
        st.session_state.task_id = None
    
    if "task_completed" not in st.session_state:
        st.session_state.task_completed = False
    
    if "enriched_file" not in st.session_state:
        st.session_state.enriched_file = None
    
    # Handle file processing
    if process_button and uploaded_file:
        with st.spinner("Uploading file..."):
            # Reset session state
            st.session_state.task_id = None
            st.session_state.task_completed = False
            st.session_state.enriched_file = None
            
            # Prepare the file for upload
            files = {"file": uploaded_file.getvalue()}
            
            # Prepare the form data
            data = {}
            if category_columns:
                data["category_columns"] = category_columns
            
            try:
                # Upload the file
                response = requests.post(f"{API_URL}/upload", files={"file": (uploaded_file.name, uploaded_file.getvalue())}, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.task_id = result["task_id"]
                    st.success(f"File uploaded successfully! Task ID: {st.session_state.task_id}")
                else:
                    st.error(f"Error uploading file: {response.text}")
            except Exception as e:
                st.error(f"Error uploading file: {e}")
    
    # Display file preview if uploaded
    if uploaded_file and not st.session_state.task_id:
        st.markdown('<h2 class="sub-header">File Preview</h2>', unsafe_allow_html=True)
        
        # Read and display the CSV
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head(10))
        
        # Display basic statistics
        st.markdown('<h3 class="sub-header">File Statistics</h3>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            missing_values = df.isnull().sum().sum()
            st.metric("Missing Values", missing_values)
    
    # Check task status and display progress
    if st.session_state.task_id and not st.session_state.task_completed:
        st.markdown('<h2 class="sub-header">Processing Status</h2>', unsafe_allow_html=True)
        
        status_placeholder = st.empty()
        progress_bar = st.progress(0)
        
        # Poll for status updates
        while True:
            status = check_task_status(st.session_state.task_id)
            
            if status:
                progress = status.get("progress", 0)
                message = status.get("message", "Processing...")
                task_status = status.get("status", "processing")
                
                # Update progress bar
                progress_bar.progress(progress)
                
                # Update status message
                status_placeholder.info(message)
                
                # Check if task is completed or failed
                if task_status == "completed":
                    st.session_state.task_completed = True
                    st.success("Processing completed successfully!")
                    break
                elif task_status == "failed":
                    error = status.get("error", "Unknown error")
                    st.error(f"Processing failed: {error}")
                    break
            
            # Wait before checking again
            time.sleep(1)
    
    # Display download button if task is completed
    if st.session_state.task_id and st.session_state.task_completed:
        st.markdown('<h2 class="sub-header">Download Enriched File</h2>', unsafe_allow_html=True)
        
        if st.button("Download Enriched CSV"):
            with st.spinner("Preparing download..."):
                file_content = download_file(st.session_state.task_id)
                
                if file_content:
                    # Create a download button
                    st.download_button(
                        label="Click to Download",
                        data=file_content,
                        file_name="enriched_data.csv",
                        mime="text/csv"
                    )
                    
                    # Display preview of enriched file
                    st.markdown('<h3 class="sub-header">Enriched File Preview</h3>', unsafe_allow_html=True)
                    
                    # Read and display the CSV
                    df = pd.read_csv(io.BytesIO(file_content))
                    st.dataframe(df.head(10))
                else:
                    st.error("Error downloading the enriched file.")

if __name__ == "__main__":
    main() 