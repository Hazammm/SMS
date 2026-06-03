from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict
from datetime import date
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import os

from app.db import get_db, init_db, Course, Task, SkillGoal, RoutineLog
from app.ml import recommend_skills, optimize_schedule
from app.analytics import (
    compute_weighted_gpa, gpa_trend, grade_distribution,
    gpa_histogram, study_efficiency_score, burnout_risk, weekly_report
)
from app.notifications import deadline_alerts, productivity_nudges, study_streak, daily_quote
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the SQLite database and seed initial mock data
    init_db()
    yield

app = FastAPI(
    title="Student Management System (SMS) Backend",
    description="FastAPI Backend with ML-based Skill Recommendations and Routine Optimization.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Pydantic Schemas
# ==========================================

# Course Schemas
class CourseBase(BaseModel):
    code: str
    name: str
    credits: int
    grade: str
    gpa: float

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    credits: Optional[int] = None
    grade: Optional[str] = None
    gpa: Optional[float] = None

class CourseResponse(CourseBase):
    id: int
    class Config:
        from_attributes = True

# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str
    category: str
    due_date: str
    status: str

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    class Config:
        from_attributes = True

# RoutineLog (Study/Activity Session) Schemas
class RoutineLogBase(BaseModel):
    activity: str
    duration: int
    productivity: int
    date: str
    category: str

class RoutineLogCreate(RoutineLogBase):
    pass

class RoutineLogUpdate(BaseModel):
    activity: Optional[str] = None
    duration: Optional[int] = None
    productivity: Optional[int] = None
    date: Optional[str] = None
    category: Optional[str] = None

class RoutineLogResponse(RoutineLogBase):
    id: int
    class Config:
        from_attributes = True

# SkillGoal (Tracked Target Skill) Schemas
class SkillGoalBase(BaseModel):
    name: str
    progress: int = 0
    goal: str

class SkillGoalCreate(SkillGoalBase):
    pass

class SkillGoalUpdate(BaseModel):
    name: Optional[str] = None
    progress: Optional[int] = None
    goal: Optional[str] = None

class SkillGoalResponse(SkillGoalBase):
    id: int
    class Config:
        from_attributes = True

# ML Schemas
class RecommendRequest(BaseModel):
    career_objective: str
    num_recommendations: int = Field(default=3, ge=1, le=10)

class RecommendResponse(BaseModel):
    id: int
    title: str
    category: str
    skills: List[str]
    description: str
    score: float

# ==========================================
# Endpoints: Health Check
# ==========================================
@app.get("/api/health")
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API Connected successfully"}

# ==========================================
# Endpoints: Course CRUD
# ==========================================
@app.post("/api/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
@app.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    existing = db.query(Course).filter(Course.code == course.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course code already exists")
    db_course = Course(**course.model_dump())
    db.add(db_course)
    try:
        db.commit()
        db.refresh(db_course)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_course

@app.get("/api/courses", response_model=List[CourseResponse])
@app.get("/courses", response_model=List[CourseResponse])
def get_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Course).offset(skip).limit(limit).all()

@app.delete("/api/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return None

# ==========================================
# Endpoints: Task CRUD
# ==========================================
@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(**task.model_dump())
    db.add(db_task)
    try:
        db.commit()
        db.refresh(db_task)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_task

@app.get("/api/tasks", response_model=List[TaskResponse])
@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Task).offset(skip).limit(limit).all()

@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_dict = task_data.model_dump(exclude_unset=True)
    for key, val in update_dict.items():
        setattr(task, key, val)
    try:
        db.commit()
        db.refresh(task)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return task

@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return None

# ==========================================
# Endpoints: Routine Log (Activity Session) CRUD
# ==========================================
@app.post("/api/routine", response_model=RoutineLogResponse, status_code=status.HTTP_201_CREATED)
@app.post("/routine", response_model=RoutineLogResponse, status_code=status.HTTP_201_CREATED)
@app.post("/api/routines", response_model=RoutineLogResponse, status_code=status.HTTP_201_CREATED)
def create_routine_log(log: RoutineLogCreate, db: Session = Depends(get_db)):
    db_log = RoutineLog(**log.model_dump())
    db.add(db_log)
    try:
        db.commit()
        db.refresh(db_log)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_log

@app.get("/api/routine", response_model=List[RoutineLogResponse])
@app.get("/routine", response_model=List[RoutineLogResponse])
@app.get("/api/routines", response_model=List[RoutineLogResponse])
def get_routine_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(RoutineLog).order_by(RoutineLog.date.desc()).offset(skip).limit(limit).all()

@app.delete("/api/routine/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
@app.delete("/routine/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
@app.delete("/api/routines/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routine_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(RoutineLog).filter(RoutineLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Routine session log not found")
    db.delete(log)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return None

# ==========================================
# Endpoints: Tracked Target Skill (SkillGoal) CRUD
# ==========================================
@app.post("/api/skills/targets", response_model=SkillGoalResponse, status_code=status.HTTP_201_CREATED)
@app.post("/skills/targets", response_model=SkillGoalResponse, status_code=status.HTTP_201_CREATED)
@app.post("/api/skills", response_model=SkillGoalResponse, status_code=status.HTTP_201_CREATED)
def create_skill_goal(goal: SkillGoalCreate, db: Session = Depends(get_db)):
    db_goal = SkillGoal(**goal.model_dump())
    db.add(db_goal)
    try:
        db.commit()
        db.refresh(db_goal)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_goal

@app.get("/api/skills/targets", response_model=List[SkillGoalResponse])
@app.get("/skills/targets", response_model=List[SkillGoalResponse])
@app.get("/api/skills", response_model=List[SkillGoalResponse])
def get_skill_goals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(SkillGoal).offset(skip).limit(limit).all()

@app.put("/api/skills/targets/{goal_id}", response_model=SkillGoalResponse)
@app.put("/skills/targets/{goal_id}", response_model=SkillGoalResponse)
@app.put("/api/skills/{goal_id}", response_model=SkillGoalResponse)
def update_skill_goal(goal_id: int, goal_data: SkillGoalUpdate, db: Session = Depends(get_db)):
    goal = db.query(SkillGoal).filter(SkillGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Tracked skill not found")
    update_dict = goal_data.model_dump(exclude_unset=True)
    for key, val in update_dict.items():
        setattr(goal, key, val)
    try:
        db.commit()
        db.refresh(goal)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return goal

@app.delete("/api/skills/targets/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
@app.delete("/skills/targets/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
@app.delete("/api/skills/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(SkillGoal).filter(SkillGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Tracked skill not found")
    db.delete(goal)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return None

# ==========================================
# Endpoints: ML / Schedule Optimization
# ==========================================
@app.post("/api/recommend-skills", response_model=List[RecommendResponse])
def get_recommendations(req: RecommendRequest):
    try:
        recs = recommend_skills(req.career_objective, req.num_recommendations)
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation engine failed: {str(e)}")

@app.get("/api/schedule/daily")
@app.get("/schedule/daily")
@app.get("/api/optimized-schedule")
def get_optimized_schedule(db: Session = Depends(get_db)):
    try:
        routine_logs = db.query(RoutineLog).order_by(RoutineLog.date.asc()).all()
        active_tasks = db.query(Task).filter(Task.status != "completed").all()
        opt_data = optimize_schedule(routine_logs, active_tasks)
        
        # Format study slots as expected by the frontend
        mapped_schedule = []
        for item in opt_data["schedule"]:
            mapped_schedule.append({
                "time": item["time_slot"],
                "title": item["activity"],
                "desc": item["description"],
                "type": "study" if "Study" in item["activity"] else "break" if "Break" in item["activity"] or "Rest" in item["activity"] or "Nap" in item["activity"] or "Recess" in item["activity"] else "study"
            })
        return mapped_schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routine optimizer failed: {str(e)}")

# ==========================================
# Endpoints: Analytics
# ==========================================
@app.get("/api/analytics/gpa")
def get_gpa_analytics(db: Session = Depends(get_db)):
    """Return weighted GPA, grade distribution, and a GPA histogram."""
    courses = db.query(Course).all()
    course_dicts = [{"code": c.code, "name": c.name, "credits": c.credits, "grade": c.grade, "gpa": c.gpa} for c in courses]
    return {
        "weighted_gpa": compute_weighted_gpa(course_dicts),
        "grade_distribution": grade_distribution(course_dicts),
        "gpa_histogram": gpa_histogram(course_dicts, bins=5),
    }

@app.get("/api/analytics/efficiency")
def get_study_efficiency(db: Session = Depends(get_db)):
    """Return per-session and overall study efficiency scores."""
    logs = db.query(RoutineLog).all()
    log_dicts = [{"activity": l.activity, "duration": l.duration, "productivity": l.productivity, "date": l.date, "category": l.category} for l in logs]
    return study_efficiency_score(log_dicts)

@app.get("/api/analytics/burnout")
def get_burnout_risk(db: Session = Depends(get_db)):
    """Return burnout risk level and advice based on this week's logs."""
    logs = db.query(RoutineLog).all()
    log_dicts = [{"activity": l.activity, "duration": l.duration, "productivity": l.productivity, "date": l.date, "category": l.category} for l in logs]
    return burnout_risk(log_dicts)

# ==========================================
# Endpoints: Notifications
# ==========================================
@app.get("/api/notifications/alerts")
def get_deadline_alerts(db: Session = Depends(get_db)):
    """Return urgency-sorted deadline alerts for all non-completed tasks."""
    tasks = db.query(Task).filter(Task.status != "completed").all()
    task_dicts = [{"id": t.id, "title": t.title, "due_date": t.due_date, "status": t.status, "priority": t.priority, "category": t.category} for t in tasks]
    return deadline_alerts(task_dicts)

@app.get("/api/notifications/nudges")
def get_productivity_nudges(db: Session = Depends(get_db)):
    """Return personalised productivity nudges based on recent session logs."""
    logs = db.query(RoutineLog).all()
    log_dicts = [{"activity": l.activity, "duration": l.duration, "productivity": l.productivity, "date": l.date} for l in logs]
    return {"nudges": productivity_nudges(log_dicts)}

@app.get("/api/notifications/quote")
def get_daily_quote(chandler_mode: bool = True):
    """Return today's motivational (or Chandler Bing) quote."""
    return {"quote": daily_quote(chandler_mode=chandler_mode)}

# ==========================================
# Endpoints: Reports & Streak
# ==========================================
@app.get("/api/report/weekly")
def get_weekly_report(db: Session = Depends(get_db)):
    """Return a comprehensive weekly performance report."""
    courses = db.query(Course).all()
    logs = db.query(RoutineLog).all()
    tasks = db.query(Task).all()
    course_dicts = [{"credits": c.credits, "grade": c.grade, "gpa": c.gpa} for c in courses]
    log_dicts = [{"duration": l.duration, "productivity": l.productivity, "date": l.date} for l in logs]
    task_dicts = [{"status": t.status, "priority": t.priority, "due_date": t.due_date, "title": t.title} for t in tasks]
    return weekly_report(course_dicts, log_dicts, task_dicts, student_name=settings.student.default_name)

@app.get("/api/streak")
def get_study_streak(db: Session = Depends(get_db)):
    """Return current and longest study streak counts."""
    logs = db.query(RoutineLog).all()
    log_dicts = [{"date": l.date} for l in logs]
    return study_streak(log_dicts)

@app.get("/api/student/profile")
def get_student_profile():
    """Return the student profile configuration (name, avatar, role)."""
    return {
        "name": settings.student.default_name,
        "role": settings.student.default_role,
        "avatar": settings.student.avatar_path,
        "chandler_mode": settings.student.chandler_mode_quotes,
    }

# ==========================================
# Static Files Server Mount (SPA Mode)
# ==========================================
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
