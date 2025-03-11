import time
from typing import Dict, Any, Optional
import json
import os

class ProgressTracker:
    """Utility class for tracking progress of CSV enrichment tasks"""
    
    def __init__(self, task_id: str):
        """
        Initialize a progress tracker
        
        Args:
            task_id: Unique identifier for the task
        """
        self.task_id = task_id
        self.start_time = time.time()
        self.status = "initializing"
        self.progress = 0.0
        self.message = "Starting task..."
        self.result = None
        self.error = None
        
        # Ensure the progress directory exists
        os.makedirs("data/progress", exist_ok=True)
        
        # Save initial state
        self._save_state()
    
    def update(self, progress: float, message: str, status: str = "processing"):
        """
        Update the progress of the task
        
        Args:
            progress: Progress value between 0 and 1
            message: Current status message
            status: Status string (initializing, processing, completed, failed)
        """
        self.progress = min(max(progress, 0.0), 1.0)  # Ensure progress is between 0 and 1
        self.message = message
        self.status = status
        self._save_state()
    
    def complete(self, result: Any):
        """
        Mark the task as completed
        
        Args:
            result: The result of the task
        """
        self.progress = 1.0
        self.status = "completed"
        self.message = "Task completed successfully"
        self.result = result
        self._save_state()
    
    def fail(self, error: str):
        """
        Mark the task as failed
        
        Args:
            error: Error message
        """
        self.status = "failed"
        self.message = f"Task failed: {error}"
        self.error = error
        self._save_state()
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the task
        
        Returns:
            Dictionary containing the current state
        """
        elapsed_time = time.time() - self.start_time
        
        return {
            "task_id": self.task_id,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "elapsed_time": elapsed_time,
            "result": self.result,
            "error": self.error
        }
    
    def _save_state(self):
        """Save the current state to a file"""
        state = self.get_state()
        file_path = os.path.join("data/progress", f"{self.task_id}.json")
        
        with open(file_path, "w") as f:
            json.dump(state, f)
    
    @staticmethod
    def get_task_state(task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the state of a task from its ID
        
        Args:
            task_id: The ID of the task
            
        Returns:
            Dictionary containing the task state, or None if not found
        """
        file_path = os.path.join("data/progress", f"{task_id}.json")
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, "r") as f:
            return json.load(f) 