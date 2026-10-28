# MeetFlow AI — REST API Documentation

Base URL: `/api/v1`

All protected endpoints require a Bearer token in the `Authorization` header:
`Authorization: Bearer <access_token>`

---

## 1. Authentication (`/api/v1/auth`)

- `POST /auth/register` — Register a new user account.
- `POST /auth/login` — Login with username/email and password, returns JWT token.
- `GET /auth/me` — Retrieve current authenticated user profile and permissions.
- `POST /auth/logout` — Revoke / logout current session.

---

## 2. Clients (`/api/v1/clients`)

- `GET /clients` — List clients (search, pagination, active filter).
- `POST /clients` — Create a new client record.
- `GET /clients/{id}` — Retrieve client details and associated projects.
- `PUT /clients/{id}` — Update client info.
- `DELETE /clients/{id}` — Archive or delete client.

---

## 3. Projects (`/api/v1/projects`)

- `GET /projects` — List projects (filter by client, status, tag).
- `POST /projects` — Create project.
- `GET /projects/{id}` — Retrieve project details, milestones, meetings.
- `PUT /projects/{id}` — Update project details.
- `DELETE /projects/{id}` — Archive project.
- `GET /projects/{id}/timeline` — Meeting-to-meeting timeline and cross-meeting conflicts.

---

## 4. Meetings & Ingestion (`/api/v1/meetings`)

- `GET /meetings` — List meetings (filter by project, client, date).
- `POST /meetings` — Create a meeting draft.
- `GET /meetings/{id}` — Retrieve meeting details, attendees, transcript.
- `PUT /meetings/{id}` — Update meeting draft.
- `POST /meetings/{id}/upload` — Upload TXT, PDF, or DOCX transcript.
- `POST /meetings/{id}/analyze` — Initiate NVIDIA NIM LLM structured analysis.
- `GET /meetings/{id}/analysis-status` — Check analysis progress and token usage.
- `GET /meetings/{id}/review` — Full review workspace payload (decisions, tasks, risks, questions, transcript).

---

## 5. Decisions (`/api/v1/decisions`)

- `GET /decisions` — List decisions (filter by meeting, project, status).
- `PUT /decisions/{id}` — Update decision details or status (`confirmed`, `rejected`, `superseded`, `disputed`).
- `POST /decisions/{id}/confirm` — Confirm decision with audit trail.

---

## 6. Tasks / Action Items (`/api/v1/tasks`)

- `GET /tasks` — List tasks with filters (project, owner, status, priority, confirmation needed).
- `POST /tasks` — Create manual task.
- `GET /tasks/{id}` — Task details, evidence quote, offsets, comments, version history.
- `PUT /tasks/{id}` — Update task (title, description, status, priority).
- `POST /tasks/{id}/confirm-owner` — Confirm or assign task owner.
- `POST /tasks/{id}/confirm-due-date` — Confirm or resolve calendar due date.
- `POST /tasks/{id}/comments` — Add comment or activity note.

---

## 7. Risks & Questions (`/api/v1/risks`, `/api/v1/questions`)

- `GET /risks` / `PUT /risks/{id}` / `POST /risks/{id}/resolve`
- `GET /questions` / `PUT /questions/{id}` / `POST /questions/{id}/answer`

---

## 8. Exports & Integrations (`/api/v1/exports`)

- `GET /exports/meetings/{id}/csv` — Formula-injection protected CSV of tasks and decisions.
- `GET /exports/meetings/{id}/json` — Versioned structured JSON export.
- `GET /exports/meetings/{id}/markdown` — Executive markdown summary report.
- `GET /exports/meetings/{id}/pdf` — Formatted PDF report generation.
- `POST /exports/meetings/{id}/github/preview` — Preview tasks to be exported to GitHub Issues.
- `POST /exports/meetings/{id}/github/export` — Execute export to GitHub Issues repository.

---

## 9. Dashboard & System (`/api/v1/dashboard`, `/api/v1/system`)

- `GET /dashboard/stats` — Real database-backed KPIs, counts, tasks requiring confirmation, open risks.
- `GET /system/health` — API health check.
- `GET /system/providers` — Configured AI provider status (checks NVIDIA connectivity without exposing keys).

