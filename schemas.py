from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# --- User Data Formats ---
class UserCreate(BaseModel):
    name: str
    email: EmailStr # This will be used for validation [cite: 167]

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime
    class Config:
        from_attributes = True

# --- Habit Data Formats ---
class HabitCreate(BaseModel):
    name: str
    target_days_per_week: int
    user_id: int

class HabitResponse(BaseModel):
    id: int
    name: str
    target_days_per_week: int
    user_id: int
    class Config:
        from_attributes = True

# --- Habit Log Data Formats ---
class HabitLogCreate(BaseModel):
    log_date: datetime
    completed: bool = True

class HabitLogResponse(BaseModel):
    id: int
    habit_id: int
    log_date: datetime
    completed: bool
    class Config:
        from_attributes = True