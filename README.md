# BizPilot AI — Business Manager + Lead Generator

BizPilot AI is a focused SaaS MVP for marketing agencies. It combines a lightweight CRM, sales pipeline, lead scoring, outreach drafting, tasks, and business KPIs in one dashboard.

## Why this product can sell

It connects AI to a measurable result: finding and converting clients. The strongest offer is not “buy my AI,” but “organize your pipeline and help your team follow up with qualified prospects.”

## Included in this MVP

- Dashboard with revenue and pipeline KPIs
- CRM lead creation, editing, deletion, and filtering
- Explainable lead score from 0–100
- Hot/warm/cold lead classification
- Sales stages: New, Qualified, Contacted, Replied, Meeting, Proposal, Won, Lost
- Personalized outreach draft for every lead
- Demo lead generator for sales demonstrations
- Tasks and follow-up dates
- SQLite database with sample data
- Responsive web interface
- REST API powered by FastAPI

> The demo generator creates fictional prospects. It does not scrape or claim to provide verified contact data. Connect a compliant data provider before production use.

## Quick start (Windows PowerShell)

```powershell
cd business-manager-ai
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>. API documentation is available at <http://127.0.0.1:8000/docs>.

## Environment

Copy `.env.example` to `.env`. The current MVP does not require an API key.

## Product roadmap

1. Authenticate users and isolate each workspace.
2. Add CSV import/export and duplicate detection.
3. Connect an approved lead-data provider such as Apollo.
4. Add OpenAI/Ollama outreach personalization using business context.
5. Connect Gmail with review-before-send approval.
6. Add scheduled follow-ups, Google Calendar, subscriptions, and usage limits.

## First sales offer

“I will configure your complete lead pipeline, add your first prospects, and create personalized outreach drafts. Setup is $100 and ongoing access is $49/month.”

See [SELLING_PLAN.md](SELLING_PLAN.md) for the complete launch plan.

## Deploy on Vercel

The repository includes `api/index.py` and `vercel.json` for Vercel's Python runtime.
Connect the repository in Vercel and deploy the `main` branch with the project root set
to the repository root. No build command is required.

Vercel functions have an ephemeral filesystem. The default Vercel deployment therefore
uses `/tmp/bizpilot.db`, which is suitable only for demonstrations and can reset between
function instances. Set `DATABASE_URL` to a managed PostgreSQL connection for persistent
production data.
