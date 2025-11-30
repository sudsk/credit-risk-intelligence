"""
Task service - task management logic
"""
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.task import Task
from app.api.v1.websocket import broadcast_update


class TaskService:
    """Task management service"""
    
    def __init__(self):
        # In-memory storage for demo
        self._tasks: List[Task] = []
        self._generate_mock_tasks()
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        return self._tasks
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return next((t for t in self._tasks if t.id == task_id), None)
    
    def create_task(self, task: Task) -> Task:
        """Create new task"""
        self._tasks.insert(0, task)
        
        # Broadcast task creation via WebSocket
        asyncio.create_task(
            broadcast_update("task_created", task.dict())
        )
        
        return task
    
    def update_task(self, task_id: str, updates: dict) -> Optional[Task]:
        """Update task"""
        task = self.get_task_by_id(task_id)
        if not task:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """Delete task"""
        task = self.get_task_by_id(task_id)
        if task:
            self._tasks.remove(task)
            return True
        return False
    
    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark task as complete"""
        task = self.get_task_by_id(task_id)
        if not task:
            return None
        
        task.status = "completed"
        return task
    
    def _generate_mock_tasks(self):
        """Generate mock tasks for demo"""
        now = datetime.utcnow()
        
        # Overdue task
        self._tasks.append(
            Task(
                id="task_001",
                title="Follow up: TechStart Solutions - Revenue Decline",
                sme_id="#0142",
                sme_name="TechStart Solutions Ltd",
                exposure="€250K",
                assignee="John Smith",
                priority="high",
                due_date=(now - timedelta(days=3)).isoformat() + "Z",
                status="overdue",
                description="Investigate revenue decline and leadership changes. CTO departure confirmed.",
                source="News Intelligence (Nov 7)",
                created_at=(now - timedelta(days=10)).isoformat() + "Z"
            )
        )
        
        # Due today
        self._tasks.append(
            Task(
                id="task_002",
                title="Review: GreenTech Energy - New Application",
                sme_id="#0823",
                sme_name="GreenTech Energy Ltd",
                exposure="€300K",
                assignee="Jane Doe",
                priority="medium",
                due_date=now.isoformat() + "Z",
                status="due_today",
                description="Review new credit facility application.",
                source="Manual Entry (Nov 12)",
                created_at=(now - timedelta(days=4)).isoformat() + "Z"
            )
        )
        
        self._tasks.append(
            Task(
                id="task_003",
                title="Hemp Ban Impact: Review GreenLeaf Products",
                sme_id="#0445",
                sme_name="GreenLeaf Products",
                exposure="€320K",
                assignee="Sarah Chen",
                priority="high",
                due_date=now.isoformat() + "Z",
                status="due_today",
                description="Assess impact of potential UK hemp ban on business model.",
                source="Predicted Event - Hemp Ban (Nov 14)",
                created_at=(now - timedelta(days=2)).isoformat() + "Z"
            )
        )
        
        # Upcoming tasks
        for i in range(7):
            self._tasks.append(
                Task(
                    id=f"task_{100 + i}",
                    title=f"Quarterly Review: SME Portfolio {i+1}",
                    sme_id=f"#{i+1:04d}",
                    sme_name=f"Sample SME {i+1}",
                    exposure="€150K",
                    assignee="Mike Wilson",
                    priority="low",
                    due_date=(now + timedelta(days=7 + i)).isoformat() + "Z",
                    status="upcoming",
                    description="Standard quarterly credit review.",
                    source="Automated - Quarterly Review",
                    created_at=now.isoformat() + "Z"
                )
            )
