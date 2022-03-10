from datetime import datetime as dt
from pydantic import BaseModel


class TaskBase(BaseModel):
    task_name: str


class CreateTask(TaskBase):
    pass


class UpdateTask(TaskBase):
    task_id: str
    task_is_complete: bool

class DeleteTask(BaseModel):
    task_id: str
    status: bool


class Task(TaskBase):
    created_at: dt
    updated_at: dt
