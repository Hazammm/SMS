import os
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, Float, String, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./sms.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    grade = Column(String, nullable=False)  # "A+", "A", "B", "IP", etc.
    gpa = Column(Float, nullable=False)     # 4.00, 3.70, etc.

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String, nullable=False)  # "low", "medium", "high"
    category = Column(String, nullable=False)  # "assignment", "project", "exam", "study"
    due_date = Column(String, nullable=False)  # YYYY-MM-DD
    status = Column(String, nullable=False, default="todo")  # "todo", "in_progress", "completed"

class RoutineLog(Base):
    __tablename__ = "routine_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    activity = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)     # in minutes
    productivity = Column(Integer, nullable=False)   # 1-10
    date = Column(String, nullable=False)           # YYYY-MM-DD
    category = Column(String, nullable=False)       # "study", "project", "revision", "class"

class SkillGoal(Base):
    __tablename__ = "skill_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    progress = Column(Integer, default=0, nullable=False)
    goal = Column(String, nullable=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_future_date_str(days_offset: int) -> str:
    d = date.today() + timedelta(days=days_offset)
    return d.isoformat()

def init_db():
    # If the database file exists, let's make sure it represents the updated tables
    # For a fresh startup we can create all
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Seed Courses
        if db.query(Course).first() is None:
            courses = [
                Course(code="CS-401", name="Artificial Intelligence & Neural Networks", credits=3, grade="A", gpa=4.00),
                Course(code="CS-302", name="Data Structures and Algorithms", credits=4, grade="A-", gpa=3.70),
                Course(code="CS-305", name="Database Management Systems", credits=3, grade="B+", gpa=3.30),
                Course(code="MAT-201", name="Linear Algebra & Applications", credits=3, grade="A", gpa=4.00),
                Course(code="CS-499", name="Capstone Project Phase I", credits=3, grade="IP", gpa=4.00),
            ]
            db.add_all(courses)
            
            # Seed Tasks
            tasks = [
                Task(
                    title="Implement backpropagation neural network in NumPy",
                    description="Write feedforward, cost computation, and gradient updates manually for a 3-layer net.",
                    priority="high",
                    category="assignment",
                    due_date=get_future_date_str(1),
                    status="in_progress"
                ),
                Task(
                    title="Design database schema for Capstone eCommerce project",
                    description="Draw Entity-Relationship diagrams and prepare SQL DDL schemas for PostgreSQL.",
                    priority="medium",
                    category="project",
                    due_date=get_future_date_str(3),
                    status="todo"
                ),
                Task(
                    title="Review lectures on Linear Algebra eigenvalues/eigenvectors",
                    description="Prepare notes on principal component analysis applications.",
                    priority="medium",
                    category="study",
                    due_date=get_future_date_str(5),
                    status="todo"
                ),
                Task(
                    title="Midterm Exam Prep - Graph algorithms & complex traversal",
                    description="Revise BFS, DFS, Dijkstra, Bellman-Ford, and Minimum Spanning Trees.",
                    priority="high",
                    category="exam",
                    due_date=get_future_date_str(2),
                    status="todo"
                ),
                Task(
                    title="Resolve LeetCode 3 Sum and sliding window problems",
                    description="Complete at least 5 medium-difficulty arrays/string interview questions.",
                    priority="low",
                    category="study",
                    due_date=get_future_date_str(-1),
                    status="completed"
                )
            ]
            db.add_all(tasks)
            
            # Seed Skill Goals
            skills = [
                SkillGoal(name="Deep Learning (PyTorch)", progress=65, goal="AI Engineer"),
                SkillGoal(name="Relational DB Normalization", progress=85, goal="Database Systems"),
                SkillGoal(name="Docker Containerization", progress=30, goal="DevOps Architect")
            ]
            db.add_all(skills)
            
            # Seed Routine Logs
            routine_logs = [
                RoutineLog(activity="Deep Work: Backpropagation Neural Net Coding", duration=120, productivity=9, date=get_future_date_str(0), category="project"),
                RoutineLog(activity="Lecture: Database Systems normalization study", duration=90, productivity=8, date=get_future_date_str(0), category="study"),
                RoutineLog(activity="Midterm Revision: Practice Exam Session", duration=150, productivity=7, date=get_future_date_str(-1), category="revision"),
                RoutineLog(activity="Linear Algebra: Problem sets on eigenvectors", duration=60, productivity=9, date=get_future_date_str(-2), category="study"),
                RoutineLog(activity="Capstone Team Standup & Backlog Grooming", duration=45, productivity=6, date=get_future_date_str(-2), category="class")
            ]
            db.add_all(routine_logs)
            
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()
