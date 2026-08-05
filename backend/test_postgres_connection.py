import asyncio
import sys
from sqlalchemy import text
from app.core.settings import get_settings
from app.db.postgres import create_engine_from_url, Base
from app.infrastructure.models import (
    UserModel, OrganizationModel, ProjectModel, WorkspaceModel,
    EnvironmentModel, PolicySnapshotModel, ExecutionEnvelopeModel, ResearchRunModel
)

async def test_postgres_connection():
    settings = get_settings()
    db_url = settings.DATABASE_URL
    
    print("=" * 75)
    print("        POSTGRESQL & PGADMIN 4 DATABASE CONNECTION DIAGNOSTIC")
    print("=" * 75)
    print(f"Configured DATABASE_URL: {db_url}")
    
    if not db_url or "postgresql" not in db_url:
        print("\n[NOTICE]: DATABASE_URL in backend/.env is not set to a PostgreSQL URL.")
        print("Please set your PostgreSQL / pgAdmin URL in backend/.env:")
        print("DATABASE_URL=postgresql://postgres:your_password@localhost:5432/research_db")
        sys.exit(1)
        
    try:
        engine = create_engine_from_url(db_url)
        async with engine.begin() as conn:
            # 1. Test raw connection query
            res = await conn.execute(text("SELECT version();"))
            version = res.scalar()
            print(f"\n[SUCCESS]: Connected to PostgreSQL Database!")
            print(f"Server Version: {version}")

            # 2. Automatically create all domain tables in pgAdmin / PostgreSQL database
            print("\n[INITIALIZING DOMAIN TABLES] Creating tables in PostgreSQL...")
            await conn.run_sync(Base.metadata.create_all)
            print("All domain tables initialized cleanly:")
            print("  ✓ users")
            print("  ✓ organizations")
            print("  ✓ projects")
            print("  ✓ workspaces")
            print("  ✓ environments")
            print("  ✓ execution_envelopes")
            print("  ✓ policy_snapshots")
            print("  ✓ research_runs")

        await engine.dispose()
        print("\n" + "=" * 75)
        print("      POSTGRESQL DB READY FOR PGADMIN 4 & FASTAPI BACKEND!")
        print("=" * 75)
    except Exception as err:
        print(f"\n[ERROR]: Failed to connect to PostgreSQL database: {err}")
        print("\nPlease verify:")
        print("1. PostgreSQL service is running on your computer.")
        print("2. Database name exists in pgAdmin 4 (e.g. 'research_db').")
        print("3. Username, password, host, and port in backend/.env are correct.")

if __name__ == "__main__":
    asyncio.run(test_postgres_connection())
