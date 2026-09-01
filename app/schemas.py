from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class LeadCreate(BaseModel):
    company: str = Field(min_length=2, max_length=120)
    contact_name: str = ""
    email: str = ""
    website: str = ""
    industry: str = Field(min_length=2, max_length=100)
    location: str = ""
    company_size: str = "small"
    need: str = ""
    stage: str = "New"
    estimated_value: float = Field(default=0, ge=0)
    next_follow_up: date | None = None
    notes: str = ""


class LeadUpdate(BaseModel):
    stage: str | None = None
    estimated_value: float | None = Field(default=None, ge=0)
    next_follow_up: date | None = None
    notes: str | None = None


class LeadOut(LeadCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    score: int
    outreach_draft: str
    temperature: str = ""
    created_at: datetime | None = None


class DemoGenerate(BaseModel):
    industry: str = "Cleaning Services"
    location: str = "Austin, Texas"
    service: str = "website redesign and lead automation"
    count: int = Field(default=5, ge=1, le=10)


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    due_date: date | None = None
    priority: str = "Medium"


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    due_date: date | None = None
    priority: str
    completed: int
    created_at: datetime | None = None


class MetricsOut(BaseModel):
    total_leads: int
    hot_leads: int
    warm_leads: int
    cold_leads: int
    pipeline_value: float
    won_value: float
    meetings: int
    overdue_tasks: int
    total_tasks: int


class AutomationPlanOut(BaseModel):
    id: int
    business_type: str
    goal: str
    status: str
    summary: str
    agents: list[dict]
    guardrails: list[str]
    created_at: datetime | None = None


class AutomationRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_type: str
    business_name: str
    goal: str
    channels: str
    status: str
    created_at: datetime | None = None


class BusinessAutomationRequest(BaseModel):
    business_name: str = Field(default="My Business", min_length=2, max_length=140)
    business_type: str = Field(min_length=2, max_length=100)
    goal: str = Field(min_length=8, max_length=1000)
    channels: list[str] = Field(default_factory=list, max_length=10)
