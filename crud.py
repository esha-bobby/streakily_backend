from sqlalchemy.orm import Session
import models, schemas
from datetime import date, timedelta, datetime
from sqlalchemy import func # Add this to your imports at the top
from fastapi import HTTPException #
# --- User Logic ---
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Habit Logic ---
def create_habit(db: Session, habit: schemas.HabitCreate):
    db_habit = models.Habit(
        name=habit.name, 
        target_days_per_week=habit.target_days_per_week, 
        user_id=habit.user_id
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

# --- Streak Calculation Logic (20 Marks) ---
def get_streak_data(db: Session, habit_id: int):
    # Fetch all completed logs for this habit, newest first [cite: 143]
    logs = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        models.HabitLog.completed == True
    ).order_by(models.HabitLog.log_date.desc()).all()

    if not logs:
        return {"current_streak": 0, "longest_streak": 0}

    # 1. Current Streak: Must be today or yesterday to continue [cite: 81, 83]
    current_streak = 0
    today = date.today()
    last_log_date = logs[0].log_date.date()
    
    if last_log_date == today or last_log_date == today - timedelta(days=1):
        current_streak = 1
        for i in range(len(logs) - 1):
            if (logs[i].log_date.date() - logs[i+1].log_date.date()).days == 1:
                current_streak += 1
            else:
                break
    
    # 2. Longest Streak: The historical record [cite: 82]
    longest_streak = 0
    temp_streak = 1
    longest_streak = 1
    for i in range(len(logs) - 1):
        if (logs[i].log_date.date() - logs[i+1].log_date.date()).days == 1:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1
                
    return {"current_streak": current_streak, "longest_streak": longest_streak}

# --- Habit Logging Logic ---
def create_habit_log(db: Session, habit_id: int, log_data: schemas.HabitLogCreate):
    # 1. NEW: Check if the habit actually exists first!
    habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # 2. Rule: No duplicate logs for the same day
    existing_log = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        func.date(models.HabitLog.log_date) == log_data.log_date.date()
    ).first()

    if existing_log:
        raise HTTPException(status_code=400, detail="Habit already logged for this date")

    # 3. Rule: Cannot log future dates
    if log_data.log_date.date() > date.today():
        raise HTTPException(status_code=400, detail="Cannot log future dates")

    # 4. Save the log
    db_log = models.HabitLog(habit_id=habit_id, **log_data.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# View and Delete User
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

# View and Delete Habit
def get_user_habits(db: Session, user_id: int):
    return db.query(models.Habit).filter(models.Habit.user_id == user_id).all()

def delete_habit(db: Session, habit_id: int):
    # 1. Find the habit first
    db_habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
    
    if db_habit:
        # 2. Delete all associated logs FIRST (removes the foreign key dependency)
        db.query(models.HabitLog).filter(models.HabitLog.habit_id == habit_id).delete()
        
        # 3. Now delete the habit itself
        db.delete(db_habit)
        db.commit()
        return db_habit
        
    return None

def get_habit(db: Session, habit_id: int):
    return db.query(models.Habit).filter(models.Habit.id == habit_id).first()

# Update an existing log [cite: 142]
def update_habit_log(db: Session, habit_id: int, log_date: date, completed: bool):
    db_log = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        func.date(models.HabitLog.log_date) == log_date
    ).first()
    
    if db_log:
        db_log.completed = completed
        db.commit()
        db.refresh(db_log)
    return db_log