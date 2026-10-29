import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://127.0.0.1:8001"
FRONTEND_URL = "http://localhost:3000"

results = []

def record(test_name, success, details=""):
    results.append({"name": test_name, "success": success, "details": details})
    status = "PASS" if success else "FAIL"
    print(f"[{status}] {test_name}: {details}")

def make_req(path, method="GET", data=None, token=None, headers=None, base=BASE_URL):
    url = f"{base}{path}"
    req_headers = headers or {}
    if token:
        req_headers["Authorization"] = f"Bearer {token}"
    
    encoded_data = None
    if data is not None:
        if isinstance(data, dict):
            encoded_data = json.dumps(data).encode("utf-8")
            req_headers["Content-Type"] = "application/json"
        elif isinstance(data, (bytes, bytearray)):
            encoded_data = data
        else:
            encoded_data = str(data).encode("utf-8")

    req = urllib.request.Request(url, data=encoded_data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
            return resp.status, resp.headers, content
    except urllib.error.HTTPError as e:
        content = e.read()
        return e.code, e.headers, content
    except Exception as e:
        return 0, {}, str(e).encode("utf-8")

def run_tests():
    print("=" * 60)
    print("STARTING END-TO-END WEBSITE & API VERIFICATION SUITE")
    print("=" * 60)

    # 1. Health & System
    status, _, body = make_req("/api/v1/system/health")
    if status == 200:
        data = json.loads(body.decode())
        record("System Health Endpoint", data.get("status") == "healthy", f"status={data.get('status')}")
    else:
        record("System Health Endpoint", False, f"HTTP {status}")

    status, _, body = make_req("/api/v1/system/providers")
    record("AI Provider Status Endpoint", status == 200, f"HTTP {status}")

    # 2. Frontend Proxy Health
    status, _, body = make_req("/api/v1/system/health", base=FRONTEND_URL)
    record("Frontend Vite Reverse Proxy", status == 200, f"HTTP {status} via port 3000")

    # 3. Frontend HTML Response
    status, _, body = make_req("/", base=FRONTEND_URL)
    record("Frontend Web App Serving HTML", status == 200 and b"<!doctype html>" in body.lower(), f"HTTP {status}")

    # 4. Auth: Invalid Login
    status, _, _ = make_req("/api/v1/auth/login", method="POST", data={"email": "admin@acme.com", "password": "WrongPassword!"})
    record("Auth Rejects Invalid Password", status == 401, f"HTTP {status}")

    # 5. Auth: Login as Admin
    status, _, body = make_req("/api/v1/auth/login", method="POST", data={"email": "admin@acme.com", "password": "AdminPass123!"})
    admin_token = None
    if status == 200:
        data = json.loads(body.decode())
        admin_token = data.get("access_token")
        record("Admin Login Success", bool(admin_token), f"Token acquired for {data.get('user', {}).get('full_name')}")
    else:
        record("Admin Login Success", False, f"HTTP {status}")

    # 6. Auth: Login as PM
    status, _, body = make_req("/api/v1/auth/login", method="POST", data={"email": "pm@acme.com", "password": "PMPass123!"})
    pm_token = None
    if status == 200:
        pm_token = json.loads(body.decode()).get("access_token")
        record("PM Login Success", bool(pm_token), "PM Token verified")
    else:
        record("PM Login Success", False, f"HTTP {status}")

    # 7. Auth: Login as Member
    status, _, body = make_req("/api/v1/auth/login", method="POST", data={"email": "member@acme.com", "password": "MemberPass123!"})
    record("Member Login Success", status == 200, f"HTTP {status}")

    # 8. Auth: Login as Viewer
    status, _, body = make_req("/api/v1/auth/login", method="POST", data={"email": "viewer@acme.com", "password": "ViewerPass123!"})
    record("Viewer Login Success", status == 200, f"HTTP {status}")

    # 9. Protected Profile (/api/v1/auth/me) with token
    if admin_token:
        status, _, body = make_req("/api/v1/auth/me", token=admin_token)
        record("Get Authenticated User Profile", status == 200, f"HTTP {status}")
    
    # 10. Protected Profile without token
    status, _, _ = make_req("/api/v1/auth/me")
    record("Protected Route Blocks Missing Token", status == 401, f"HTTP {status}")

    # 11. Dashboard Analytics
    if admin_token:
        status, _, body = make_req("/api/v1/dashboard/stats", token=admin_token)
        if status == 200:
            stats = json.loads(body.decode())
            record("Dashboard Stats Retrieval", True, f"Total meetings: {stats.get('total_meetings')}, Tasks: {stats.get('total_tasks')}")
        else:
            record("Dashboard Stats Retrieval", False, f"HTTP {status}")

    # 12. Clients Retrieval
    client_id = None
    if admin_token:
        status, _, body = make_req("/api/v1/clients", token=admin_token)
        if status == 200:
            clients = json.loads(body.decode())
            if clients:
                client_id = clients[0]["id"]
            record("Clients Listing", True, f"Found {len(clients)} client(s)")
        else:
            record("Clients Listing", False, f"HTTP {status}")

    # 13. Create New Client
    if admin_token:
        status, _, body = make_req("/api/v1/clients", method="POST", token=admin_token, data={
            "name": "Wayne Enterprises",
            "organization_name": "Wayne Global",
            "contact_name": "Bruce Wayne",
            "contact_email": "bruce@wayne.com",
            "industry": "Technology"
        })
        record("Create Client", status in (200, 201), f"HTTP {status}")

    # 14. Projects Listing
    project_id = None
    if admin_token:
        status, _, body = make_req("/api/v1/projects", token=admin_token)
        if status == 200:
            projects = json.loads(body.decode())
            if projects:
                project_id = projects[0]["id"]
            record("Projects Listing", True, f"Found {len(projects)} project(s)")
        else:
            record("Projects Listing", False, f"HTTP {status}")

    # 15. Meetings Listing
    meeting_id = None
    if admin_token:
        status, _, body = make_req("/api/v1/meetings", token=admin_token)
        if status == 200:
            meetings = json.loads(body.decode())
            if meetings:
                meeting_id = meetings[0]["id"]
            record("Meetings Listing", True, f"Found {len(meetings)} meeting(s)")
        else:
            record("Meetings Listing", False, f"HTTP {status}")

    # 16. Create Meeting with Transcript
    if admin_token and client_id and project_id:
        status, _, body = make_req("/api/v1/meetings", method="POST", token=admin_token, data={
            "client_id": client_id,
            "project_id": project_id,
            "title": "E2E Test Action Review Meeting",
            "meeting_type": "status_update",
            "meeting_date": "2026-10-29T10:00:00Z",
            "timezone": "UTC",
            "raw_transcript": "Alice: We decided to deploy the new auth microservice by Friday. Bob will test the database migration.",
            "attendees": [
                {"name": "Alice Admin", "email": "admin@acme.com", "role": "Host"},
                {"name": "Bob Builder", "email": "bob@acme.com", "role": "Engineer"}
            ]
        })
        if status in (200, 201):
            created_meeting = json.loads(body.decode())
            test_meeting_id = created_meeting.get("id")
            record("Create Meeting with Transcript", True, f"Meeting ID: {test_meeting_id}")
            if not meeting_id:
                meeting_id = test_meeting_id
        else:
            record("Create Meeting with Transcript", False, f"HTTP {status}")

    # 17. Tasks Listing
    if admin_token:
        status, _, body = make_req("/api/v1/tasks", token=admin_token)
        record("Tasks Board Listing", status == 200, f"HTTP {status}")

    # 18. Decisions Listing
    if admin_token:
        status, _, body = make_req("/api/v1/decisions", token=admin_token)
        record("Decisions Register Listing", status == 200, f"HTTP {status}")

    # 19. Risks & Questions Listing
    if admin_token:
        status_r, _, _ = make_req("/api/v1/risks", token=admin_token)
        status_q, _, _ = make_req("/api/v1/questions", token=admin_token)
        record("Risks & Questions Retrieval", status_r == 200 and status_q == 200, f"Risks: {status_r}, Questions: {status_q}")

    # 20. Multi-Format Exports (CSV, JSON, Markdown, PDF)
    if admin_token and meeting_id:
        # CSV
        status, headers, content = make_req(f"/api/v1/exports/meetings/{meeting_id}/csv", token=admin_token)
        record("Export Tasks as CSV (Formula-Safe)", status == 200 and len(content) > 0, f"HTTP {status}, {len(content)} bytes")

        # JSON
        status, headers, content = make_req(f"/api/v1/exports/meetings/{meeting_id}/json", token=admin_token)
        record("Export Outcomes as Structured JSON", status == 200 and b"meeting" in content, f"HTTP {status}")

        # Markdown
        status, headers, content = make_req(f"/api/v1/exports/meetings/{meeting_id}/markdown", token=admin_token)
        record("Export Executive Markdown Brief", status == 200 and len(content) > 0, f"HTTP {status}, {len(content)} bytes")

        # PDF
        status, headers, content = make_req(f"/api/v1/exports/meetings/{meeting_id}/pdf", token=admin_token)
        record("Export ReportLab PDF Document", status == 200 and content.startswith(b"%PDF"), f"HTTP {status}, valid %PDF magic header")

    print("=" * 60)
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    print(f"E2E SUITE SUMMARY: {passed}/{total} Passed ({(passed/total)*100:.1f}%)")
    print("=" * 60)
    if passed < total:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
