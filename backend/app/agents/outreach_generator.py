"""
Personalized Outreach Generator.

Generates first email + 2 follow-ups + LinkedIn message.
This is the core product value — personalized outreach that references
actual research, not generic templates.

ANTI-SPAM: We instruct the LLM to be concise, reference specific findings,
and avoid spam trigger words. In production, add SPF/DKIM checks and
integrate with email warmup services (Instantly, Lemlist).
"""

from app.agents.base import BaseAgent


class OutreachGeneratorAgent(BaseAgent):
    SYSTEM_PROMPT = """You are an expert B2B sales copywriter.
Generate personalized outreach messages. Return JSON with:
- first_email: {subject, body}
- followup_1: {subject, body}
- followup_2: {subject, body}
- linkedin_message: {body}

Rules:
- Keep emails under 150 words
- Reference specific company research findings
- Be conversational, not salesy
- No spam trigger words (free, guarantee, act now)
- Each follow-up adds new value, doesn't just "bump"
- LinkedIn message under 300 characters"""

    def run(
        self,
        lead_data: dict,
        company_research: dict | None = None,
        lead_intelligence: dict | None = None,
        lead_score: dict | None = None,
    ) -> list[dict]:
        user_prompt = f"""Generate outreach for:

Lead: {lead_data.get('name')} — {lead_data.get('role', 'Unknown')} at {lead_data.get('company')}
Company Research: {company_research or 'Limited info'}
Lead Intelligence: {lead_intelligence or 'Limited info'}
Lead Score: {lead_score.get('score') if lead_score else 'Not scored'}

Our product: AI-powered lead response system that helps sales teams
respond to inbound leads instantly with personalized outreach."""

        result = self._call_llm(self.SYSTEM_PROMPT, user_prompt)

        messages = []
        if first := result.get("first_email"):
            messages.append({
                "message_type": "first_email",
                "subject": first.get("subject"),
                "body": first.get("body", ""),
            })
        if fu1 := result.get("followup_1"):
            messages.append({
                "message_type": "followup_1",
                "subject": fu1.get("subject"),
                "body": fu1.get("body", ""),
            })
        if fu2 := result.get("followup_2"):
            messages.append({
                "message_type": "followup_2",
                "subject": fu2.get("subject"),
                "body": fu2.get("body", ""),
            })
        if li := result.get("linkedin_message"):
            messages.append({
                "message_type": "linkedin",
                "subject": None,
                "body": li.get("body", ""),
            })
        return messages
