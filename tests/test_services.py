from app.agents import orchestrate_business
from app.schemas import LeadCreate
from app.services import calculate_lead_score, lead_temperature

def test_complete_lead_is_hot():
    lead=LeadCreate(company="Example Agency",contact_name="Alex",email="alex@example.com",website="https://example.com",industry="Marketing Agency",location="New York",company_size="small",need="Needs a complete automated lead follow-up system",estimated_value=1000)
    score=calculate_lead_score(lead);assert score>=70;assert lead_temperature(score)=="Hot"

def test_any_business_gets_coordinated_plan():
    plan=orchestrate_business("Local School","Automate admissions, parent messages, fees, and reporting",["WhatsApp","Email"])
    names={agent["agent"] for agent in plan["agents"]}
    assert {"Operations Agent","Finance Agent","Customer Support Agent"} <= names
    assert plan["status"]=="plan_ready"

def test_broad_goal_uses_all_specialists():
    plan=orchestrate_business("Custom Manufacturing","Automate the complete business workflow",[])
    assert len(plan["agents"])==5
    assert any(agent["requires_approval"] for agent in plan["agents"])
