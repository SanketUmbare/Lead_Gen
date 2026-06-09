"""
Lead processing pipeline — the core async workflow.

Pipeline: Company Research → Lead Intelligence → Scoring → Outreach → Summary

FAILURE MODES:
- OpenAI rate limit → retry with backoff (handled by tenacity)
- Website unreachable → proceed with limited data
- Any agent fails → lead status = FAILED, logged for manual review
- Partial success → store what we have, mark as READY with warnings

MONITORING: Log duration per stage. Alert if p95 > 60s or failure rate > 5%.
"""

from uuid import UUID

from app.agents.company_research import CompanyResearchAgent
from app.agents.lead_intelligence import LeadIntelligenceAgent
from app.agents.lead_scoring import LeadScoringAgent
from app.agents.outreach_generator import OutreachGeneratorAgent
from app.agents.summary_generator import SummaryGeneratorAgent
from app.core.logging import get_logger
from app.db.models import LeadStatus
from app.db.repositories.lead_repository import LeadRepository
from app.db.session import SessionLocal
from app.tasks.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(bind=True, name="process_lead")
def process_lead_task(self, lead_id: str):
    db = SessionLocal()
    repo = LeadRepository(db)
    lead = repo.get_by_id(UUID(lead_id))

    if not lead:
        logger.error("lead_not_found", lead_id=lead_id)
        return {"status": "error", "message": "Lead not found"}

    try:
        repo.update_status(lead, LeadStatus.RESEARCHING)
        repo.log_activity(lead.id, "processing_started", "AI pipeline initiated")

        lead_data = {
            "name": lead.name,
            "email": lead.email,
            "company": lead.company,
            "role": lead.role,
            "website": lead.website,
            "notes": lead.notes,
        }

        # Stage 1: Company Research
        logger.info("stage_company_research", lead_id=lead_id)
        company_agent = CompanyResearchAgent()
        company_result = company_agent.run(
            company=lead.company, website=lead.website, notes=lead.notes
        )
        repo.save_company_research(lead.id, company_result)
        repo.log_activity(lead.id, "company_researched", "Company research completed")

        # Stage 2: Lead Intelligence
        logger.info("stage_lead_intelligence", lead_id=lead_id)
        intel_agent = LeadIntelligenceAgent()
        intel_result = intel_agent.run(
            name=lead.name,
            role=lead.role,
            company=lead.company,
            company_research=company_result,
        )
        repo.save_lead_intelligence(lead.id, intel_result)
        repo.log_activity(lead.id, "intelligence_analyzed", "Lead intelligence completed")

        repo.update_status(lead, LeadStatus.ANALYZED)

        # Stage 3: Lead Scoring
        logger.info("stage_lead_scoring", lead_id=lead_id)
        scoring_agent = LeadScoringAgent()
        score_result = scoring_agent.run(
            lead_data=lead_data,
            company_research=company_result,
            lead_intelligence=intel_result,
        )
        repo.save_lead_score(lead.id, score_result)
        repo.log_activity(
            lead.id,
            "lead_scored",
            f"Lead scored {score_result['score']}/100",
            metadata={"score": score_result["score"]},
        )

        # Stage 4: Outreach Generation
        logger.info("stage_outreach", lead_id=lead_id)
        outreach_agent = OutreachGeneratorAgent()
        messages = outreach_agent.run(
            lead_data=lead_data,
            company_research=company_result,
            lead_intelligence=intel_result,
            lead_score=score_result,
        )
        repo.save_outreach_messages(lead.id, messages)
        repo.log_activity(
            lead.id, "outreach_generated", f"{len(messages)} messages created"
        )

        # Stage 5: AI Summary
        logger.info("stage_summary", lead_id=lead_id)
        summary_agent = SummaryGeneratorAgent()
        summary_result = summary_agent.run(
            lead_data=lead_data,
            company_research=company_result,
            lead_intelligence=intel_result,
            lead_score=score_result,
        )
        repo.save_ai_summary(lead.id, summary_result)
        repo.log_activity(lead.id, "summary_generated", "AI summary created")

        repo.update_status(lead, LeadStatus.READY)
        logger.info("processing_complete", lead_id=lead_id, score=score_result["score"])
        return {"status": "success", "lead_id": lead_id, "score": score_result["score"]}

    except Exception as e:
        logger.error("processing_failed", lead_id=lead_id, error=str(e))
        repo.update_status(lead, LeadStatus.FAILED)
        repo.log_activity(lead.id, "processing_failed", str(e))
        raise self.retry(exc=e)
    finally:
        db.close()
