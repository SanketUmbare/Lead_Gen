"""
AI Summary Generator.

Produces the executive summary shown on the dashboard.
Sales reps glance at this in 10 seconds to decide: call now, email, or skip.
"""

from app.agents.base import BaseAgent


class SummaryGeneratorAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a sales intelligence summarizer.
Return JSON with:
- lead_summary: 2-3 sentence overview of the lead
- opportunity_summary: business opportunity assessment
- recommended_action: specific next step (e.g. "Schedule demo call within 24h")"""

    def run(
        self,
        lead_data: dict,
        company_research: dict | None = None,
        lead_intelligence: dict | None = None,
        lead_score: dict | None = None,
    ) -> dict:
        user_prompt = f"""Summarize this lead opportunity:

Lead: {lead_data}
Company Research: {company_research or 'N/A'}
Lead Intelligence: {lead_intelligence or 'N/A'}
Lead Score: {lead_score or 'N/A'}

Provide executive summary."""

        result = self._call_llm(self.SYSTEM_PROMPT, user_prompt)
        return {
            "lead_summary": result.get("lead_summary"),
            "opportunity_summary": result.get("opportunity_summary"),
            "recommended_action": result.get("recommended_action"),
        }
