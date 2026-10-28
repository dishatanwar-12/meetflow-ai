import asyncio
import os
import sys
from datetime import datetime, date, timedelta, timezone

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.core.security import get_password_hash
from backend.app.models.user import Organization, User, UserRole
from backend.app.models.client import Client
from backend.app.models.project import Project, ProjectStatus
from backend.app.models.meeting import Meeting, MeetingStatus, MeetingType, MeetingAttendee
from backend.app.models.decision import Decision, DecisionStatus
from backend.app.models.task import Task, TaskStatus, TaskPriority, OwnerStatus, DueDateStatus
from backend.app.models.risk import Risk, RiskStatus
from backend.app.models.blocker import BlockerDependency
from backend.app.models.question import UnansweredQuestion, QuestionStatus
from sqlalchemy import select

async def seed():
    print("Initializing tables...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        res = await db.execute(select(Organization).where(Organization.slug == "acme-solutions"))
        if res.scalar_one_or_none():
            print("Database already contains seed data. Skipping.")
            return

        print("Seeding demo organization and users...")
        org = Organization(name="Acme Enterprise Solutions", slug="acme-solutions")
        db.add(org)
        await db.commit()
        await db.refresh(org)

        admin = User(
            organization_id=org.id,
            email="admin@acme.com",
            hashed_password=get_password_hash("AdminPass123!"),
            full_name="Alice Admin",
            role=UserRole.ADMIN,
            is_active=True
        )
        pm = User(
            organization_id=org.id,
            email="pm@acme.com",
            hashed_password=get_password_hash("PMPass123!"),
            full_name="Peter ProjectManager",
            role=UserRole.PROJECT_MANAGER,
            is_active=True
        )
        member = User(
            organization_id=org.id,
            email="member@acme.com",
            hashed_password=get_password_hash("MemberPass123!"),
            full_name="Mike Member",
            role=UserRole.MEMBER,
            is_active=True
        )
        viewer = User(
            organization_id=org.id,
            email="viewer@acme.com",
            hashed_password=get_password_hash("ViewerPass123!"),
            full_name="Victor Viewer",
            role=UserRole.VIEWER,
            is_active=True
        )
        db.add_all([admin, pm, member, viewer])
        await db.commit()

        print("Seeding clients and projects...")
        client1 = Client(
            organization_id=org.id,
            name="Stark Industries",
            organization_name="Stark Global",
            contact_name="Tony Stark",
            contact_email="tony@stark.com",
            industry="Aerospace & Defense"
        )
        client2 = Client(
            organization_id=org.id,
            name="Initech Global",
            organization_name="Initech Corporation",
            contact_name="Peter Gibbons",
            contact_email="peter@initech.com",
            industry="Financial Services"
        )
        db.add_all([client1, client2])
        await db.commit()
        await db.refresh(client1)
        await db.refresh(client2)

        proj1 = Project(
            organization_id=org.id,
            client_id=client1.id,
            name="Arc Reactor Monitoring Platform",
            description="Real-time telemetry and predictive anomaly detection.",
            manager_id=pm.id,
            status=ProjectStatus.ACTIVE,
            start_date=date(2026, 10, 1),
            target_date=date(2026, 12, 31),
            tags=["iot", "telemetry", "ai"]
        )
        proj2 = Project(
            organization_id=org.id,
            client_id=client2.id,
            name="Automated TPS Reporting Migration",
            description="Modernize legacy reporting batch jobs to cloud streaming.",
            manager_id=pm.id,
            status=ProjectStatus.ACTIVE,
            tags=["migration", "cloud"]
        )
        db.add_all([proj1, proj2])
        await db.commit()
        await db.refresh(proj1)
        await db.refresh(proj2)

        print("Seeding sample meeting and structured outcomes...")
        meeting_dt = datetime.now(timezone.utc) - timedelta(days=2)
        raw_notes = """Tony Stark: We need to ensure the telemetry dashboard responds in sub-50ms latency.
Peter Gibbons: Agreed. We approved migrating the storage backend to PostgreSQL.
Sarah: Priya will optimize the database indexing by Friday.
Tony: We should try to update the mobile client sometime next month, but who will own it?
Peter: We might move the production launch to December if the security audit takes longer."""

        meeting = Meeting(
            organization_id=org.id,
            client_id=client1.id,
            project_id=proj1.id,
            title="Telemetry Architecture Review",
            description="Weekly alignment on database throughput and dashboard latency.",
            meeting_date=meeting_dt,
            timezone="America/New_York",
            meeting_type=MeetingType.STATUS_UPDATE,
            language="en",
            status=MeetingStatus.REVIEWED,
            raw_transcript=raw_notes,
            summary_data={
                "meeting_summary": "Team aligned on sub-50ms latency targets. Approved PostgreSQL migration. Identified open question regarding mobile client ownership.",
                "topics": ["Telemetry Latency", "Database Migration", "Mobile Client", "Launch Schedule"]
            },
            analysis_warnings=[
                "Task 'Update mobile client' has no assigned owner in source notes.",
                "Proposal to move launch to December is unconfirmed."
            ]
        )
        db.add(meeting)
        await db.commit()
        await db.refresh(meeting)

        # Attendees
        att1 = MeetingAttendee(meeting_id=meeting.id, name="Tony Stark", email="tony@stark.com", role="Client Sponsor")
        att2 = MeetingAttendee(meeting_id=meeting.id, name="Peter Gibbons", email="peter@initech.com", role="Project Lead")
        att3 = MeetingAttendee(meeting_id=meeting.id, name="Priya Sharma", email="priya@acme.com", role="Database Engineer")
        db.add_all([att1, att2, att3])
        await db.commit()

        # Decisions
        dec1 = Decision(
            meeting_id=meeting.id,
            project_id=proj1.id,
            title="Migrate Telemetry Storage to PostgreSQL",
            description="Approved migrating storage backend to PostgreSQL for native JSONB and relational integrity.",
            status=DecisionStatus.CONFIRMED,
            owner_or_approver="Peter Gibbons",
            evidence_passage="We approved migrating the storage backend to PostgreSQL.",
            confirmation_required=False
        )
        dec2 = Decision(
            meeting_id=meeting.id,
            project_id=proj1.id,
            title="Consider moving launch to December",
            description="Tentative proposal discussed in the event of audit delays.",
            status=DecisionStatus.PROPOSED,
            evidence_passage="We might move the production launch to December if the security audit takes longer.",
            confirmation_required=True
        )
        db.add_all([dec1, dec2])

        # Tasks
        task1 = Task(
            meeting_id=meeting.id,
            project_id=proj1.id,
            title="Optimize database indexing",
            description="Review index coverage for sub-50ms latency queries.",
            owner_name="Priya Sharma",
            owner_status=OwnerStatus.EXPLICIT,
            due_date=(meeting_dt + timedelta(days=3)).date(),
            due_date_status=DueDateStatus.RESOLVED_FROM_MEETING_DATE,
            date_expression="by Friday",
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            evidence_passage="Priya will optimize the database indexing by Friday.",
            confirmation_required=False
        )
        task2 = Task(
            meeting_id=meeting.id,
            project_id=proj1.id,
            title="Update mobile client telemetry view",
            description="Implement new latency widgets on iOS/Android.",
            owner_name=None,
            owner_status=OwnerStatus.NOT_STATED,
            due_date=None,
            due_date_status=DueDateStatus.AMBIGUOUS,
            date_expression="sometime next month",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.NEEDS_CLARIFICATION,
            evidence_passage="We should try to update the mobile client sometime next month, but who will own it?",
            confirmation_required=True,
            confirmation_reason="No owner assigned; date expression 'sometime next month' requires confirmation."
        )
        db.add_all([task1, task2])

        # Risks
        risk1 = Risk(
            meeting_id=meeting.id,
            project_id=proj1.id,
            description="Security audit may delay target completion date.",
            potential_impact="2-3 week launch delay",
            likelihood="Medium",
            mitigation="Schedule pre-audit compliance review.",
            evidence_passage="if the security audit takes longer.",
            status=RiskStatus.OPEN
        )
        db.add(risk1)

        # Questions
        q1 = UnansweredQuestion(
            meeting_id=meeting.id,
            project_id=proj1.id,
            question="Who will lead and own the mobile client updates?",
            clarification_reason="Tony noted uncertainty over ownership during meeting.",
            evidence_passage="but who will own it?",
            status=QuestionStatus.OPEN
        )
        db.add(q1)

        await db.commit()
        print("Demo seed data created successfully!")

if __name__ == "__main__":
    asyncio.run(seed())

