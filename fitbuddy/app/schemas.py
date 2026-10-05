"""Pydantic models for request validation."""
from typing import Literal

from pydantic import BaseModel, Field


class UserInput(BaseModel):
    username: str = Field(..., min_length=1)
    user_id: int = Field(..., ge=1)
    age: int = Field(..., ge=10, le=100)
    weight: float = Field(..., gt=20, lt=400)
    goal: str = Field(..., min_length=2)
    intensity: Literal["low", "medium", "high"]


class WorkoutRequest(BaseModel):
    goal: str
    intensity: Literal["low", "medium", "high"] = "medium"


class FeedbackRequest(BaseModel):
    feedback: str = Field(..., min_length=3)
