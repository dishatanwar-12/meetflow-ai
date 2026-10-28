import logging
from typing import List, Dict, Any, Optional
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.task import Task, OwnerStatus, DueDateStatus
from backend.app.models.integration import ExternalTaskMapping
from backend.app.schemas.export import (
    GitHubExportPreviewResponse,
    GitHubExportPreviewItem,
    GitHubExportRequest,
    GitHubExportResponse,
    GitHubExportItemResult
)

logger = logging.getLogger(__name__)

class GitHubTrackerService:
    def __init__(self, db: AsyncSession, default_token: Optional[str] = None):
        self.db = db
        self.default_token = default_token

    async def preview_tasks_for_export(
        self,
        repository: str,
        tasks: List[Task]
    ) -> GitHubExportPreviewResponse:
        """
        Generates a pre-flight preview of tasks to be exported to GitHub Issues,
        highlighting unresolved uncertainties (missing owners, unconfirmed dates).
        """
        preview_items = []
        ready_count = 0
        unresolved_count = 0

        for t in tasks:
            missing = []
            if t.owner_status in [OwnerStatus.NOT_STATED, OwnerStatus.AMBIGUOUS]:
                missing.append("Owner not confirmed")
            if t.due_date_status in [DueDateStatus.NOT_STATED, DueDateStatus.AMBIGUOUS]:
                missing.append("Due date not confirmed")

            is_ready = len(missing) == 0
            if is_ready:
                ready_count += 1
            else:
                unresolved_count += 1

            preview_items.append(GitHubExportPreviewItem(
                task_id=t.id,
                title=t.title,
                description=t.description,
                owner=t.owner_name or "Unassigned",
                due_date=t.due_date.strftime("%Y-%m-%d") if t.due_date else (t.date_expression or "None"),
                priority=t.priority.value if hasattr(t.priority, "value") else str(t.priority),
                status=t.status.value if hasattr(t.status, "value") else str(t.status),
                is_ready_for_export=is_ready,
                missing_fields=missing
            ))

        return GitHubExportPreviewResponse(
            repository=repository,
            total_tasks=len(tasks),
            ready_tasks=ready_count,
            unresolved_tasks=unresolved_count,
            tasks=preview_items
        )

    async def export_tasks_to_github(
        self,
        request: GitHubExportRequest,
        token: Optional[str] = None
    ) -> GitHubExportResponse:
        """
        Creates GitHub Issues via official REST API for the selected tasks.
        Includes idempotency checks against existing ExternalTaskMapping.
        """
        auth_token = token or request.personal_access_token or self.default_token
        if not auth_token:
            raise ValueError("A GitHub Personal Access Token is required to export issues.")

        repo = request.repository.strip()
        if "/" not in repo:
            raise ValueError("Repository must be in 'owner/repo' format (e.g., 'acme-corp/project-tracker').")

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "MeetFlow-AI-Tracker"
        }

        api_url = f"https://api.github.com/repos/{repo}/issues"
        results: List[GitHubExportItemResult] = []
        created_count = 0
        failed_count = 0

        async with httpx.AsyncClient(timeout=30.0) as client:
            for task_id in request.task_ids:
                # 1. Fetch task
                res = await self.db.execute(select(Task).where(Task.id == task_id))
                task = res.scalar_one_or_none()
                if not task:
                    failed_count += 1
                    results.append(GitHubExportItemResult(
                        task_id=task_id,
                        issue_number=0,
                        issue_url="",
                        success=False,
                        error="Task not found in local database."
                    ))
                    continue

                # 2. Check if already exported (Idempotency)
                map_res = await self.db.execute(
                    select(ExternalTaskMapping).where(
                        ExternalTaskMapping.task_id == task.id,
                        ExternalTaskMapping.provider == "github"
                    )
                )
                existing_mapping = map_res.scalar_one_or_none()
                if existing_mapping:
                    # Already mapped and exported
                    created_count += 1
                    results.append(GitHubExportItemResult(
                        task_id=task.id,
                        issue_number=int(existing_mapping.external_task_id) if existing_mapping.external_task_id.isdigit() else 0,
                        issue_url=existing_mapping.external_url,
                        success=True,
                        error="Task already exported previously."
                    ))
                    continue

                # 3. Check unresolved approval constraints
                if not request.allow_unassigned_export and task.owner_status in [OwnerStatus.NOT_STATED, OwnerStatus.AMBIGUOUS]:
                    failed_count += 1
                    results.append(GitHubExportItemResult(
                        task_id=task.id,
                        issue_number=0,
                        issue_url="",
                        success=False,
                        error="Task owner is unresolved. Check 'Allow unassigned export' to proceed."
                    ))
                    continue

                # 4. Construct Issue Body with trace evidence
                due_info = task.due_date.strftime("%Y-%m-%d") if task.due_date else (task.date_expression or "Not confirmed")
                owner_info = task.owner_name or "Unassigned"

                issue_body = f"""### Action Item (Created by MeetFlow AI)

**Description:**
{task.description or 'No description provided.'}

---
- **Assigned Owner:** {owner_info} ({task.owner_status.value if hasattr(task.owner_status, 'value') else task.owner_status})
- **Due Date:** {due_info} ({task.due_date_status.value if hasattr(task.due_date_status, 'value') else task.due_date_status})
- **Priority:** {task.priority.value if hasattr(task.priority, 'value') else task.priority}
- **Status:** {task.status.value if hasattr(task.status, 'value') else task.status}

**Supporting Meeting Evidence:**
> "{task.evidence_passage or 'No direct quote captured.'}"
"""

                issue_payload = {
                    "title": task.title,
                    "body": issue_body,
                    "labels": ["meetflow-ai", f"priority:{task.priority.value if hasattr(task.priority, 'value') else task.priority}"]
                }

                try:
                    resp = await client.post(api_url, headers=headers, json=issue_payload)
                    if resp.status_code == 201:
                        data = resp.json()
                        issue_num = data.get("number", 0)
                        html_url = data.get("html_url", "")

                        # Store external mapping
                        mapping = ExternalTaskMapping(
                            task_id=task.id,
                            provider="github",
                            external_task_id=str(issue_num),
                            external_url=html_url,
                            sync_status="synced"
                        )
                        self.db.add(mapping)
                        await self.db.commit()

                        created_count += 1
                        results.append(GitHubExportItemResult(
                            task_id=task.id,
                            issue_number=issue_num,
                            issue_url=html_url,
                            success=True
                        ))
                    elif resp.status_code == 404:
                        failed_count += 1
                        results.append(GitHubExportItemResult(
                            task_id=task.id,
                            issue_number=0,
                            issue_url="",
                            success=False,
                            error=f"Repository '{repo}' not found or token lacks access."
                        ))
                    elif resp.status_code == 401:
                        failed_count += 1
                        results.append(GitHubExportItemResult(
                            task_id=task.id,
                            issue_number=0,
                            issue_url="",
                            success=False,
                            error="GitHub token is invalid or expired."
                        ))
                    else:
                        failed_count += 1
                        results.append(GitHubExportItemResult(
                            task_id=task.id,
                            issue_number=0,
                            issue_url="",
                            success=False,
                            error=f"GitHub API returned error HTTP {resp.status_code}: {resp.text}"
                        ))
                except Exception as e:
                    failed_count += 1
                    results.append(GitHubExportItemResult(
                        task_id=task.id,
                        issue_number=0,
                        issue_url="",
                        success=False,
                        error=f"Network exception calling GitHub: {str(e)}"
                    ))

        return GitHubExportResponse(
            repository=repo,
            total_requested=len(request.task_ids),
            total_created=created_count,
            total_failed=failed_count,
            results=results
        )

