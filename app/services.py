from .schemas import LeadCreate


def calculate_lead_score(lead: LeadCreate) -> int:
    score = 10
    if lead.industry.strip():
        score += 15
    if lead.location.strip():
        score += 10
    if lead.website.strip():
        score += 10
    if lead.email.strip() and "@" in lead.email:
        score += 15
    if len(lead.need.strip()) >= 15:
        score += 20
    if lead.company_size.lower() in {"small", "medium", "2-10", "11-50"}:
        score += 10
    if lead.estimated_value >= 500:
        score += 10
    return min(score, 100)


def lead_temperature(score: int) -> str:
    if score >= 70:
        return "Hot"
    if score >= 45:
        return "Warm"
    return "Cold"


def build_outreach(lead: LeadCreate) -> str:
    contact = lead.contact_name.strip() or f"{lead.company} team"
    opportunity = lead.need.strip() or "improving your lead follow-up process"
    return (
        f"Hi {contact}, I came across {lead.company} and noticed an opportunity "
        f"around {opportunity}. I help {lead.industry.lower()} businesses organize "
        f"leads and turn more inquiries into booked calls. Would you be open to a "
        f"short, personalized demo?"
    )


def demo_leads(industry: str, location: str, service: str, count: int) -> list[LeadCreate]:
    prefixes = [
        "Bright", "Northstar", "Prime", "Evergreen", "Bluebird",
        "Summit", "Urban", "Trusted", "Apex", "Golden",
    ]
    results = []
    for index in range(count):
        company = f"{prefixes[index]} {industry.split()[0].title()} Co."
        slug = company.lower().replace(" ", "-").replace(".", "")
        results.append(
            LeadCreate(
                company=company,
                contact_name=["Alex", "Jordan", "Taylor", "Morgan", "Casey"][index % 5],
                email=f"hello@{slug}.example",
                website=f"https://{slug}.example",
                industry=industry,
                location=location,
                company_size="small" if index % 2 == 0 else "medium",
                need=f"May benefit from {service}; fictional demo prospect requiring verification.",
                estimated_value=500 + index * 250,
            )
        )
    return results
