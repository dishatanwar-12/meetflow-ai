import pytest
from datetime import datetime, date
from unittest.mock import MagicMock
from backend.app.services.export_service import ExportService
from backend.app.models.task import Task, TaskPriority, TaskStatus, OwnerStatus, DueDateStatus
from backend.app.models.decision import Decision, DecisionStatus
from backend.app.models.meeting import Meeting, MeetingType, MeetingStatus

def test_csv_formula_injection_sanitization():
    # Malicious inputs starting with =, +, -, @
    malicious_task = MagicMock(spec=Task)
    malicious_task.id = "t1"
    malicious_task.title = "=CMD('calc.exe')"
    malicious_task.description = "+1234567890"
    malicious_task.owner_name = "@admin"
    malicious_task.owner_status = OwnerStatus.EXPLICIT
    malicious_task.due_date = None
    malicious_task.due_date_status = DueDateStatus.NOT_STATED
    malicious_task.date_expression = "-30"
    malicious_task.priority = TaskPriority.HIGH
    malicious_task.status = TaskStatus.READY
    malicious_task.dependencies = []
    malicious_task.confirmation_required = False
    malicious_task.confirmation_reason = None
    malicious_task.evidence_passage = "source quote"
    malicious_task.created_at = datetime(2026, 10, 15, 10, 0, 0)

    csv_out = ExportService.generate_tasks_csv([malicious_task])

    # Must be neutralized with leading single quote: '=CMD..., '+123..., '@admin, '-30
    assert "'=CMD('calc.exe')" in csv_out
    assert "'+1234567890" in csv_out
    assert "'@admin" in csv_out
    assert "'-30" in csv_out

def test_pdf_generation_valid_header():
    mock_meeting = MagicMock(spec=Meeting)
    mock_meeting.title = "Q4 Product Strategy"
    mock_meeting.meeting_date = datetime(2026, 10, 15, 14, 0)
    mock_meeting.timezone = "UTC"
    mock_meeting.summary_data = {"meeting_summary": "Discussed roadmap and Q4 milestones."}

    mock_decision = MagicMock(spec=Decision)
    mock_decision.title = "Adopt PostgreSQL"
    mock_decision.description = "Migrate from MySQL to PostgreSQL for JSONB support."
    mock_decision.status = DecisionStatus.CONFIRMED
    mock_decision.evidence_passage = "We agreed to migrate to Postgres."

    mock_task = MagicMock(spec=Task)
    mock_task.title = "Benchmark database performance"
    mock_task.owner_name = "Alex"
    mock_task.due_date = date(2026, 11, 1)
    mock_task.date_expression = "Nov 1"
    mock_task.status = TaskStatus.IN_PROGRESS
    mock_task.priority = TaskPriority.HIGH

    pdf_bytes = ExportService.generate_meeting_pdf(
        meeting=mock_meeting,
        client_name="Acme Corp",
        project_name="Platform 2.0",
        decisions=[mock_decision],
        tasks=[mock_task],
        risks=[],
        questions=[]
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    # Valid PDF file must start with %PDF-
    assert pdf_bytes.startswith(b"%PDF-")

