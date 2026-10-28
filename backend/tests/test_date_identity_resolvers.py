from datetime import datetime, date
from backend.app.services.date_resolver import DateResolver
from backend.app.services.identity_resolver import IdentityResolver
from backend.app.models.task import OwnerStatus, DueDateStatus

def test_date_resolver_unknown_meeting_date():
    # If meeting date is None, relative expression CANNOT be resolved to a calendar date
    resolved, status, reason = DateResolver.resolve_deadline(
        date_expression="tomorrow",
        meeting_datetime=None
    )
    assert resolved is None
    assert status == DueDateStatus.NOT_STATED
    assert "Meeting date is unknown" in reason

def test_date_resolver_relative_dates():
    # Base meeting date: Thursday, Oct 15, 2026
    meeting_dt = datetime(2026, 10, 15, 14, 0, 0)

    # 1. "tomorrow" -> Oct 16, 2026
    resolved, status, _ = DateResolver.resolve_deadline(
        date_expression="tomorrow",
        meeting_datetime=meeting_dt
    )
    assert resolved == date(2026, 10, 16)
    assert status == DueDateStatus.RESOLVED_FROM_MEETING_DATE

    # 2. "in 3 days" -> Oct 18, 2026
    resolved, status, _ = DateResolver.resolve_deadline(
        date_expression="in 3 days",
        meeting_datetime=meeting_dt
    )
    assert resolved == date(2026, 10, 18)
    assert status == DueDateStatus.RESOLVED_FROM_MEETING_DATE

    # 3. Explicit date string
    resolved, status, _ = DateResolver.resolve_deadline(
        date_expression=None,
        meeting_datetime=meeting_dt,
        explicit_date_str="2026-11-20"
    )
    assert resolved == date(2026, 11, 20)
    assert status == DueDateStatus.EXPLICIT

    # 4. Ambiguous expression
    resolved, status, _ = DateResolver.resolve_deadline(
        date_expression="in a couple weeks",
        meeting_datetime=meeting_dt
    )
    assert resolved is None
    assert status == DueDateStatus.AMBIGUOUS

def test_identity_resolver_unassigned():
    name, uid, status, reason = IdentityResolver.resolve_task_owner(
        raw_owner_name=None,
        attendees=[{"name": "Alice Smith"}],
        project_members=[]
    )
    assert name is None
    assert uid is None
    assert status == OwnerStatus.NOT_STATED

def test_identity_resolver_ambiguous_names():
    attendees = [
        {"name": "Alex Mercer", "user_id": "u1"},
        {"name": "Alex Smith", "user_id": "u2"}
    ]
    name, uid, status, reason = IdentityResolver.resolve_task_owner(
        raw_owner_name="Alex",
        attendees=attendees,
        project_members=[]
    )
    # Must preserve uncertainty!
    assert status == OwnerStatus.AMBIGUOUS
    assert uid is None
    assert "multiple candidates" in reason.lower()

def test_identity_resolver_unambiguous():
    attendees = [
        {"name": "Priya Sharma", "user_id": "u3"},
        {"name": "David Brown", "user_id": "u4"}
    ]
    name, uid, status, reason = IdentityResolver.resolve_task_owner(
        raw_owner_name="Priya",
        attendees=attendees,
        project_members=[]
    )
    assert name == "Priya Sharma"
    assert uid == "u3"
    assert status == OwnerStatus.EXPLICIT

