# BizPilot AI — Multi-Agent Business Automation

BizPilot AI is a FastAPI MVP that combines CRM, lead scoring, tasks, KPIs, and multi-agent workflow planning for **any business type**.

## Multi-agent automation

Enter a business type (restaurant, school, clinic, shop, agency, e-commerce, services, or a custom category), a goal, and its customer channels. The orchestrator routes the goal to relevant specialists:

- Sales Agent: lead capture, qualification, pipeline, and follow-ups
- Marketing Agent: campaigns, offers, content, and channel measurement
- Operations Agent: workflows, owners, deadlines, and exceptions
- Finance Agent: revenue, costs, invoices, cash flow, and margins
- Customer Support Agent: request classification, draft replies, and escalation

`POST /api/automation/plan` creates and saves the coordinated plan. `GET /api/automation/runs` returns recent plans. The planner is provider-independent, so it works without a paid AI API; its agent interfaces can later use OpenAI, Ollama, or authorized business tools.

## Safety boundary

The MVP plans automation. It does not falsely claim to execute external actions. Messages, payments, refunds, and destructive actions require human approval, and real execution requires authorized tool connections.

## Run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>; API docs are at <http://127.0.0.1:8000/docs>.
