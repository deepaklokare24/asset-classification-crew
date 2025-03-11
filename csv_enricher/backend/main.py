from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import sys
import json
from typing import Dict, Any, List, Optional

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use absolute imports
from utils.file_handler import FileHandler
from utils.progress_tracker import ProgressTracker
from agents.csv_enrichment_crew import CSVEnrichmentCrew

app = FastAPI(title="CSV Enrichment API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Ensure data directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("data/progress", exist_ok=True)

# Store active tasks
active_tasks: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "CSV Enrichment API is running", "version": "0.2.0"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    category_columns: Optional[str] = None
):
    """
    Upload a CSV file for enrichment
    
    Args:
        file: The CSV file to enrich
        background_tasks: FastAPI background tasks
        category_columns: Comma-separated list of category column names
        
    Returns:
        Task ID for tracking progress
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Read the file content
    file_content = await file.read()
    
    # Save the uploaded file
    file_path = FileHandler.save_uploaded_file(file_content, file.filename)
    
    # Generate a task ID
    task_id = str(uuid.uuid4())
    
    # Parse category columns
    cat_cols = []
    if category_columns:
        cat_cols = [col.strip() for col in category_columns.split(',')]
    else:
        # Default to the last two columns if not specified
        # In a real application, you would want to analyze the file to determine this
        df = FileHandler.read_csv(file_path)
        cat_cols = df.columns[-2:].tolist()
    
    # Create a progress tracker
    tracker = ProgressTracker(task_id)
    
    # Store task info
    active_tasks[task_id] = {
        "input_file": file_path,
        "category_columns": cat_cols,
        "status": "initializing",
        "output_file": None
    }
    
    # Start the enrichment process in the background
    if background_tasks:
        background_tasks.add_task(
            process_file,
            task_id=task_id,
            input_file=file_path,
            category_columns=cat_cols
        )
    
    return {"task_id": task_id}

@app.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """
    Get the status of a task
    
    Args:
        task_id: The ID of the task
        
    Returns:
        Task status information
    """
    # Check if the task exists
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get the task state from the progress tracker
    state = ProgressTracker.get_task_state(task_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Task state not found")
    
    return state

@app.get("/tasks/{task_id}/download")
async def download_file(task_id: str):
    """
    Download the enriched CSV file
    
    Args:
        task_id: The ID of the task
        
    Returns:
        The enriched CSV file
    """
    # Check if the task exists
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get the task state
    state = ProgressTracker.get_task_state(task_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Task state not found")
    
    # Check if the task is completed
    if state["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task is not completed yet")
    
    # Get the output file path
    output_file = state["result"]
    
    if not output_file or not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    # Return the file
    return FileResponse(
        output_file,
        media_type="text/csv",
        filename=os.path.basename(output_file)
    )

async def process_file(task_id: str, input_file: str, category_columns: List[str]):
    """
    Process a CSV file in the background
    
    Args:
        task_id: The ID of the task
        input_file: Path to the input CSV file
        category_columns: List of category column names
    """
    # Create a progress tracker
    tracker = ProgressTracker(task_id)
    
    try:
        # Update task status
        tracker.update(0.05, "Starting CSV enrichment process...")
        
        # Get the source CSV file path
        source_csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "pricerunner_aggregate.csv")
        
        # Create the enrichment crew
        crew = CSVEnrichmentCrew(
            source_csv_path=source_csv_path,
            input_csv_path=input_file,
            category_columns=category_columns,
            progress_tracker=tracker
        )
        
        # Run the enrichment process
        output_file = crew.run()
        
        # Update task status
        tracker.complete(output_file)
        
        # Update active tasks
        active_tasks[task_id]["status"] = "completed"
        active_tasks[task_id]["output_file"] = output_file
        
    except Exception as e:
        # Update task status
        tracker.fail(str(e))
        
        # Update active tasks
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["error"] = str(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 