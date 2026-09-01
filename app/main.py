import json
from contextlib import asynccontextmanager
from datetime import date, timedelta
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .agents import orchestrate_business
from .database import Base, SessionLocal, engine, get_db
from .models import AutomationRun, Lead, Task
from .schemas import (
    AutomationPlanOut,
    AutomationRunOut,
    BusinessAutomationRequest,
    DemoGenerate,
    LeadCreate,
    LeadOut,
    LeadUpdate,
    MetricsOut,
    TaskCreate,
    TaskOut,
)
from .services import (
    build_outreach,
    calculate_lead_score,
    demo_leads,
    lead_temperature,
)

BASE_DIR = Path(__file__).resolve().parent


def _seed_database() -> None:
    with SessionLocal() as db:
        if db.scalar(select(func.count(Lead.id))) == 0:
            stages = ["New", "Qualified", "Contacted", "Meeting"]
            for index, item in enumerate(
                demo_leads("Cleaning Services", "Austin, Texas", "online booking and lead follow-up", 4)
            ):
                values = item.model_dump()
                values["stage"] = stages[index]
                db.add(
                    Lead(
                        **values,
                        score=calculate_lead_score(item),
                        outreach_draft=build_outreach(item),
                    )
                )
            db.add(
                Task(title="Review hot leads", due_date=date.today(), priority="High")
            )
            db.add(
                Task(
                    title="Follow up after demo",
                    due_date=date.today() + timedelta(days=2),
                    priority="Medium",
                )
            )
            db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    _seed_database()
    yield


app = FastAPI(title="BizPilot AI", version="0.3.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return HTMLResponse(content=f"Internal Server Error: {exc}", status_code=500)


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ---------------------------------------------------------------------------
# Leads
# ---------------------------------------------------------------------------

@app.get("/api/leads", response_model=list[LeadOut])
def list_leads(stage: str | None = None, db: Session = Depends(get_db)):
    query = select(Lead).order_by(Lead.score.desc(), Lead.created_at.desc())
    if stage:
        query = query.where(Lead.stage == stage)
    leads = db.scalars(query).all()
    result = []
    for lead in leads:
        out = LeadOut.model_validate(lead)
        out.temperature = lead_temperature(lead.score)
        result.append(out)
    return result


@app.post("/api/leads", response_model=LeadOut, status_code=201)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(
        **payload.model_dump(),
        score=calculate_lead_score(payload),
        outreach_draft=build_outreach(payload),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    out = LeadOut.model_validate(lead)
    out.temperature = lead_temperature(lead.score)
    return out


@app.patch("/api/leads/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: int, payload: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)
    db.commit()
    db.refresh(lead)
    out = LeadOut.model_validate(lead)
    out.temperature = lead_temperature(lead.score)
    return out


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
        lead = Lead(
            **item.model_dump(),
            score=calculate_lead_score(item),
            outreach_draft=build_outreach(item),
        )
        db.add(lead)
        created.append(lead)
    db.commit()
    result = []
    for lead in created:
        db.refresh(lead)
        out = LeadOut.model_validate(lead)
        out.temperature = lead_temperature(lead.score)
        result.append(out)
    return result


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@app.get("/api/tasks", response_model=list[TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.scalars(select(Task).order_by(Task.completed, Task.due_date)).all()
    return [TaskOut.model_validate(t) for t in tasks]


@app.post("/api/tasks", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


@app.patch("/api/tasks/{task_id}/toggle", response_model=TaskOut)
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    task.completed = 0 if task.completed else 1
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

@app.get("/api/metrics", response_model=MetricsOut)
def metrics(db: Session = Depends(get_db)):
    total_leads = db.scalar(select(func.count(Lead.id))) or 0
    hot_leads = db.scalar(
        select(func.count(Lead.id)).where(Lead.score >= 70)
    ) or 0
    warm_leads = db.scalar(
        select(func.count(Lead.id)).where(Lead.score >= 45, Lead.score < 70)
    ) or 0
    cold_leads = db.scalar(
        select(func.count(Lead.id)).where(Lead.score < 45)
    ) or 0
    pipeline_value = db.scalar(
        select(func.coalesce(func.sum(Lead.estimated_value), 0.0)).where(
            Lead.stage.notin_(["Won", "Lost"])
        )
    ) or 0.0
    won_value = db.scalar(
        select(func.coalesce(func.sum(Lead.estimated_value), 0.0)).where(
            Lead.stage == "Won"
        )
    ) or 0.0
    meetings = db.scalar(
        select(func.count(Lead.id)).where(Lead.stage == "Meeting")
    ) or 0
    total_tasks = db.scalar(select(func.count(Task.id))) or 0
    overdue_tasks = db.scalar(
        select(func.count(Task.id)).where(
            Task.due_date < date.today(), Task.completed == 0
        )
    ) or 0

    return MetricsOut(
        total_leads=total_leads,
        hot_leads=hot_leads,
        warm_leads=warm_leads,
        cold_leads=cold_leads,
        pipeline_value=float(pipeline_value),
        won_value=float(won_value),
        meetings=meetings,
        overdue_tasks=overdue_tasks,
        total_tasks=total_tasks,
    )


# ---------------------------------------------------------------------------
# Multi-Agent Automation
# ---------------------------------------------------------------------------

@app.post("/api/automation/plan", response_model=AutomationPlanOut, status_code=201)
def create_automation_plan(
    payload: BusinessAutomationRequest, db: Session = Depends(get_db)
):
    plan = orchestrate_business(payload.business_type, payload.goal, payload.channels)
    run = AutomationRun(
        business_type=payload.business_type,
        business_name=payload.business_name,
        goal=payload.goal,
        channels=",".join(payload.channels),
        plan_json=json.dumps(plan),
        status=plan["status"],
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return AutomationPlanOut(
        id=run.id,
        business_type=run.business_type,
        goal=run.goal,
        status=run.status,
        summary=plan["summary"],
        agents=plan["agents"],
        guardrails=plan["guardrails"],
        created_at=run.created_at,
    )


@app.get("/api/automation/runs", response_model=list[AutomationRunOut])
def list_automation_runs(db: Session = Depends(get_db)):
    runs = db.scalars(
        select(AutomationRun).order_by(AutomationRun.created_at.desc()).limit(20)
    ).all()
    return [AutomationRunOut.model_validate(run) for run in runs]
