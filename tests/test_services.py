from datetime import date, timedelta

import pytest

from app.agents import orchestrate_business
from app.schemas import LeadCreate, TaskCreate
from app.services import build_outreach, calculate_lead_score, demo_leads, lead_temperature


# ---------------------------------------------------------------------------
# Service tests
# ---------------------------------------------------------------------------

class TestCalculateLeadScore:
    def test_minimal_lead(self):
        lead = LeadCreate(company="Acme", industry="Tech")
        score = calculate_lead_score(lead)
        # base=10 + industry=15 + company_size("small")=10 = 35
        assert score == 35

    def test_full_lead(self):
        lead = LeadCreate(
            company="Acme Corp",
            contact_name="Alex",
            email="alex@acme.com",
            website="https://acme.com",
            industry="Marketing",
            location="New York",
            company_size="small",
            need="Needs a complete automated lead follow-up system",
            estimated_value=1000,
        )
        assert calculate_lead_score(lead) == 100

    def test_score_capped_at_100(self):
        lead = LeadCreate(
            company="Big Corp",
            contact_name="Jordan",
            email="jordan@big.com",
            website="https://big.com",
            industry="Finance",
            location="London",
            company_size="medium",
            need="Very long requirement text that exceeds the threshold",
            estimated_value=5000,
        )
        assert calculate_lead_score(lead) == 100


class TestLeadTemperature:
    def test_hot(self):
        assert lead_temperature(70) == "Hot"
        assert lead_temperature(100) == "Hot"

    def test_warm(self):
        assert lead_temperature(45) == "Warm"
        assert lead_temperature(69) == "Warm"

    def test_cold(self):
        assert lead_temperature(0) == "Cold"
        assert lead_temperature(44) == "Cold"


class TestBuildOutreach:
    def test_with_contact(self):
        lead = LeadCreate(
            company="Acme",
            contact_name="Alex",
            industry="Marketing",
            need="automated follow-up",
        )
        result = build_outreach(lead)
        assert "Alex" in result
        assert "acme" in result.lower()

    def test_without_contact(self):
        lead = LeadCreate(company="Acme", industry="Marketing")
        result = build_outreach(lead)
        assert "Acme team" in result

    def test_without_need(self):
        lead = LeadCreate(company="Acme", contact_name="Alex", industry="Marketing")
        result = build_outreach(lead)
        assert "improving your lead follow-up" in result


class TestDemoLeads:
    def test_generates_correct_count(self):
        leads = demo_leads("Cleaning", "Austin", "booking", 3)
        assert len(leads) == 3

    def test_leads_have_correct_industry(self):
        leads = demo_leads("Cleaning", "Austin", "booking", 2)
        for lead in leads:
            assert lead.industry == "Cleaning"

    def test_leads_have_valid_email(self):
        leads = demo_leads("Cleaning", "Austin", "booking", 2)
        for lead in leads:
            assert "@" in lead.email


# ---------------------------------------------------------------------------
# Agent tests
# ---------------------------------------------------------------------------

class TestOrchestrateBusiness:
    def test_coordinated_plan(self):
        plan = orchestrate_business(
            "Local School",
            "Automate admissions, parent messages, fees, and reporting",
            ["WhatsApp", "Email"],
        )
        names = {a["agent"] for a in plan["agents"]}
        assert {"Operations Agent", "Finance Agent", "Customer Support Agent"} <= names
        assert plan["status"] == "plan_ready"

    def test_broad_goal_all_agents(self):
        plan = orchestrate_business(
            "Custom Manufacturing",
            "Automate the complete business workflow",
            [],
        )
        assert len(plan["agents"]) == 5

    def test_plan_has_guardrails(self):
        plan = orchestrate_business("Shop", "increase sales", ["email"])
        assert len(plan["guardrails"]) == 3


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

