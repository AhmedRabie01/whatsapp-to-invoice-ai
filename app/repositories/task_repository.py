from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Task


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_task(
        self,
        *,
        customer_id: int | None,
        order_id: int | None,
        message_id: int | None,
        task_type: str,
        title: str,
        description: str | None,
        priority: str = "medium",
        due_date: datetime | None = None,
    ) -> Task:
        task = Task(
            customer_id=customer_id,
            order_id=order_id,
            message_id=message_id,
            task_type=task_type,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
        self.db.add(task)
        self.db.flush()
        self.db.refresh(task)
        return task
