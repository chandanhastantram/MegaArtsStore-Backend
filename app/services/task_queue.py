"""
Task Queue Service
Async background task processing using asyncio queues
"""

import asyncio
from typing import Callable, Any, Dict
from datetime import datetime
import uuid
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskQueue:
    """
    Simple async task queue for background processing.
    
    Handles:
    - Email sending
    - Image processing
    - 3D model generation
    - Report generation
    """
    
    def __init__(self, max_workers: int = 5):
        self.queue = asyncio.Queue()
        self.tasks: Dict[str, Dict] = {}
        self.max_workers = max_workers
        self.workers = []
        self.running = False
    
    async def start(self):
        """Start the task queue workers"""
        if self.running:
            return
        
        self.running = True
        self.workers = [
            asyncio.create_task(self._worker(i))
            for i in range(self.max_workers)
        ]
    
    async def stop(self):
        """Stop the task queue workers"""
        self.running = False
        
        # Wait for queue to empty
        await self.queue.join()
        
        # Cancel workers
        for worker in self.workers:
            worker.cancel()
        
        await asyncio.gather(*self.workers, return_exceptions=True)
    
    async def _worker(self, worker_id: int):
        """Worker that processes tasks from the queue"""
        while self.running:
            try:
                task_id, func, args, kwargs = await self.queue.get()
                
                # Update task status
                self.tasks[task_id]["status"] = TaskStatus.RUNNING
                self.tasks[task_id]["started_at"] = datetime.utcnow()
                
                try:
                    # Execute task
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    # Mark as completed
                    self.tasks[task_id]["status"] = TaskStatus.COMPLETED
                    self.tasks[task_id]["result"] = result
                    self.tasks[task_id]["completed_at"] = datetime.utcnow()
                    
                except Exception as e:
                    # Mark as failed
                    self.tasks[task_id]["status"] = TaskStatus.FAILED
                    self.tasks[task_id]["error"] = str(e)
                    self.tasks[task_id]["completed_at"] = datetime.utcnow()
                
                finally:
                    self.queue.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
    
    async def enqueue(
        self,
        func: Callable,
        *args,
        task_name: str = None,
        **kwargs
    ) -> str:
        """
        Add a task to the queue.
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            task_name: Optional task name
            **kwargs: Keyword arguments for func
        
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        
        # Store task metadata
        self.tasks[task_id] = {
            "id": task_id,
            "name": task_name or func.__name__,
            "status": TaskStatus.PENDING,
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None
        }
        
        # Add to queue
        await self.queue.put((task_id, func, args, kwargs))
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get task status and result"""
        return self.tasks.get(task_id, {"status": "not_found"})
    
    def get_queue_stats(self) -> Dict:
        """Get queue statistics"""
        pending = sum(1 for t in self.tasks.values() if t["status"] == TaskStatus.PENDING)
        running = sum(1 for t in self.tasks.values() if t["status"] == TaskStatus.RUNNING)
        completed = sum(1 for t in self.tasks.values() if t["status"] == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks.values() if t["status"] == TaskStatus.FAILED)
        
        return {
            "queue_size": self.queue.qsize(),
            "total_tasks": len(self.tasks),
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
            "workers": self.max_workers
        }


# Global task queue instance
task_queue = TaskQueue(max_workers=5)


# ============ Helper Functions ============

async def queue_email_task(email_func: Callable, *args, **kwargs) -> str:
    """Queue an email sending task"""
    return await task_queue.enqueue(
        email_func,
        *args,
        task_name=f"email_{email_func.__name__}",
        **kwargs
    )


async def queue_image_processing(image_func: Callable, *args, **kwargs) -> str:
    """Queue an image processing task"""
    return await task_queue.enqueue(
        image_func,
        *args,
        task_name=f"image_{image_func.__name__}",
        **kwargs
    )


async def queue_model_processing(model_func: Callable, *args, **kwargs) -> str:
    """Queue a 3D model processing task"""
    return await task_queue.enqueue(
        model_func,
        *args,
        task_name=f"model_{model_func.__name__}",
        **kwargs
    )


async def queue_analytics_task(analytics_func: Callable, *args, **kwargs) -> str:
    """Queue an analytics/report generation task"""
    return await task_queue.enqueue(
        analytics_func,
        *args,
        task_name=f"analytics_{analytics_func.__name__}",
        **kwargs
    )
