from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, get_db

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
    # This logic combines habits and streaks for the summary view [cite: 87-103]
    habits = db.query(models.Habit).filter(models.Habit.user_id == user_id).all()
    results = []
    for h in habits:
        streak = crud.get_streak_data(db, h.id)
        results.append({"habitName": h.name, **streak})
    return {"totalHabits": len(habits), "currentStreaks": results}

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