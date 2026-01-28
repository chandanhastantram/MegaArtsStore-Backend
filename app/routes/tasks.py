"""
Task Queue Routes
Monitor and manage background tasks
"""

from fastapi import APIRouter, Depends

from app.services.task_queue import task_queue
from app.middleware.rbac import get_admin_user

router = APIRouter()


@router.get("/stats")
async def get_queue_stats(
    current_user: dict = Depends(get_admin_user)
):
    """
    Get task queue statistics.
    
    - Admin only
    """
    return task_queue.get_queue_stats()


@router.get("/task/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Get status of a specific task.
    
    - Admin only
    """
    return task_queue.get_task_status(task_id)