class TestLeadsAPI:
    def test_list_leads_empty(self, client):
        resp = client.get("/api/leads")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_lead(self, client):
        resp = client.post(
            "/api/leads",
            json={
                "company": "Acme Corp",
                "industry": "Marketing",
                "contact_name": "Alex",
                "email": "alex@acme.com",
                "estimated_value": 500,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["company"] == "Acme Corp"
        assert "score" in data
        assert "temperature" in data
        assert data["temperature"] in ("Hot", "Warm", "Cold")

    def test_list_leads_after_create(self, client):
        client.post(
            "/api/leads",
            json={"company": "Test Inc", "industry": "Tech"},
        )
        resp = client.get("/api/leads")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_leads_filter_by_stage(self, client):
        client.post(
            "/api/leads",
            json={"company": "Alpha Corp", "industry": "Tech", "stage": "New"},
        )
        client.post(
            "/api/leads",
            json={"company": "Beta Corp", "industry": "Tech", "stage": "Won"},
        )
        resp = client.get("/api/leads?stage=Won")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_update_lead(self, client):
        resp = client.post(
            "/api/leads",
            json={"company": "Acme", "industry": "Tech"},
        )
        lead_id = resp.json()["id"]
        resp = client.patch(
            f"/api/leads/{lead_id}",
            json={"stage": "Won", "notes": "Closed deal"},
        )
        assert resp.status_code == 200
        assert resp.json()["stage"] == "Won"

    def test_update_lead_not_found(self, client):
        resp = client.patch("/api/leads/9999", json={"stage": "Won"})
        assert resp.status_code == 404

    def test_delete_lead(self, client):
        resp = client.post(
            "/api/leads",
            json={"company": "Del", "industry": "Tech"},
        )
        lead_id = resp.json()["id"]
        resp = client.delete(f"/api/leads/{lead_id}")
        assert resp.status_code == 204
        assert client.get("/api/leads").json() == []

    def test_delete_lead_not_found(self, client):
        resp = client.delete("/api/leads/9999")
        assert resp.status_code == 404

    def test_generate_demo_leads(self, client):
        resp = client.post(
            "/api/leads/generate",
            json={
                "industry": "Cleaning",
                "location": "Austin",
                "service": "booking",
                "count": 3,
            },
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 3


class TestTasksAPI:
    def test_list_tasks_empty(self, client):
        resp = client.get("/api/tasks")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_task(self, client):
        resp = client.post(
            "/api/tasks",
            json={"title": "Review leads", "priority": "High"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Review leads"
        assert data["completed"] == 0

    def test_toggle_task(self, client):
        resp = client.post(
            "/api/tasks",
            json={"title": "Do something"},
        )
        task_id = resp.json()["id"]
        resp = client.patch(f"/api/tasks/{task_id}/toggle")
        assert resp.status_code == 200
        assert resp.json()["completed"] == 1

    def test_toggle_task_not_found(self, client):
        resp = client.patch("/api/tasks/9999/toggle")
        assert resp.status_code == 404


class TestMetricsAPI:
    def test_metrics_empty(self, client):
        resp = client.get("/api/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_leads"] == 0
        assert data["pipeline_value"] == 0.0

    def test_metrics_with_data(self, client):
        client.post(
            "/api/leads",
            json={
                "company": "Hot Lead",
                "industry": "Marketing",
                "email": "hot@test.com",
                "website": "https://test.com",
                "need": "Very long requirement text",
                "company_size": "small",
                "estimated_value": 1000,
            },
        )
        client.post(
            "/api/tasks",
            json={"title": "Task 1"},
        )
        resp = client.get("/api/metrics")
        data = resp.json()
        assert data["total_leads"] == 1
        assert data["total_tasks"] == 1


class TestAutomationAPI:
    def test_create_plan(self, client):
        resp = client.post(
            "/api/automation/plan",
            json={
                "business_name": "Test Agency",
                "business_type": "Marketing Agency",
                "goal": "Automate lead follow-up and sales pipeline",
                "channels": ["email", "social"],
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "plan_ready"
        assert len(data["agents"]) >= 1
        assert len(data["guardrails"]) == 3

    def test_list_runs_empty(self, client):
        resp = client.get("/api/automation/runs")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_runs_after_create(self, client):
        client.post(
            "/api/automation/plan",
            json={
                "business_name": "Agency",
                "business_type": "Agency",
                "goal": "Improve customer retention and follow-up",
                "channels": ["email"],
            },
        )
        resp = client.get("/api/automation/runs")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
