"""
Company Research Agent.

Scrapes the lead's company website and uses LLM to extract structured intel.
In production, you'd also integrate: Clearbit, Apollo, LinkedIn API, Crunchbase.
Those APIs cost $0.01-0.10 per lookup but give richer data than web scraping alone.
"""

from app.agents.base import BaseAgent


class CompanyResearchAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a B2B sales intelligence analyst.
Analyze company information and return JSON with these fields:
- company_summary: 2-3 sentence overview
- industry: primary industry
- estimated_size: employee count range (e.g. "50-200", "1000+")
- key_offerings: array of main products/services
- possible_pain_points: array of likely business challenges
Be factual. If information is limited, make reasonable inferences and note uncertainty."""

    def run(self, company: str, website: str | None = None, notes: str | None = None) -> dict:
        website_text = self._fetch_website_text(website) if website else ""

        user_prompt = f"""Research this company:
Company: {company}
Website: {website or 'Not provided'}
Additional notes: {notes or 'None'}

Website content (if scraped):
{website_text or 'No website content available'}

Provide structured company intelligence."""

        result = self._call_llm(self.SYSTEM_PROMPT, user_prompt)
        return {
            "company_summary": result.get("company_summary"),
            "industry": result.get("industry"),
            "estimated_size": result.get("estimated_size"),
            "key_offerings": result.get("key_offerings", []),
            "possible_pain_points": result.get("possible_pain_points", []),
            "raw_research": result,
        }
