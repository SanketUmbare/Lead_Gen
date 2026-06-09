"""
Lead Scoring Engine.

Scores 0-100 based on company size, role seniority, industry fit, and engagement.
Scoring is your pricing lever — agencies pay more for leads scored >80
because those convert 3-5x better than cold outreach.
"""

from app.agents.base import BaseAgent


class LeadScoringAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a lead scoring engine for B2B SaaS sales.
Score leads 0-100 and return JSON with:
- score: integer 0-100
- reasoning: 2-3 sentence explanation
- factors: object with sub-scores:
  - company_size: 0-25
  - relevance: 0-25
  - role_seniority: 0-25
  - industry_fit: 0-25

Scoring guidelines:
- Larger companies score higher (more budget)
- Decision makers score higher than ICs
- Target industries: agencies, consultancies, SaaS, cybersecurity, manufacturing
- Leads with websites and detailed notes score higher (more engagement)"""

    def run(
        self,
        lead_data: dict,
        company_research: dict | None = None,
        lead_intelligence: dict | None = None,
    ) -> dict:
        user_prompt = f"""Score this lead:

Lead: {lead_data.get('name')} ({lead_data.get('role', 'Unknown role')})
Company: {lead_data.get('company')}
Email: {lead_data.get('email')}
Website: {lead_data.get('website', 'None')}
Notes: {lead_data.get('notes', 'None')}

Company Research: {company_research or 'Not available'}
Lead Intelligence: {lead_intelligence or 'Not available'}

Provide lead score with reasoning."""

        result = self._call_llm(self.SYSTEM_PROMPT, user_prompt)
        score = max(0, min(100, int(result.get("score", 0))))
        return {
            "score": score,
            "reasoning": result.get("reasoning"),
            "factors": result.get("factors", {}),
        }
