from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskBase(BaseModel):
    customer_id: int | None = None
    order_id: int | None = None
    message_id: int | None = None
    task_type: str
    title: str
    description: str | None = None
    status: str = "open"
    priority: str = "medium"
    due_date: datetime | None = None
    assigned_to: str | None = None


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
