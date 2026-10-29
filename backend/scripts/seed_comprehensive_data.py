import asyncio
import os
import sys
from datetime import datetime, date, timedelta, timezone

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.user import Organization, User, UserRole
from backend.app.models.client import Client
from backend.app.models.project import Project, ProjectStatus
from backend.app.models.meeting import Meeting, MeetingStatus, MeetingType, MeetingAttendee
from backend.app.models.decision import Decision, DecisionStatus
from backend.app.models.task import Task, TaskStatus, TaskPriority, OwnerStatus, DueDateStatus
from backend.app.models.risk import Risk, RiskStatus
from backend.app.models.blocker import BlockerDependency
from backend.app.models.question import UnansweredQuestion, QuestionStatus
from sqlalchemy import select, func

async def seed_data():
    print("Connecting to database...")
    await init_db()

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Organization).where(Organization.slug == "acme-solutions"))
        org = res.scalar_one_or_none()
        if not org:
            res_org = await db.execute(select(Organization))
            org = res_org.scalars().first()

        if not org:
            print("No organization found. Creating Acme Enterprise Solutions...")
            org = Organization(name="Acme Enterprise Solutions", slug="acme-solutions")
            db.add(org)
            await db.commit()
            await db.refresh(org)

        print(f"Using Organization: {org.name} ({org.id})")

        # Get existing users
        u_res = await db.execute(select(User).where(User.organization_id == org.id))
        users = u_res.scalars().all()
        admin_user = next((u for u in users if u.role == UserRole.ADMIN), users[0] if users else None)

        # 1. Clients
        existing_clients_res = await db.execute(select(Client).where(Client.organization_id == org.id))
        existing_clients = {c.name: c for c in existing_clients_res.scalars().all()}

        clients_data = [
            {"name": "Acme Corp", "org_name": "Acme Global Manufacturing", "contact": "Alice Admin", "email": "alice@acme.com", "industry": "Industrial Manufacturing"},
            {"name": "Stark Industries", "org_name": "Stark Global", "contact": "Tony Stark", "email": "tony@stark.com", "industry": "Aerospace & Robotics"},
            {"name": "Initech Global", "org_name": "Initech Corporation", "contact": "Peter Gibbons", "email": "peter@initech.com", "industry": "Financial Services"},
            {"name": "Wayne Enterprises", "org_name": "Wayne Global", "contact": "Bruce Wayne", "email": "bruce@wayne.com", "industry": "Applied Sciences & Defense"},
            {"name": "Cyberdyne Systems", "org_name": "Cyberdyne Technologies", "contact": "Miles Dyson", "email": "miles@cyberdyne.com", "industry": "Artificial Intelligence"},
            {"name": "Hooli Cloud", "org_name": "Hooli Corporation", "contact": "Gavin Belson", "email": "gavin@hooli.com", "industry": "Cloud Infrastructure"},
        ]

        clients_map = {}
        for c in clients_data:
            if c["name"] in existing_clients:
                clients_map[c["name"]] = existing_clients[c["name"]]
            else:
                new_c = Client(
                    organization_id=org.id,
                    name=c["name"],
                    organization_name=c["org_name"],
                    contact_name=c["contact"],
                    contact_email=c["email"],
                    industry=c["industry"]
                )
                db.add(new_c)
                await db.commit()
                await db.refresh(new_c)
                clients_map[c["name"]] = new_c

        print(f"Clients ready: {len(clients_map)}")

        # 2. Projects
        existing_projs_res = await db.execute(select(Project).where(Project.organization_id == org.id))
        existing_projs = {p.name: p for p in existing_projs_res.scalars().all()}

        projs_data = [
            {
                "name": "Arc Reactor Monitoring Platform",
                "client": "Stark Industries",
                "desc": "Real-time telemetry and predictive anomaly detection pipeline.",
                "tags": ["telemetry", "ai", "hardware"]
            },
            {
                "name": "Website Redesign & Brand Identity",
                "client": "Acme Corp",
                "desc": "Enterprise web portal overhaul with modern design system and CMS integration.",
                "tags": ["frontend", "branding", "react"]
            },
            {
                "name": "Automated TPS Reporting Migration",
                "client": "Initech Global",
                "desc": "Modernize legacy reporting batch jobs to cloud streaming analytics.",
                "tags": ["cloud", "data-pipeline"]
            },
            {
                "name": "Zero-Trust Security & Identity Audit",
                "client": "Wayne Enterprises",
                "desc": "Comprehensive security architecture review, RBAC enforcement, and penetration testing.",
                "tags": ["security", "audit", "compliance"]
            },
            {
                "name": "Autonomous Workflow Orchestration",
                "client": "Cyberdyne Systems",
                "desc": "AI agent framework for automating multi-stage enterprise operations.",
                "tags": ["agents", "workflow", "automation"]
            }
        ]

        projects_map = {}
        for p in projs_data:
            if p["name"] in existing_projs:
                projects_map[p["name"]] = existing_projs[p["name"]]
            else:
                client_obj = clients_map.get(p["client"]) or list(clients_map.values())[0]
                new_p = Project(
                    organization_id=org.id,
                    client_id=client_obj.id,
                    name=p["name"],
                    description=p["desc"],
                    manager_id=admin_user.id if admin_user else None,
                    status=ProjectStatus.ACTIVE,
                    start_date=date(2026, 9, 1),
                    target_date=date(2026, 12, 15),
                    tags=p["tags"]
                )
                db.add(new_p)
                await db.commit()
                await db.refresh(new_p)
                projects_map[p["name"]] = new_p

        print(f"Projects ready: {len(projects_map)}")

        # 3. Meetings with rich outcomes
        now = datetime.now(timezone.utc)
        meetings_spec = [
            {
                "title": "E2E Test Action Review Meeting",
                "project": "Automated TPS Reporting Migration",
                "client": "Initech Global",
                "date": now - timedelta(hours=3),
                "type": MeetingType.CLIENT_REVIEW,
                "transcript": """Alice Admin: Welcome everyone. We need to finalize the cloud streaming migration plan today.
Bob Builder: I will complete the database schema migration scripts by Friday.
Peter Gibbons: Approved. We confirmed the decision to migrate legacy MySQL tables to PostgreSQL 16.
Alice Admin: We should also prepare the executive progress report for next Tuesday.
Bob Builder: Who will be responsible for the end-to-end integration testing suite?
Peter Gibbons: Sarah might assist, but we need user confirmation on her availability.
Alice Admin: Warning: if the IAM permissions are delayed by IT, we risk missing the staging freeze date.""",
                "attendees": [
                    {"name": "Alice Admin", "email": "alice@acme.com", "role": "Meeting Chair"},
                    {"name": "Bob Builder", "email": "bob@acme.com", "role": "Senior Engineer"},
                    {"name": "Peter Gibbons", "email": "peter@initech.com", "role": "Client Lead"},
                    {"name": "Sarah Connor", "email": "sarah@acme.com", "role": "QA Architect"},
                    {"name": "Mike Member", "email": "member@acme.com", "role": "Frontend Dev"},
                    {"name": "Victor Viewer", "email": "viewer@acme.com", "role": "Auditor"},
                    {"name": "Diana Prince", "email": "diana@wayne.com", "role": "Security Consultant"},
                    {"name": "Bruce Wayne", "email": "bruce@wayne.com", "role": "Executive Sponsor"},
                ],
                "decisions": [
                    {
                        "title": "Migrate Legacy MySQL to PostgreSQL 16",
                        "desc": "Approved migrating legacy batch reporting tables to PostgreSQL 16 with native JSONB support.",
                        "status": DecisionStatus.CONFIRMED,
                        "approver": "Peter Gibbons",
                        "evidence": "We confirmed the decision to migrate legacy MySQL tables to PostgreSQL 16."
                    },
                    {
                        "title": "Staging Deployment Freeze Date",
                        "desc": "Proposed freezing staging deployments on the 15th pending IT approvals.",
                        "status": DecisionStatus.PROPOSED,
                        "approver": None,
                        "evidence": "we risk missing the staging freeze date."
                    }
                ],
                "tasks": [
                    {
                        "title": "Complete database schema migration scripts",
                        "desc": "Finalize alembic scripts and test relational foreign key cascades.",
                        "owner": "Bob Builder",
                        "owner_status": OwnerStatus.EXPLICIT,
                        "due_date": (now + timedelta(days=2)).date(),
                        "due_date_status": DueDateStatus.RESOLVED_FROM_MEETING_DATE,
                        "date_expr": "by Friday",
                        "priority": TaskPriority.HIGH,
                        "status": TaskStatus.READY,
                        "evidence": "I will complete the database schema migration scripts by Friday."
                    },
                    {
                        "title": "Prepare executive progress report",
                        "desc": "Assemble KPI metrics, database benchmarks, and timeline update.",
                        "owner": None,
                        "owner_status": OwnerStatus.NOT_STATED,
                        "due_date": (now + timedelta(days=6)).date(),
                        "due_date_status": DueDateStatus.RESOLVED_FROM_MEETING_DATE,
                        "date_expr": "for next Tuesday",
                        "priority": TaskPriority.MEDIUM,
                        "status": TaskStatus.NEEDS_CLARIFICATION,
                        "evidence": "We should also prepare the executive progress report for next Tuesday."
                    },
                    {
                        "title": "Implement end-to-end integration test harness",
                        "desc": "Verify all streaming event consumers against the staging cluster.",
                        "owner": "Sarah Connor",
                        "owner_status": OwnerStatus.AMBIGUOUS,
                        "due_date": None,
                        "due_date_status": DueDateStatus.NOT_STATED,
                        "date_expr": None,
                        "priority": TaskPriority.HIGH,
                        "status": TaskStatus.NEEDS_CLARIFICATION,
                        "evidence": "Sarah might assist, but we need user confirmation on her availability."
                    },
                    {
                        "title": "Verify IAM cloud permissions with central IT",
                        "desc": "Request elevated service principal credentials for the migration runner.",
                        "owner": "Alice Admin",
                        "owner_status": OwnerStatus.EXPLICIT,
                        "due_date": (now + timedelta(days=1)).date(),
                        "due_date_status": DueDateStatus.EXPLICIT,
                        "date_expr": "tomorrow morning",
                        "priority": TaskPriority.URGENT,
                        "status": TaskStatus.IN_PROGRESS,
                        "evidence": "if the IAM permissions are delayed by IT, we risk missing the staging freeze date."
                    },
                    {
                        "title": "Audit database backup redundancy in cloud region",
                        "desc": "Confirm automated snapshots are configured for cross-region replication.",
                        "owner": "Bob Builder",
                        "owner_status": OwnerStatus.EXPLICIT,
                        "due_date": (now + timedelta(days=5)).date(),
                        "due_date_status": DueDateStatus.RESOLVED_FROM_MEETING_DATE,
                        "date_expr": "by end of week",
                        "priority": TaskPriority.MEDIUM,
                        "status": TaskStatus.COMPLETED,
                        "evidence": "We need to ensure the telemetry dashboard responds in sub-50ms latency."
                    }
                ],
                "risks": [
                    {
                        "desc": "IT delay in provisioning IAM role credentials could delay staging rollout.",
                        "impact": "1-2 week schedule slippage",
                        "likelihood": "High",
                        "mitigation": "Escalate ticket directly to Director of Infrastructure.",
                        "evidence": "if the IAM permissions are delayed by IT, we risk missing the staging freeze date."
                    }
                ],
                "questions": [
                    {
                        "q": "Who will own the end-to-end integration test suite execution?",
                        "reason": "Sarah's availability is tentative and unconfirmed.",
                        "evidence": "Who will be responsible for the end-to-end integration testing suite?"
                    }
                ]
            },
            {
                "title": "Website Redesign Discussion",
                "project": "Website Redesign & Brand Identity",
                "client": "Acme Corp",
                "date": now - timedelta(days=1),
                "type": MeetingType.PLANNING,
                "transcript": """Tony Stark: The new visual language needs to feel ultra-clean, minimal, and responsive.
Alice Admin: We finalized the design palette: deep midnight navy with electric indigo accents and clean card shadows.
Mike Member: I will build the React component library and implement Tailwind tokens by Wednesday.
Priya Sharma: Let's make sure accessibility standards WCAG AA are met across all form elements.
Tony Stark: We must launch the public landing page before the annual investor summit on November 20th.
Sarah Connor: What about the content migration from WordPress? Who has the export files?""",
                "attendees": [
                    {"name": "Alice Admin", "email": "alice@acme.com", "role": "Creative Director"},
                    {"name": "Tony Stark", "email": "tony@stark.com", "role": "Brand Sponsor"},
                    {"name": "Mike Member", "email": "member@acme.com", "role": "UI/UX Engineer"},
                    {"name": "Priya Sharma", "email": "priya@acme.com", "role": "Accessibility Specialist"},
                    {"name": "Sarah Connor", "email": "sarah@acme.com", "role": "Content Strategist"},
                    {"name": "Peter ProjectManager", "email": "pm@acme.com", "role": "Delivery Lead"},
                    {"name": "Bruce Wayne", "email": "bruce@wayne.com", "role": "Stakeholder"},
                    {"name": "Miles Dyson", "email": "miles@cyberdyne.com", "role": "Advisor"},
                    {"name": "Gavin Belson", "email": "gavin@hooli.com", "role": "Advisor"},
                    {"name": "Clark Kent", "email": "clark@dailyplanet.com", "role": "Communications"},
                    {"name": "Victor Viewer", "email": "viewer@acme.com", "role": "Observer"},
                    {"name": "Diana Prince", "email": "diana@wayne.com", "role": "Design Lead"}
                ],
                "decisions": [
                    {
                        "title": "Adopt Midnight Navy & Electric Indigo Design System",
                        "desc": "Agreed to use deep navy surface tokens with vibrant purple and indigo interactive elements.",
                        "status": DecisionStatus.CONFIRMED,
                        "approver": "Alice Admin",
                        "evidence": "We finalized the design palette: deep midnight navy with electric indigo accents and clean card shadows."
                    }
                ],
                "tasks": [
                    {
                        "title": "Build Tailwind token system and React UI components",
                        "desc": "Implement button, modal, card, and input components conforming to Figma spec.",
                        "owner": "Mike Member",
                        "owner_status": OwnerStatus.EXPLICIT,
                        "due_date": (now + timedelta(days=4)).date(),
                        "due_date_status": DueDateStatus.RESOLVED_FROM_MEETING_DATE,
                        "date_expr": "by Wednesday",
                        "priority": TaskPriority.HIGH,
                        "status": TaskStatus.IN_PROGRESS,
                        "evidence": "I will build the React component library and implement Tailwind tokens by Wednesday."
                    },
                    {
                        "title": "Perform WCAG 2.1 AA accessibility audit on UI components",
                        "desc": "Check color contrast ratios, screen reader ARIA labels, and focus rings.",
                        "owner": "Priya Sharma",
                        "owner_status": OwnerStatus.EXPLICIT,
                        "due_date": (now + timedelta(days=7)).date(),
                        "due_date_status": DueDateStatus.EXPLICIT,
                        "date_expr": "in one week",
                        "priority": TaskPriority.MEDIUM,
                        "status": TaskStatus.READY,
                        "evidence": "Let's make sure accessibility standards WCAG AA are met across all form elements."
                    },
                    {
                        "title": "Export legacy WordPress content to structured markdown",
                        "desc": "Extract blog posts, press releases, and author metadata.",
                        "owner": None,
                        "owner_status": OwnerStatus.NOT_STATED,
                        "due_date": None,
                        "due_date_status": DueDateStatus.NOT_STATED,
                        "date_expr": None,
                        "priority": TaskPriority.MEDIUM,
                        "status": TaskStatus.NEEDS_CLARIFICATION,
                        "evidence": "What about the content migration from WordPress? Who has the export files?"
                    },
                    {
                        "title": "Prepare landing page staging deployment on Vercel",
                        "desc": "Setup preview URLs, custom domain SSL, and Lighthouse performance CI checks.",
                        "owner": "Mike Member",
                        "owner_status": OwnerStatus.EXPLICIT,
                        "due_date": date(2026, 11, 20),
                        "due_date_status": DueDateStatus.EXPLICIT,
                        "date_expr": "November 20th",
                        "priority": TaskPriority.URGENT,
                        "status": TaskStatus.READY,
                        "evidence": "We must launch the public landing page before the annual investor summit on November 20th."
                    }
                ],
                "risks": [
                    {
                        "desc": "Delayed legacy content extraction could compress QA review timeline.",
                        "impact": "Content formatting inconsistencies on launch",
                        "likelihood": "Medium",
                        "mitigation": "Assign dedicated copywriter to audit top 20 revenue pages first.",
                        "evidence": "Who has the export files?"
                    }
                ],
                "questions": [
                    {
                        "q": "Who is the custodian of the WordPress database export archive?",
                        "reason": "Missing owner for data migration.",
                        "evidence": "What about the content migration from WordPress? Who has the export files?"
                    }
                ]
            },
            {
                "title": "Telemetry Architecture Review",
                "project": "Arc Reactor Monitoring Platform",
                "client": "Stark Industries",
                "date": now - timedelta(days=3),
                "type": MeetingType.STATUS_UPDATE,
                "transcript": """Tony Stark: We need to ensure the telemetry dashboard responds in sub-50ms latency.
Peter Gibbons: Agreed. We approved migrating the storage backend to PostgreSQL.
Sarah: Priya will optimize the database indexing by Friday.
Tony: We should try to update the mobile client sometime next month, but who will own it?
Peter: We might move the production launch to December if the security audit takes longer.""",
                "attendees": [
                    {"name": "Tony Stark", "email": "tony@stark.com", "role": "Client Sponsor"},
                    {"name": "Peter Gibbons", "email": "peter@initech.com", "role": "Project Lead"},
                    {"name": "Priya Sharma", "email": "priya@acme.com", "role": "Database Engineer"},
                    {"name": "Alice Admin", "email": "alice@acme.com", "role": "Architect"},
                    {"name": "Miles Dyson", "email": "miles@cyberdyne.com", "role": "Consultant"},
                    {"name": "Bruce Wayne", "email": "bruce@wayne.com", "role": "Observer"}
                ],
                "decisions": [
                    {
                        "title": "Migrate Telemetry Storage to PostgreSQL",
                        "desc": "Approved migrating storage backend to PostgreSQL for native JSONB and relational integrity.",
                        "status": DecisionStatus.CONFIRMED,
                        "approver": "Peter Gibbons",
                        "evidence": "We approved migrating the storage backend to PostgreSQL."
                    }
                ],
                "tasks": [
                    {
                        "title": "Optimize database indexing for telemetry stream",
                        "desc": "Review composite indices on device_id and timestamp for sub-50ms queries.",
                        "owner": "Priya Sharma",
                        "owner_status": OwnerStatus.EXPLICIT,
                        "due_date": (now - timedelta(days=1)).date(),
                        "due_date_status": DueDateStatus.RESOLVED_FROM_MEETING_DATE,
                        "date_expr": "by Friday",
                        "priority": TaskPriority.HIGH,
                        "status": TaskStatus.COMPLETED,
                        "evidence": "Priya will optimize the database indexing by Friday."
                    },
                    {
                        "title": "Update mobile client telemetry view",
                        "desc": "Implement new latency widgets on iOS and Android.",
                        "owner": None,
                        "owner_status": OwnerStatus.NOT_STATED,
                        "due_date": None,
                        "due_date_status": DueDateStatus.AMBIGUOUS,
                        "date_expr": "sometime next month",
                        "priority": TaskPriority.MEDIUM,
                        "status": TaskStatus.NEEDS_CLARIFICATION,
                        "evidence": "We should try to update the mobile client sometime next month, but who will own it?"
                    }
                ],
                "risks": [
                    {
                        "desc": "Security audit may delay target completion date.",
                        "impact": "2-3 week launch delay",
                        "likelihood": "Medium",
                        "mitigation": "Schedule pre-audit compliance review.",
                        "evidence": "if the security audit takes longer."
                    }
                ],
                "questions": [
                    {
                        "q": "Who will lead and own the mobile client updates?",
                        "reason": "Tony noted uncertainty over ownership during meeting.",
                        "evidence": "but who will own it?"
                    }
                ]
            },
            {
                "title": "Sprint Planning & Roadmap",
                "project": "Zero-Trust Security & Identity Audit",
                "client": "Wayne Enterprises",
                "date": now - timedelta(days=7),
                "type": MeetingType.PLANNING,
                "transcript": """Bruce Wayne: The security audit found 3 edge-case authentication tokens with indefinite TTL.
Diana Prince: We must enforce 15-minute token rotation with refresh token revoking.
Alice Admin: I will implement the Redis-backed token blacklist and session validator by Monday.
Bruce Wayne: Agreed. We approved the new security baseline.""",
                "attendees": [
                    {"name": "Bruce Wayne", "email": "bruce@wayne.com", "role": "Client Sponsor"},
                    {"name": "Diana Prince", "email": "diana@wayne.com", "role": "Security Architect"},
                    {"name": "Alice Admin", "email": "alice@acme.com", "role": "Lead Architect"},
                    {"name": "Peter ProjectManager", "email": "pm@acme.com", "role": "Scrum Master"},
                    {"name": "Bob Builder", "email": "bob@acme.com", "role": "Backend Engineer"},
                    {"name": "Sarah Connor", "email": "sarah@acme.com", "role": "QA Engineer"},
                    {"name": "Victor Viewer", "email": "viewer@acme.com", "role": "Compliance Analyst"}
                ],
                "decisions": [
                    {
                        "title": "Enforce 15-minute JWT Token Expiration Policy",
                        "desc": "Mandate short-lived JWT access tokens and cryptographically signed refresh tokens.",
                        "status": DecisionStatus.CONFIRMED,
                        "approver": "Bruce Wayne",
                        "evidence": "We must enforce 15-minute token rotation with refresh token revoking."
                    }
                ],
                "tasks": [
                    {
                        "title": "Implement Redis-backed token blacklist and session validator",
                        "desc": "Build token revocation endpoint and integrate with API gateway middleware.",
                        "owner": "Alice Admin",
                        "owner_status": OwnerStatus.EXPLICIT,
                        "due_date": (now - timedelta(days=2)).date(),
                        "due_date_status": DueDateStatus.RESOLVED_FROM_MEETING_DATE,
                        "date_expr": "by Monday",
                        "priority": TaskPriority.URGENT,
                        "status": TaskStatus.COMPLETED,
                        "evidence": "I will implement the Redis-backed token blacklist and session validator by Monday."
                    }
                ],
                "risks": [
                    {
                        "desc": "Stale tokens could remain valid if Redis failover experiences replication lag.",
                        "impact": "Brief window of revoked token acceptance",
                        "likelihood": "Low",
                        "mitigation": "Configure Redis cluster with synchronous replication on revoke events.",
                        "evidence": "3 edge-case authentication tokens with indefinite TTL."
                    }
                ],
                "questions": []
            },
            {
                "title": "Beta Client Feedback & QA",
                "project": "Autonomous Workflow Orchestration",
                "client": "Cyberdyne Systems",
                "date": now - timedelta(days=11),
                "type": MeetingType.CLIENT_REVIEW,
                "transcript": """Miles Dyson: The beta test group gave very positive remarks on automated task routing.
Sarah Connor: However, 2 clients reported that notifications were delivered with a 5-minute delay.
Miles Dyson: Bob will investigate the Celery background worker queue by next Tuesday.
Sarah Connor: We should verify if WebSocket connections are dropping behind the reverse proxy.""",
                "attendees": [
                    {"name": "Miles Dyson", "email": "miles@cyberdyne.com", "role": "Client Lead"},
                    {"name": "Sarah Connor", "email": "sarah@acme.com", "role": "Product Manager"},
                    {"name": "Bob Builder", "email": "bob@acme.com", "role": "Infrastructure Engineer"},
                    {"name": "Alice Admin", "email": "alice@acme.com", "role": "System Architect"},
                    {"name": "Peter Gibbons", "email": "peter@initech.com", "role": "Reviewer"}
                ],
                "decisions": [
                    {
                        "title": "Prioritize Real-time Notification Queue Overhaul",
                        "desc": "Shift focus in upcoming sprint to resolving background worker queue latency.",
                        "status": DecisionStatus.CONFIRMED,
                        "approver": "Miles Dyson",
                        "evidence": "Bob will investigate the Celery background worker queue by next Tuesday."
                    }
                ],
                "tasks": [
                    {
                        "title": "Investigate Celery background worker queue delay",
                        "desc": "Profile task execution latency and redis broker message backpressure.",
                        "owner": "Bob Builder",
                        "owner_status": OwnerStatus.EXPLICIT,
                        "due_date": (now - timedelta(days=4)).date(),
                        "due_date_status": DueDateStatus.RESOLVED_FROM_MEETING_DATE,
                        "date_expr": "by next Tuesday",
                        "priority": TaskPriority.HIGH,
                        "status": TaskStatus.IN_PROGRESS,
                        "evidence": "Bob will investigate the Celery background worker queue by next Tuesday."
                    },
                    {
                        "title": "Audit reverse proxy WebSocket keepalive timeouts",
                        "desc": "Inspect NGINX proxy_read_timeout and ping intervals for persistent connections.",
                        "owner": None,
                        "owner_status": OwnerStatus.NOT_STATED,
                        "due_date": None,
                        "due_date_status": DueDateStatus.NOT_STATED,
                        "date_expr": None,
                        "priority": TaskPriority.MEDIUM,
                        "status": TaskStatus.NEEDS_CLARIFICATION,
                        "evidence": "We should verify if WebSocket connections are dropping behind the reverse proxy."
                    }
                ],
                "risks": [
                    {
                        "desc": "Notification latency could degrade client satisfaction during enterprise pilot.",
                        "impact": "Pilot extension requested by client",
                        "likelihood": "Medium",
                        "mitigation": "Add dedicated worker pool for high-priority notification channels.",
                        "evidence": "2 clients reported that notifications were delivered with a 5-minute delay."
                    }
                ],
                "questions": [
                    {
                        "q": "Are WebSocket disconnections occurring at the client browser or proxy layer?",
                        "reason": "Need network trace to isolate connection drops.",
                        "evidence": "We should verify if WebSocket connections are dropping behind the reverse proxy."
                    }
                ]
            }
        ]

        # Insert meetings
        for m_data in meetings_spec:
            # Check if already exists
            existing_m_res = await db.execute(
                select(Meeting).where(
                    Meeting.organization_id == org.id,
                    Meeting.title == m_data["title"]
                )
            )
            existing_m = existing_m_res.scalars().first()
            if existing_m:
                print(f"Meeting '{m_data['title']}' already exists, skipping creation.")
                continue

            proj_obj = projects_map.get(m_data["project"]) or list(projects_map.values())[0]
            client_obj = clients_map.get(m_data["client"]) or list(clients_map.values())[0]

            new_meeting = Meeting(
                organization_id=org.id,
                client_id=client_obj.id,
                project_id=proj_obj.id,
                title=m_data["title"],
                description=f"Strategic alignment and progress review for {proj_obj.name}.",
                meeting_date=m_data["date"],
                timezone="America/New_York",
                meeting_type=m_data["type"],
                language="en",
                status=MeetingStatus.REVIEWED,
                raw_transcript=m_data["transcript"],
                summary_data={
                    "meeting_summary": f"Executive alignment on {proj_obj.name}. Discussed milestones, agreed on strategic priorities, and established actionable task assignments.",
                    "topics": [m_data["title"], proj_obj.name, "Deliverables", "Risk Mitigation"]
                },
                analysis_warnings=[]
            )
            db.add(new_meeting)
            await db.commit()
            await db.refresh(new_meeting)

            # Attendees
            for att in m_data["attendees"]:
                db.add(MeetingAttendee(
                    meeting_id=new_meeting.id,
                    name=att["name"],
                    email=att["email"],
                    role=att["role"]
                ))

            # Decisions
            for d in m_data["decisions"]:
                db.add(Decision(
                    meeting_id=new_meeting.id,
                    project_id=proj_obj.id,
                    title=d["title"],
                    description=d["desc"],
                    status=d["status"],
                    owner_or_approver=d["approver"],
                    evidence_passage=d["evidence"],
                    confirmation_required=d["status"] == DecisionStatus.PROPOSED
                ))

            # Tasks
            for t in m_data["tasks"]:
                db.add(Task(
                    meeting_id=new_meeting.id,
                    project_id=proj_obj.id,
                    title=t["title"],
                    description=t["desc"],
                    owner_name=t["owner"],
                    owner_status=t["owner_status"],
                    due_date=t["due_date"],
                    due_date_status=t["due_date_status"],
                    date_expression=t["date_expr"],
                    priority=t["priority"],
                    status=t["status"],
                    evidence_passage=t["evidence"],
                    confirmation_required=t["owner_status"] != OwnerStatus.EXPLICIT or t["due_date_status"] != DueDateStatus.EXPLICIT
                ))

            # Risks
            for r in m_data["risks"]:
                db.add(Risk(
                    meeting_id=new_meeting.id,
                    project_id=proj_obj.id,
                    description=r["desc"],
                    potential_impact=r["impact"],
                    likelihood=r["likelihood"],
                    mitigation=r["mitigation"],
                    evidence_passage=r["evidence"],
                    status=RiskStatus.OPEN
                ))

            # Questions
            for q in m_data["questions"]:
                db.add(UnansweredQuestion(
                    meeting_id=new_meeting.id,
                    project_id=proj_obj.id,
                    question=q["q"],
                    clarification_reason=q["reason"],
                    evidence_passage=q["evidence"],
                    status=QuestionStatus.OPEN
                ))

            await db.commit()
            print(f"Created meeting '{m_data['title']}' with {len(m_data['tasks'])} tasks, {len(m_data['attendees'])} attendees.")

        # Final counts
        total_m = (await db.execute(select(func.count(Meeting.id)).where(Meeting.organization_id == org.id))).scalar()
        total_t = (await db.execute(select(func.count(Task.id)).join(Meeting).where(Meeting.organization_id == org.id))).scalar()
        total_d = (await db.execute(select(func.count(Decision.id)).join(Meeting).where(Meeting.organization_id == org.id))).scalar()
        total_r = (await db.execute(select(func.count(Risk.id)).join(Meeting).where(Meeting.organization_id == org.id))).scalar()
        total_q = (await db.execute(select(func.count(UnansweredQuestion.id)).join(Meeting).where(Meeting.organization_id == org.id))).scalar()

        print("=" * 60)
        print("DATABASE DUMMY DATA SEED COMPLETE!")
        print(f"Total Meetings: {total_m}")
        print(f"Total Tasks: {total_t}")
        print(f"Total Decisions: {total_d}")
        print(f"Total Risks: {total_r}")
        print(f"Total Questions: {total_q}")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(seed_data())
