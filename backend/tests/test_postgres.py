"""Unit tests for PostgreSQL ORM models and session management."""

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import pytest
from app.db.models import (
    ArtifactModel,
    ChunkModel,
    CitationModel,
    ClaimModel,
    DocumentVersionModel,
    EnvironmentModel,
    EvidenceModel,
    ExecutionEnvelopeModel,
    OrganizationModel,
    PolicySnapshotModel,
    ProjectModel,
    ResearchRunModel,
    SourceModel,
    UserModel,
    WorkspaceModel,
)
from app.db.postgres import Base, create_engine_from_url, create_session_factory
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


@pytest.fixture
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated in-memory SQLite async database session for testing."""

    engine = create_engine_from_url("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = create_session_factory(engine)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_tenancy_hierarchy_crud(test_db_session: AsyncSession) -> None:
    """Verify Organization -> Project -> Workspace -> Environment -> User CRUD relationship."""

    org = OrganizationModel(name="Deep Research Corp")
    test_db_session.add(org)
    await test_db_session.commit()

    project = ProjectModel(organization_id=org.id, name="Project Alpha")
    test_db_session.add(project)
    await test_db_session.commit()

    workspace = WorkspaceModel(
        project_id=project.id, name="Default Workspace", quotas={"max_runs": 10}
    )
    test_db_session.add(workspace)
    await test_db_session.commit()

    env = EnvironmentModel(workspace_id=workspace.id, name="production")
    test_db_session.add(env)

    user = UserModel(organization_id=org.id, email="lead@deepresearch.ai", role="admin")
    test_db_session.add(user)
    await test_db_session.commit()

    stmt = (
        select(OrganizationModel)
        .options(selectinload(OrganizationModel.projects).selectinload(ProjectModel.workspaces))
        .where(OrganizationModel.name == "Deep Research Corp")
    )
    result = await test_db_session.scalar(stmt)

    assert result is not None
    assert result.id == org.id
    assert len(result.projects) == 1
    assert result.projects[0].name == "Project Alpha"
    assert len(result.projects[0].workspaces) == 1
    assert result.projects[0].workspaces[0].quotas["max_runs"] == 10


@pytest.mark.asyncio
async def test_execution_and_research_run_creation(test_db_session: AsyncSession) -> None:
    """Verify PolicySnapshot, ExecutionEnvelope, and ResearchRun persistence."""

    org = OrganizationModel(name="Org Beta")
    test_db_session.add(org)
    await test_db_session.commit()

    project = ProjectModel(organization_id=org.id, name="Proj Beta")
    test_db_session.add(project)
    await test_db_session.commit()

    workspace = WorkspaceModel(project_id=project.id, name="WS Beta")
    test_db_session.add(workspace)
    await test_db_session.commit()

    env = EnvironmentModel(workspace_id=workspace.id, name="dev")
    user = UserModel(organization_id=org.id, email="user@beta.ai")
    policy = PolicySnapshotModel(policy_id="default_v1", version="1.0.0", digest="sha256:12345")
    test_db_session.add_all([env, user, policy])
    await test_db_session.commit()

    envelope = ExecutionEnvelopeModel(
        principal_id=user.id,
        organization_id=org.id,
        project_id=project.id,
        workspace_id=workspace.id,
        environment_id=env.id,
        policy_snapshot_id=policy.id,
        idempotency_key="idemp_run_001",
        correlation_id="corr_run_001",
        deadline=datetime.now(UTC) + timedelta(hours=2),
        budget={"tokens": 50000},
    )
    test_db_session.add(envelope)
    await test_db_session.commit()

    run = ResearchRunModel(
        execution_id=envelope.id,
        workspace_id=workspace.id,
        title="Autonomous AI Platform Analysis",
        objective="Analyze modern deep research architecture patterns",
    )
    test_db_session.add(run)
    await test_db_session.commit()

    fetched_run = await test_db_session.scalar(
        select(ResearchRunModel).where(ResearchRunModel.id == run.id)
    )
    assert fetched_run is not None
    assert fetched_run.status == "pending"
    assert fetched_run.stage == "intake"
    assert fetched_run.execution_id == envelope.id


@pytest.mark.asyncio
async def test_knowledge_plane_entities(test_db_session: AsyncSession) -> None:
    """Verify Artifact, Source, DocumentVersion, Chunk, Claim, Evidence, and Citation ORM chain."""

    org = OrganizationModel(name="Org Gamma")
    test_db_session.add(org)
    await test_db_session.commit()

    proj = ProjectModel(organization_id=org.id, name="Proj Gamma")
    test_db_session.add(proj)
    await test_db_session.commit()

    ws = WorkspaceModel(project_id=proj.id, name="WS Gamma")
    test_db_session.add(ws)
    await test_db_session.commit()

    artifact = ArtifactModel(
        uri="s3://research/docs/v1.pdf",
        content_hash="hash_pdf_123",
        media_type="application/pdf",
    )
    source = SourceModel(
        workspace_id=ws.id,
        url="https://arxiv.org/abs/2401.00001",
        title="Deep Research Systems Architecture",
    )
    test_db_session.add_all([artifact, source])
    await test_db_session.commit()

    doc_version = DocumentVersionModel(
        source_id=source.id,
        artifact_id=artifact.id,
        version_number=1,
        mime_type="application/pdf",
    )
    test_db_session.add(doc_version)
    await test_db_session.commit()

    chunk = ChunkModel(
        document_version_id=doc_version.id,
        chunk_index=0,
        text_content="Autonomous agents require explicit execution envelopes and durable state.",
    )
    test_db_session.add(chunk)
    await test_db_session.commit()

    claim = ClaimModel(
        chunk_id=chunk.id,
        claim_text="Agents must run inside execution envelopes.",
        confidence=0.98,
    )
    test_db_session.add(claim)
    await test_db_session.commit()

    evidence = EvidenceModel(
        claim_id=claim.id,
        source_span="Autonomous agents require explicit execution envelopes",
        citation_eligible=True,
    )
    test_db_session.add(evidence)
    await test_db_session.commit()

    citation = CitationModel(
        evidence_id=evidence.id,
        formatted_citation="[1] Deep Research Systems Architecture, Section 2.",
    )
    test_db_session.add(citation)
    await test_db_session.commit()

    fetched_citation = await test_db_session.scalar(
        select(CitationModel).where(CitationModel.id == citation.id)
    )
    assert fetched_citation is not None
    assert "[1]" in fetched_citation.formatted_citation
