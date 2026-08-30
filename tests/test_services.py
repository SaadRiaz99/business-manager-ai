from app.schemas import LeadCreate
from app.services import calculate_lead_score, lead_temperature


def test_complete_lead_is_hot():
    lead = LeadCreate(
        company="Example Agency",
        contact_name="Alex",
        email="alex@example.com",
        website="https://example.com",
        industry="Marketing Agency",
        location="New York",
        company_size="small",
        need="Needs a complete automated lead follow-up system",
        estimated_value=1000,
    )
    score = calculate_lead_score(lead)
    assert score >= 70
    assert lead_temperature(score) == "Hot"

