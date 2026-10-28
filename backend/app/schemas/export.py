from typing import List, Optional
from pydantic import BaseModel

class GitHubExportPreviewItem(BaseModel):
    task_id: str
    title: str
    description: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    is_ready_for_export: bool
    missing_fields: List[str] = []

class GitHubExportPreviewResponse(BaseModel):
    repository: str
    total_tasks: int
    ready_tasks: int
    unresolved_tasks: int
    tasks: List[GitHubExportPreviewItem]

class GitHubExportRequest(BaseModel):
    repository: str  # owner/repo format
    personal_access_token: Optional[str] = None  # User provided or configured in workspace
    task_ids: List[str]
    allow_unassigned_export: bool = False
    allow_undated_export: bool = True

class GitHubExportItemResult(BaseModel):
    task_id: str
    issue_number: int
    issue_url: str
    success: bool
    error: Optional[str] = None

class GitHubExportResponse(BaseModel):
    repository: str
    total_requested: int
    total_created: int
    total_failed: int
    results: List[GitHubExportItemResult]

