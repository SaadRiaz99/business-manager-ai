# BizPilot AI — Business Manager + Lead Generator

BizPilot AI is a focused SaaS MVP for marketing agencies. It combines a lightweight CRM, sales pipeline, lead scoring, outreach drafting, tasks, and business KPIs in one dashboard.

## Purpose of the project

Small agencies and freelancers often manage prospects in spreadsheets, WhatsApp chats, and memory. This causes missed follow-ups and lost sales. BizPilot AI puts leads, priorities, next actions, outreach drafts, and pipeline value in one place so the owner can focus on closing clients.

The product is designed to answer four daily questions:

1. Which lead should I contact first?
2. What should I say to that lead?
3. Who needs a follow-up today?
4. How much potential revenue is in my pipeline?

## Benefits for the business owner

- Saves time by keeping leads, notes, tasks, and follow-ups together.
- Highlights hot prospects using a transparent 0–100 lead score.
- Reduces missed opportunities by showing the next action and follow-up date.
- Produces personalized outreach drafts faster than writing every message manually.
- Makes sales activity measurable through pipeline, conversion, and revenue KPIs.
- Gives a small team a repeatable sales process without buying a large enterprise CRM.

## Why a client may be interested

A client is not buying another dashboard; they are buying a simpler way to win more business. The strongest reasons to purchase are:

- They have leads but do not follow up consistently.
- Their prospect information is scattered across several tools.
- They cannot quickly identify which opportunities are most valuable.
- Their team spends too much time writing similar outreach messages.
- They want visibility into deals, expected revenue, and team priorities.
- They need an affordable CRM that can be configured for their workflow.

## Questions to ask a potential client

Use these discovery questions before offering a demo:

1. How do you currently store and track new leads?
2. How many leads do you receive in a typical month?
3. What usually causes a good lead to be lost?
4. How does your team decide which prospect to contact first?
5. How much time do you spend writing outreach and follow-up messages?
6. Do team members ever miss follow-up dates or contact the same lead twice?
7. Which sales stages do you use from first contact to closed deal?
8. Which numbers do you check to understand sales performance?
9. What tools are you using now, and what do you dislike about them?
10. If this system saved five hours or helped close one extra client per month, what would that be worth to you?

## Good customer profile

The best early customers are marketing agencies, web-development studios, consultants, recruiters, and other service businesses with 20–500 active prospects that need a simple, organized follow-up system.

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
