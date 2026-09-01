"""Provider-independent multi-agent workflow planning for any business type."""
from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class AgentResult:
    agent: str
    objective: str
    actions: list[str]
    kpi: str
    requires_approval: bool = False

class BusinessAgent:
    name = "Business Agent"
    keywords: tuple[str, ...] = ()
    def is_relevant(self, goal: str) -> bool:
        return not self.keywords or any(word in goal.lower() for word in self.keywords)
    def run(self, business_type: str, goal: str, channels: list[str]) -> AgentResult:
        raise NotImplementedError

class SalesAgent(BusinessAgent):
    name = "Sales Agent"; keywords = ("sale", "lead", "customer", "revenue", "booking", "order", "client")
    def run(self, business_type, goal, channels):
        return AgentResult(self.name, "Turn demand into trackable opportunities", [f"Define the ideal customer and offer for this {business_type}", "Capture every inquiry in one pipeline and assign a next action", "Prioritize high-intent opportunities and schedule follow-ups"], "Qualified opportunities and conversion rate")

class MarketingAgent(BusinessAgent):
    name = "Marketing Agent"; keywords = ("market", "campaign", "content", "social", "brand", "promot", "lead", "customer")
    def run(self, business_type, goal, channels):
        channel_text = ", ".join(channels) if channels else "the strongest customer channel"
        return AgentResult(self.name, "Create repeatable customer acquisition", [f"Create a clear offer and campaign for {channel_text}", "Prepare a weekly content and promotion calendar", "Track source, cost, response, and conversion for every campaign"], "Qualified leads per channel", True)

class OperationsAgent(BusinessAgent):
    name = "Operations Agent"
    def run(self, business_type, goal, channels):
        return AgentResult(self.name, "Deliver work consistently with fewer manual steps", [f"Map the {business_type} workflow from request to delivery", "Create reusable checklists, owners, deadlines, and exception rules", "Queue recurring work and flag overdue or blocked items"], "On-time completion rate")

class FinanceAgent(BusinessAgent):
    name = "Finance Agent"; keywords = ("cost", "profit", "finance", "invoice", "payment", "fee", "budget", "revenue", "sale")
    def run(self, business_type, goal, channels):
        return AgentResult(self.name, "Protect cash flow and profitability", ["Record expected revenue, costs, invoices, and payment dates", "Review margin and cash-flow exceptions every week", "Prepare reminders for overdue invoices without sending automatically"], "Gross margin and overdue receivables", True)

class SupportAgent(BusinessAgent):
    name = "Customer Support Agent"; keywords = ("support", "customer", "complaint", "message", "parent", "review", "retention", "service")
    def run(self, business_type, goal, channels):
        return AgentResult(self.name, "Respond faster and retain more customers", ["Classify requests by topic, urgency, and sentiment", "Draft approved answers from a reusable business knowledge base", "Escalate complaints, refunds, safety, and unusual requests to a person"], "First-response time and retention", True)

AGENTS = [SalesAgent(), MarketingAgent(), OperationsAgent(), FinanceAgent(), SupportAgent()]

def orchestrate_business(business_type: str, goal: str, channels: list[str]) -> dict:
    selected = [agent for agent in AGENTS if agent.is_relevant(goal)]
    operations = next(agent for agent in AGENTS if isinstance(agent, OperationsAgent))
    if operations not in selected: selected.append(operations)
    if len(selected) == 1: selected = AGENTS
    results = [agent.run(business_type, goal, channels) for agent in selected]
    return {"business_type": business_type, "goal": goal, "status": "plan_ready", "summary": f"{len(results)} specialist agents created a coordinated automation plan.", "agents": [asdict(result) for result in results], "guardrails": ["A human must approve external messages, payments, refunds, and destructive actions.", "Generated plans do not claim that third-party actions were executed.", "Connect authorized business tools before enabling real execution."]}
