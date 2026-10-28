import io
import pytest
from httpx import AsyncClient
from backend.app.services.transcript_parser import TranscriptParser, DocumentParseError

@pytest.mark.asyncio
async def test_meeting_creation_and_txt_upload(client: AsyncClient, pm_user, auth_headers):
    # 1. Create client and project
    c_res = await client.post("/api/v1/clients", json={"name": "Cyberdyne"}, headers=auth_headers(pm_user))
    client_id = c_res.json()["id"]

    p_res = await client.post("/api/v1/projects", json={"name": "Neural Net", "client_id": client_id}, headers=auth_headers(pm_user))
    project_id = p_res.json()["id"]

    # 2. Create meeting draft
    m_res = await client.post(
        "/api/v1/meetings",
        json={
            "title": "Architecture Kickoff",
            "client_id": client_id,
            "project_id": project_id,
            "meeting_date": "2026-10-15T10:00:00Z",
            "timezone": "America/New_York",
            "attendees": [
                {"name": "Sarah Connor", "email": "sarah@connor.com", "role": "PM"},
                {"name": "Miles Dyson", "email": "miles@cyberdyne.com", "role": "Lead Architect"}
            ]
        },
        headers=auth_headers(pm_user)
    )
    assert m_res.status_code == 201
    meeting_id = m_res.json()["id"]

    # 3. Upload TXT transcript
    txt_content = b"Sarah: We need to finalize the GPU server specifications.\nMiles: I will compile the specs by next Friday.\n"
    files = {"file": ("transcript.txt", txt_content, "text/plain")}
    up_res = await client.post(
        f"/api/v1/meetings/{meeting_id}/upload",
        files=files,
        headers=auth_headers(pm_user)
    )
    assert up_res.status_code == 200
    doc_data = up_res.json()
    assert doc_data["filename"] == "transcript.txt"

    # Verify meeting transcript updated
    get_res = await client.get(f"/api/v1/meetings/{meeting_id}", headers=auth_headers(pm_user))
    assert "Miles: I will compile the specs by next Friday." in get_res.json()["raw_transcript"]

def test_transcript_parser_normalization_and_speakers():
    raw_text = "Speaker 1: Welcome everyone.\r\n\r\n\r\nSpeaker 2: Let's begin the review.\u00a0\n"
    cleaned = TranscriptParser.normalize_text(raw_text)
    assert "\r" not in cleaned
    assert "\u00a0" not in cleaned

    speakers = TranscriptParser.extract_speakers("Alice: Hello\nBob: Hi\nCharlie: Good morning")
    assert speakers == ["Alice", "Bob", "Charlie"]

def test_scanned_pdf_error_handling():
    # An empty or image-only PDF stream should raise DocumentParseError
    # rather than pretending it was read successfully
    with pytest.raises(DocumentParseError) as exc_info:
        TranscriptParser.parse_pdf(b"%PDF-1.4 dummy non-readable pdf stream")
    assert "Failed to parse PDF document" in str(exc_info.value) or "scanned" in str(exc_info.value)

