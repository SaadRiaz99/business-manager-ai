from datetime import date

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


class DemoGenerate(BaseModel):
    industry: str = "Cleaning Services"
    location: str = "Austin, Texas"
    service: str = "website redesign and lead automation"
    count: int = Field(default=5, ge=1, le=10)


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    due_date: date | None = None
    priority: str = "Medium"

