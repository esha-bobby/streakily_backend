from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True) # Unique as per requirement [cite: 112]
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # e.g. "Morning Workout" [cite: 66]
    target_days_per_week = Column(Integer) # [cite: 117]
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HabitLog(Base):
    __tablename__ = "habit_logs"
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"))
    log_date = Column(DateTime, nullable=False)
    completed = Column(Boolean, default=True)

    # CRITICAL: This ensures one log per habit per day [cite: 73, 128]
    __table_args__ = (UniqueConstraint('habit_id', 'log_date', name='_habit_date_uc'),)