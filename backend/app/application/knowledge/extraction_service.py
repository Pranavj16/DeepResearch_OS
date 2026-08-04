"""Factual claim extraction, evidence span linkage, and citation verification service."""

from uuid import UUID

from app.db.models import CitationModel, ClaimModel, EvidenceModel
from sqlalchemy.ext.asyncio import AsyncSession


class ExtractionService:
    """Service managing factual claim extraction, evidence linking, and citation formatting."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_claim_with_evidence(
        self,
        chunk_id: UUID,
        claim_text: str,
        source_span: str,
        confidence: float = 1.0,
        formatted_citation: str | None = None,
    ) -> tuple[ClaimModel, EvidenceModel, CitationModel | None]:
        """Create a claim record linked to an exact source evidence span and citation."""

        claim = ClaimModel(
            chunk_id=chunk_id,
            claim_text=claim_text,
            confidence=confidence,
        )
        self._session.add(claim)
        await self._session.flush()

        evidence = EvidenceModel(
            claim_id=claim.id,
            source_span=source_span,
            citation_eligible=True,
        )
        self._session.add(evidence)
        await self._session.flush()

        citation = None
        if formatted_citation:
            citation = CitationModel(
                evidence_id=evidence.id,
                formatted_citation=formatted_citation,
            )
            self._session.add(citation)
            await self._session.flush()

        await self._session.commit()
        return claim, evidence, citation


__all__ = ["ExtractionService"]
