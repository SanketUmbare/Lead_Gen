"""
Lead Intelligence Agent.

Analyzes the individual's role to estimate buying authority and goals.
This is where you differentiate from generic email tools — understanding
WHO the lead is, not just WHAT company they work at.
"""

from app.agents.base import BaseAgent


class LeadIntelligenceAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a B2B buyer persona analyst.
Analyze the lead's role and return JSON with:
- probable_goals: array of likely professional goals
- probable_challenges: array of role-specific challenges
- buying_authority: one of "decision_maker", "influencer", "user", "unknown"
- authority_score: float 0.0-1.0 indicating purchasing influence
Base analysis on title patterns: C-suite/VP = high authority, IC = low."""

    def run(
        self,
        name: str,
        role: str | None,
        company: str,
        company_research: dict | None = None,
    ) -> dict:
        research_context = ""
        if company_research:
            research_context = f"""
Company context:
- Industry: {company_research.get('industry', 'Unknown')}
- Size: {company_research.get('estimated_size', 'Unknown')}
- Pain points: {company_research.get('possible_pain_points', [])}"""

        user_prompt = f"""Analyze this lead:
Name: {name}
Role/Title: {role or 'Not provided'}
Company: {company}
{research_context}

Provide lead intelligence analysis."""

        result = self._call_llm(self.SYSTEM_PROMPT, user_prompt)
        return {
            "probable_goals": result.get("probable_goals", []),
            "probable_challenges": result.get("probable_challenges", []),
            "buying_authority": result.get("buying_authority", "unknown"),
            "authority_score": result.get("authority_score", 0.0),
            "raw_analysis": result,
        }
