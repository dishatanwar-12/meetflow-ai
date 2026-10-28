export type UserRole = 'admin' | 'project_manager' | 'member' | 'viewer';

export interface User {
  id: string;
  organization_id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Client {
  id: string;
  organization_id: string;
  name: string;
  organization_name?: string;
  contact_name?: string;
  contact_email?: string;
  industry?: string;
  website?: string;
  notes?: string;
  is_archived: boolean;
  projects_count?: number;
  created_at: string;
  updated_at: string;
}

export type ProjectStatus = 'active' | 'on_hold' | 'completed' | 'archived';

export interface Project {
  id: string;
  organization_id: string;
  client_id: string;
  name: string;
  description?: string;
  goals?: string;
  manager_id?: string;
  client_name?: string;
  manager_name?: string;
  start_date?: string;
  target_date?: string;
  status: ProjectStatus;
  tags: string[];
  meetings_count?: number;
  tasks_count?: number;
  created_at: string;
  updated_at: string;
}

export type MeetingType = 'discovery' | 'status_update' | 'client_review' | 'planning' | 'retrospective' | 'other';
export type MeetingStatus = 'draft' | 'processing' | 'reviewed' | 'archived';

export interface MeetingAttendee {
  id: string;
  meeting_id: string;
  name: string;
  email?: string;
  role?: string;
  is_external: boolean;
  speaker_label?: string;
  created_at: string;
}

export interface TranscriptDocument {
  id: string;
  meeting_id: string;
  filename: string;
  file_size: number;
  mime_type: string;
  created_at: string;
}

export interface Meeting {
  id: string;
  organization_id: string;
  project_id: string;
  client_id: string;
  title: string;
  description?: string;
  client_name?: string;
  project_name?: string;
  meeting_date?: string;
  timezone: string;
  meeting_type: MeetingType;
  language: string;
  status: MeetingStatus;
  raw_transcript?: string;
  tasks_count?: number;
  decisions_count?: number;
  created_at: string;
  updated_at: string;
}

export type DecisionStatus = 'proposed' | 'confirmed' | 'rejected' | 'superseded' | 'disputed';

export interface Decision {
  id: string;
  meeting_id: string;
  project_id: string;
  title: string;
  description?: string;
  status: DecisionStatus;
  decision_date?: string;
  owner_or_approver?: string;
  evidence_passage?: string;
  source_start?: number;
  source_end?: number;
  evidence_type: string;
  confirmation_required: boolean;
  superseded_by_id?: string;
  created_at: string;
  updated_at: string;
}

export type OwnerStatus = 'explicit' | 'user_confirmed' | 'not_stated' | 'ambiguous' | 'conflicting';
export type DueDateStatus = 'explicit' | 'resolved_from_meeting_date' | 'user_confirmed' | 'not_stated' | 'ambiguous' | 'conflicting';
export type TaskPriority = 'unspecified' | 'low' | 'medium' | 'high' | 'urgent';
export type TaskStatus = 'needs_clarification' | 'ready' | 'in_progress' | 'blocked' | 'completed' | 'cancelled';

export interface Task {
  id: string;
  meeting_id: string;
  project_id: string;
  project_name?: string;
  meeting_title?: string;
  title: string;
  description?: string;
  owner_name?: string;
  owner_user_id?: string;
  owner_status: OwnerStatus;
  due_date?: string;
  due_date_status: DueDateStatus;
  date_expression?: string;
  priority: TaskPriority;
  status: TaskStatus;
  dependencies: string[];
  related_decision_id?: string;
  evidence_passage?: string;
  source_start?: number;
  source_end?: number;
  evidence_type: string;
  confirmation_required: boolean;
  confirmation_reason?: string;
  is_overdue?: boolean;
  comments_count?: number;
  external_sync_url?: string;
  created_at: string;
  updated_at: string;
}

export interface TaskComment {
  id: string;
  task_id: string;
  user_id: string;
  user_name?: string;
  content: string;
  created_at: string;
}

export type RiskStatus = 'open' | 'mitigated' | 'accepted' | 'closed';

export interface Risk {
  id: string;
  meeting_id: string;
  project_id: string;
  description: string;
  potential_impact?: string;
  likelihood?: string;
  mitigation?: string;
  responsible_person?: string;
  evidence_passage?: string;
  source_start?: number;
  source_end?: number;
  status: RiskStatus;
  created_at: string;
  updated_at: string;
}

export interface Blocker {
  id: string;
  meeting_id: string;
  project_id: string;
  task_id?: string;
  task_title?: string;
  description: string;
  dependency_type: string;
  responsible_party?: string;
  evidence_passage?: string;
  resolution_question?: string;
  is_resolved: boolean;
  created_at: string;
  updated_at: string;
}

export type QuestionStatus = 'open' | 'answered' | 'deferred';

export interface UnansweredQuestion {
  id: string;
  meeting_id: string;
  project_id: string;
  question: string;
  clarification_reason?: string;
  related_entity_type?: string;
  related_entity_id?: string;
  evidence_passage?: string;
  suggested_person?: string;
  status: QuestionStatus;
  answer?: string;
  answered_by_name?: string;
  answered_at?: string;
  created_at: string;
  updated_at: string;
}

export interface MeetingReviewWorkspaceData {
  meeting: Meeting;
  attendees: MeetingAttendee[];
  documents: TranscriptDocument[];
  summary_data?: {
    meeting_summary?: string;
    topics?: string[];
    follow_up_topics?: string[];
    contradictions?: Array<{
      topic: string;
      statement_a: string;
      statement_b: string;
      evidence?: string;
      resolution_needed: string;
    }>;
  };
  decisions: Decision[];
  tasks: Task[];
  risks: Risk[];
  blockers: Blocker[];
  questions: UnansweredQuestion[];
  analysis_warnings: string[];
  latest_analysis_run?: {
    id: string;
    model_name: string;
    status: string;
    prompt_tokens: number;
    completion_tokens: number;
    error_message?: string;
    created_at: string;
  };
}

export interface DashboardStats {
  total_meetings: number;
  analyzed_meetings: number;
  total_tasks: number;
  open_tasks: number;
  tasks_needing_owner_confirmation: number;
  tasks_needing_deadline_confirmation: number;
  overdue_tasks: number;
  unresolved_risks: number;
  open_blockers: number;
  open_questions: number;
  recent_projects: Array<{
    id: string;
    name: string;
    client_name?: string;
    status: string;
    updated_at: string;
  }>;
  recent_meetings: Array<{
    id: string;
    title: string;
    status: string;
    meeting_date?: string;
    created_at: string;
  }>;
}

export interface TimelineItem {
  id: string;
  type: 'meeting' | 'decision' | 'task';
  title: string;
  timestamp: string;
  status?: string;
  details?: string;
  meeting_id?: string;
  meeting_title?: string;
}

export interface ContradictionConflict {
  id: string;
  type: string;
  title: string;
  description: string;
  first_meeting_title: string;
  first_meeting_date?: string;
  first_statement: string;
  second_meeting_title: string;
  second_meeting_date?: string;
  second_statement: string;
  suggested_resolution?: string;
  status: string;
}

