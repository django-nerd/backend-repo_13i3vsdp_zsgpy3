from pydantic import BaseModel, Field
from typing import Optional, Literal

class Task(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Literal['backlog', 'selected', 'in_progress', 'done'] = 'backlog'
    assignee: Optional[str] = None
    priority: Optional[Literal['low', 'medium', 'high']] = 'medium'
    tag: Optional[str] = None
    points: Optional[int] = Field(None, ge=0, le=100)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[Literal['backlog', 'selected', 'in_progress', 'done']] = None
    assignee: Optional[str] = None
    priority: Optional[Literal['low', 'medium', 'high']] = None
    tag: Optional[str] = None
    points: Optional[int] = Field(None, ge=0, le=100)
