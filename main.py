from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, get_db
from datetime import date
from sqlalchemy import func

# Build the DB tables on startup [cite: 107]
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Streakify MVP")

# 1. Create User [cite: 133]
@app.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

# 2. Create Habit [cite: 137]
@app.post("/habits", response_model=schemas.HabitResponse)
def create_habit(habit: schemas.HabitCreate, db: Session = Depends(get_db)):
    return crud.create_habit(db=db, habit=habit)

# 3. View Streak [cite: 145]
@app.get("/habits/{habit_id}/streak")
def get_streak(habit_id: int, db: Session = Depends(get_db)):
    return crud.get_streak_data(db=db, habit_id=habit_id)

# 4. Dashboard [cite: 147]
@app.get("/users/{user_id}/dashboard")
def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    habits = crud.get_user_habits(db, user_id=user_id)
    total_habits = len(habits)
    
    if total_habits == 0:
        return {"totalHabits": 0, "activeHabits": 0, "completedToday": 0, "consistencyScore": 0}

    today = date.today()
    completed_today_count = 0
    results = []

    for h in habits:
        streak = crud.get_streak_data(db, h.id)
        # Check if logged today
        logged_today = db.query(models.HabitLog).filter(
            models.HabitLog.habit_id == h.id,
            func.date(models.HabitLog.log_date) == today,
            models.HabitLog.completed == True
        ).first()

        if logged_today:
            completed_today_count += 1
            
        results.append({"habitName": h.name, **streak})

    # Requirement 2.5: Consistency Score
    score = int((completed_today_count / total_habits) * 100)

    return {
        "totalHabits": total_habits,
        "activeHabits": total_habits,
        "completedToday": completed_today_count,
        "currentStreaks": results,
        "consistencyScore": score
    }

# New: Edit an existing log (Requirement 2.3)
@app.put("/habits/{habit_id}/logs/{log_date}")
def update_log(habit_id: int, log_date: date, completed: bool, db: Session = Depends(get_db)):
    db_log = crud.update_habit_log(db, habit_id=habit_id, log_date=log_date, completed=completed)
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    return db_log

# 5. Log a Habit (Add this now!)
@app.post("/habits/{habit_id}/logs", response_model=schemas.HabitLogResponse)
def log_habit(habit_id: int, log: schemas.HabitLogCreate, db: Session = Depends(get_db)):
    # This calls the logging logic we wrote in crud.py
    return crud.create_habit_log(db=db, habit_id=habit_id, log_data=log)

@app.get("/users/{id}", response_model=schemas.UserResponse)
def read_user(id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):
    return crud.delete_user(db, user_id=id)

@app.get("/users/{userId}/habits", response_model=list[schemas.HabitResponse])
def read_habits(userId: int, db: Session = Depends(get_db)):
    return crud.get_user_habits(db, user_id=userId)

@app.delete("/habits/{id}")
def delete_habit(id: int, db: Session = Depends(get_db)):
    return crud.delete_habit(db, habit_id=id)

# View a single habit by its ID
@app.get("/habits/{habit_id}", response_model=schemas.HabitResponse)
def read_habit(habit_id: int, db: Session = Depends(get_db)):
    db_habit = crud.get_habit(db, habit_id=habit_id)
    if db_habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return db_habit