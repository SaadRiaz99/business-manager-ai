from datetime import date, timedelta
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, get_db
from .models import Lead, Task
from .schemas import DemoGenerate, LeadCreate, LeadOut, LeadUpdate, TaskCreate
from .services import build_outreach, calculate_lead_score, demo_leads

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="BizPilot AI", version="0.1.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(engine)
    seed_database()


def seed_database() -> None:
    with SessionLocal() as db:
        if db.scalar(select(func.count(Lead.id))) == 0:
            samples = demo_leads("Cleaning Services", "Austin, Texas", "online booking and lead follow-up", 4)
            for index, item in enumerate(samples):
                score = calculate_lead_score(item)
                values = item.model_dump()
                values["stage"] = ["New", "Qualified", "Contacted", "Meeting"][index]
                db.add(Lead(**values, score=score, outreach_draft=build_outreach(item)))
            db.add(Task(title="Review hot leads", due_date=date.today(), priority="High"))
            db.add(Task(title="Follow up after demo", due_date=date.today() + timedelta(days=2), priority="Medium"))
            db.commit()


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/leads", response_model=list[LeadOut])
def list_leads(stage: str | None = None, db: Session = Depends(get_db)):
    query = select(Lead).order_by(Lead.score.desc(), Lead.created_at.desc())
    if stage:
        query = query.where(Lead.stage == stage)
    return db.scalars(query).all()


@app.post("/api/leads", response_model=LeadOut, status_code=201)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(**payload.model_dump(), score=calculate_lead_score(payload), outreach_draft=build_outreach(payload))
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@app.patch("/api/leads/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: int, payload: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)
    db.commit()
    db.refresh(lead)
    return lead


@app.delete("/api/leads/{lead_id}", status_code=204)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    db.delete(lead)
    db.commit()


@app.post("/api/leads/generate", response_model=list[LeadOut])
def generate_demo(payload: DemoGenerate, db: Session = Depends(get_db)):
    created = []
    for item in demo_leads(payload.industry, payload.location, payload.service, payload.count):
        lead = Lead(**item.model_dump(), score=calculate_lead_score(item), outreach_draft=build_outreach(item))
        db.add(lead)
        created.append(lead)
    db.commit()
    for lead in created:
        db.refresh(lead)
    return created


@app.get("/api/tasks")
def list_tasks(db: Session = Depends(get_db)):
    return db.scalars(select(Task).order_by(Task.completed, Task.due_date)).all()


@app.post("/api/tasks", status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.patch("/api/tasks/{task_id}/toggle")
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    task.completed = 0 if task.completed else 1
    db.commit()
    db.refresh(task)
    return task


@app.get("/api/metrics")
def metrics(db: Session = Depends(get_db)):
    leads = db.scalars(select(Lead)).all()
    active = [lead for lead in leads if lead.stage not in {"Won", "Lost"}]
    return {
        "total_leads": len(leads),
        "hot_leads": sum(lead.score >= 70 for lead in leads),
        "pipeline_value": sum(lead.estimated_value for lead in active),
        "meetings": sum(lead.stage == "Meeting" for lead in leads),
        "won_value": sum(lead.estimated_value for lead in leads if lead.stage == "Won"),
    }
