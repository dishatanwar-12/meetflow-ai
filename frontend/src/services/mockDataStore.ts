import {
  AuthResponse,
  User,
  Client,
  Project,
  Meeting,
  MeetingReviewWorkspaceData,
  Decision,
  Task,
  Risk,
  UnansweredQuestion,
  DashboardStats,
  Blocker
} from '../types';

const STORAGE_KEY = 'meetflow_mock_db_v1';

interface DBState {
  users: Record<string, User & { password?: string }>;
  clients: Client[];
  projects: Project[];
  meetings: Meeting[];
  tasks: Task[];
  decisions: Decision[];
  risks: Risk[];
  blockers: Blocker[];
  questions: UnansweredQuestion[];
}

const DEFAULT_USERS: Record<string, User & { password?: string }> = {
  'admin@acme.com': {
    id: 'usr_admin_001',
    organization_id: 'org_acme_001',
    email: 'admin@acme.com',
    full_name: 'Alice Admin',
    role: 'admin',
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    password: 'AdminPass123!'
  },
  'pm@acme.com': {
    id: 'usr_pm_002',
    organization_id: 'org_acme_001',
    email: 'pm@acme.com',
    full_name: 'Peter ProjectManager',
    role: 'project_manager',
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    password: 'PMPass123!'
  },
  'member@acme.com': {
    id: 'usr_mem_003',
    organization_id: 'org_acme_001',
    email: 'member@acme.com',
    full_name: 'Mike Member',
    role: 'member',
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    password: 'MemberPass123!'
  },
  'viewer@acme.com': {
    id: 'usr_view_004',
    organization_id: 'org_acme_001',
    email: 'viewer@acme.com',
    full_name: 'Victor Viewer',
    role: 'viewer',
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    password: 'ViewerPass123!'
  }
};

const DEFAULT_CLIENTS: Client[] = [
  {
    id: 'cli_01',
    organization_id: 'org_acme_001',
    name: 'Acme Corp',
    organization_name: 'Acme Global Manufacturing',
    contact_name: 'Alice Admin',
    contact_email: 'alice@acme.com',
    industry: 'Industrial Manufacturing',
    is_archived: false,
    projects_count: 2,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'cli_02',
    organization_id: 'org_acme_001',
    name: 'Stark Industries',
    organization_name: 'Stark Global',
    contact_name: 'Tony Stark',
    contact_email: 'tony@stark.com',
    industry: 'Aerospace & Robotics',
    is_archived: false,
    projects_count: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'cli_03',
    organization_id: 'org_acme_001',
    name: 'Initech Global',
    organization_name: 'Initech Corporation',
    contact_name: 'Peter Gibbons',
    contact_email: 'peter@initech.com',
    industry: 'Financial Services',
    is_archived: false,
    projects_count: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

const DEFAULT_PROJECTS: Project[] = [
  {
    id: 'proj_01',
    organization_id: 'org_acme_001',
    client_id: 'cli_01',
    name: 'Website Redesign & Brand Identity',
    description: 'Enterprise web portal overhaul with modern design system and CMS integration.',
    client_name: 'Acme Corp',
    manager_name: 'Peter ProjectManager',
    status: 'active',
    tags: ['frontend', 'branding', 'react'],
    meetings_count: 3,
    tasks_count: 12,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'proj_02',
    organization_id: 'org_acme_001',
    client_id: 'cli_02',
    name: 'Arc Reactor Monitoring Platform',
    description: 'Real-time telemetry and predictive anomaly detection pipeline.',
    client_name: 'Stark Industries',
    manager_name: 'Alice Admin',
    status: 'active',
    tags: ['telemetry', 'ai', 'hardware'],
    meetings_count: 2,
    tasks_count: 9,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'proj_03',
    organization_id: 'org_acme_001',
    client_id: 'cli_03',
    name: 'Automated TPS Reporting Migration',
    description: 'Modernize legacy reporting batch jobs to cloud streaming analytics.',
    client_name: 'Initech Global',
    manager_name: 'Peter Gibbons',
    status: 'active',
    tags: ['cloud', 'data-pipeline'],
    meetings_count: 1,
    tasks_count: 7,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

const DEFAULT_MEETINGS: Meeting[] = [
  {
    id: 'meet_01',
    organization_id: 'org_acme_001',
    project_id: 'proj_01',
    client_id: 'cli_01',
    title: 'E2E Test Action Review Meeting',
    meeting_date: '2026-10-29T10:00:00Z',
    timezone: 'UTC',
    meeting_type: 'client_review',
    language: 'en',
    status: 'reviewed',
    client_name: 'Acme Corp',
    project_name: 'Website Redesign & Brand Identity',
    tasks_count: 8,
    decisions_count: 3,
    attendees_count: 12,
    created_at: new Date(Date.now() - 3600000).toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'meet_02',
    organization_id: 'org_acme_001',
    project_id: 'proj_02',
    client_id: 'cli_02',
    title: 'Telemetry Architecture Review',
    meeting_date: '2026-10-26T10:00:00Z',
    timezone: 'UTC',
    meeting_type: 'planning',
    language: 'en',
    status: 'reviewed',
    client_name: 'Stark Industries',
    project_name: 'Arc Reactor Monitoring Platform',
    tasks_count: 11,
    decisions_count: 4,
    attendees_count: 6,
    created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
    updated_at: new Date(Date.now() - 86400000 * 3).toISOString()
  },
  {
    id: 'meet_03',
    organization_id: 'org_acme_001',
    project_id: 'proj_01',
    client_id: 'cli_01',
    title: 'Acme Corp - Project Kickoff',
    meeting_date: '2026-10-22T10:30:00Z',
    timezone: 'UTC',
    meeting_type: 'discovery',
    language: 'en',
    status: 'reviewed',
    client_name: 'Acme Corp',
    project_name: 'Website Redesign & Brand Identity',
    tasks_count: 8,
    decisions_count: 2,
    attendees_count: 8,
    created_at: new Date(Date.now() - 86400000 * 7).toISOString(),
    updated_at: new Date(Date.now() - 86400000 * 7).toISOString()
  },
  {
    id: 'meet_04',
    organization_id: 'org_acme_001',
    project_id: 'proj_03',
    client_id: 'cli_03',
    title: 'Sprint Planning & TPS Sync',
    meeting_date: '2026-10-15T11:00:00Z',
    timezone: 'UTC',
    meeting_type: 'planning',
    language: 'en',
    status: 'reviewed',
    client_name: 'Initech Global',
    project_name: 'Automated TPS Reporting Migration',
    tasks_count: 5,
    decisions_count: 2,
    attendees_count: 5,
    created_at: new Date(Date.now() - 86400000 * 14).toISOString(),
    updated_at: new Date(Date.now() - 86400000 * 14).toISOString()
  }
];

const DEFAULT_TASKS: Task[] = [
  {
    id: 'tsk_01',
    meeting_id: 'meet_01',
    project_id: 'proj_01',
    title: 'Complete database schema migration scripts by Friday',
    description: 'Ensure compatibility with PostgreSQL 16 partition syntax.',
    owner_name: 'Bob Builder',
    owner_status: 'explicit',
    due_date: '2026-11-06',
    due_date_status: 'explicit',
    status: 'in_progress',
    priority: 'high',
    dependencies: [],
    evidence_type: 'transcript_quote',
    confirmation_required: false,
    project_name: 'Website Redesign & Brand Identity',
    meeting_title: 'E2E Test Action Review Meeting',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'tsk_02',
    meeting_id: 'meet_01',
    project_id: 'proj_01',
    title: 'Prepare the executive progress report for next Tuesday',
    owner_name: 'Alice Admin',
    owner_status: 'explicit',
    due_date: '2026-11-03',
    due_date_status: 'explicit',
    status: 'ready',
    priority: 'medium',
    dependencies: [],
    evidence_type: 'transcript_quote',
    confirmation_required: false,
    project_name: 'Website Redesign & Brand Identity',
    meeting_title: 'E2E Test Action Review Meeting',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'tsk_03',
    meeting_id: 'meet_02',
    project_id: 'proj_02',
    title: 'Configure high-throughput gRPC telemetry collector',
    owner_name: 'Tony Stark',
    owner_status: 'explicit',
    due_date: '2026-10-30',
    due_date_status: 'explicit',
    status: 'in_progress',
    priority: 'urgent',
    dependencies: [],
    evidence_type: 'transcript_quote',
    confirmation_required: false,
    project_name: 'Arc Reactor Monitoring Platform',
    meeting_title: 'Telemetry Architecture Review',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'tsk_04',
    meeting_id: 'meet_03',
    project_id: 'proj_01',
    title: 'Implement WCAG AA accessible contrast palette tokens',
    owner_name: 'Mike Member',
    owner_status: 'explicit',
    due_date: '2026-10-28',
    due_date_status: 'explicit',
    status: 'completed',
    priority: 'high',
    dependencies: [],
    evidence_type: 'transcript_quote',
    confirmation_required: false,
    project_name: 'Website Redesign & Brand Identity',
    meeting_title: 'Acme Corp - Project Kickoff',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

const DEFAULT_DECISIONS: Decision[] = [
  {
    id: 'dec_01',
    project_id: 'proj_01',
    meeting_id: 'meet_01',
    title: 'Migrate legacy MySQL tables to PostgreSQL 16',
    description: 'Required for JSONB indexing and streaming pipeline compatibility.',
    status: 'confirmed',
    owner_or_approver: 'Alice Admin',
    evidence_passage: 'We confirmed the decision to migrate legacy MySQL tables to PostgreSQL 16.',
    evidence_type: 'transcript_quote',
    confirmation_required: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'dec_02',
    project_id: 'proj_01',
    meeting_id: 'meet_01',
    title: 'Design palette: deep midnight navy with electric indigo accents',
    status: 'confirmed',
    owner_or_approver: 'Alice Admin',
    evidence_passage: 'We finalized the design palette: deep midnight navy with electric indigo accents and clean card shadows.',
    evidence_type: 'transcript_quote',
    confirmation_required: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

const DEFAULT_RISKS: Risk[] = [
  {
    id: 'rsk_01',
    project_id: 'proj_01',
    meeting_id: 'meet_01',
    description: 'If IAM permissions are delayed, we risk missing the staging freeze date.',
    potential_impact: 'High',
    likelihood: 'Medium',
    status: 'open',
    mitigation: 'Escalate to enterprise security architect.',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

const DEFAULT_QUESTIONS: UnansweredQuestion[] = [
  {
    id: 'que_01',
    project_id: 'proj_01',
    meeting_id: 'meet_01',
    question: 'Who will lead end-to-end integration testing suite?',
    suggested_person: 'Sarah Connor',
    status: 'open',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

class MockDataStore {
  private getState(): DBState {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        return JSON.parse(raw);
      }
    } catch {
      // fallback
    }
    const fresh: DBState = {
      users: DEFAULT_USERS,
      clients: DEFAULT_CLIENTS,
      projects: DEFAULT_PROJECTS,
      meetings: DEFAULT_MEETINGS,
      tasks: DEFAULT_TASKS,
      decisions: DEFAULT_DECISIONS,
      risks: DEFAULT_RISKS,
      blockers: [],
      questions: DEFAULT_QUESTIONS
    };
    this.saveState(fresh);
    return fresh;
  }

  private saveState(state: DBState) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      // storage full or disabled
    }
  }

  handleLogin(email: string, _password?: string): AuthResponse {
    const state = this.getState();
    const user = state.users[email?.toLowerCase()] || Object.values(state.users)[0];
    const token = `demo_jwt_token_${user.id}_${Date.now()}`;
    return {
      access_token: token,
      token_type: 'bearer',
      user: {
        id: user.id,
        organization_id: user.organization_id,
        email: user.email,
        full_name: user.full_name,
        role: user.role,
        is_active: true,
        created_at: user.created_at,
        updated_at: user.updated_at
      }
    };
  }

  handleRegister(data: { email: string; full_name?: string; organization_name?: string; role?: string }): AuthResponse {
    const state = this.getState();
    const newUser: User & { password?: string } = {
      id: `usr_${Date.now()}`,
      organization_id: 'org_acme_001',
      email: (data.email || 'user@example.com').toLowerCase(),
      full_name: data.full_name || 'Demo User',
      role: (data.role as any) || 'admin',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    state.users[newUser.email] = newUser;
    this.saveState(state);
    return this.handleLogin(newUser.email);
  }

  handleGetCurrentUser(): User {
    const state = this.getState();
    const storedUser = localStorage.getItem('meetflow_user');
    if (storedUser) {
      try {
        return JSON.parse(storedUser);
      } catch {
        // ignore
      }
    }
    return Object.values(state.users)[0];
  }

  handleDashboardStats(): DashboardStats {
    const state = this.getState();
    return {
      total_meetings: state.meetings.length,
      analyzed_meetings: state.meetings.filter(m => m.status === 'reviewed').length,
      total_tasks: state.tasks.length + 24,
      open_tasks: state.tasks.filter(t => t.status !== 'completed').length,
      tasks_needing_owner_confirmation: state.tasks.filter(t => t.owner_status === 'ambiguous' || t.owner_status === 'not_stated').length,
      tasks_needing_deadline_confirmation: state.tasks.filter(t => t.due_date_status === 'ambiguous' || t.due_date_status === 'not_stated').length,
      overdue_tasks: 3,
      unresolved_risks: state.risks.filter(r => r.status === 'open').length,
      open_blockers: 1,
      open_questions: state.questions.filter(q => q.status === 'open').length,
      recent_projects: state.projects.map(p => ({
        id: p.id,
        name: p.name,
        client_name: p.client_name,
        status: p.status,
        updated_at: p.updated_at
      })),
      recent_meetings: state.meetings.map(m => ({
        id: m.id,
        title: m.title,
        status: m.status,
        meeting_date: m.meeting_date,
        created_at: m.created_at
      }))
    };
  }

  handleGetMeetings(params?: { search?: string; status?: string }): Meeting[] {
    const state = this.getState();
    let res = [...state.meetings];
    if (params?.search) {
      const q = params.search.toLowerCase();
      res = res.filter(m => m.title.toLowerCase().includes(q));
    }
    return res;
  }

  handleGetMeeting(id: string): Meeting {
    const state = this.getState();
    return state.meetings.find(m => m.id === id) || state.meetings[0];
  }

  handleCreateMeeting(data: any): Meeting {
    const state = this.getState();
    const newM: Meeting = {
      id: `meet_${Date.now()}`,
      organization_id: 'org_acme_001',
      project_id: data.project_id || state.projects[0].id,
      client_id: data.client_id || state.clients[0].id,
      title: data.title || 'Untitled Meeting',
      meeting_date: data.meeting_date || new Date().toISOString(),
      timezone: data.timezone || 'UTC',
      meeting_type: data.meeting_type || 'discovery',
      language: 'en',
      status: 'reviewed',
      client_name: 'Acme Corp',
      project_name: 'Website Redesign & Brand Identity',
      tasks_count: 5,
      decisions_count: 2,
      attendees_count: 4,
      raw_transcript: data.transcript_text || '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    state.meetings.unshift(newM);
    this.saveState(state);
    return newM;
  }

  handleGetMeetingReview(meetingId: string): MeetingReviewWorkspaceData {
    const state = this.getState();
    const meeting = this.handleGetMeeting(meetingId);
    return {
      meeting: {
        ...meeting,
        raw_transcript: meeting.raw_transcript || 'Alice Admin: Welcome everyone. We will deploy the full stack today.\nBob Builder: All database migrations and tests are complete.'
      },
      attendees: [
        {
          id: 'att_01',
          meeting_id: meeting.id,
          name: 'Alice Admin',
          email: 'alice@acme.com',
          role: 'Host',
          is_external: false,
          created_at: new Date().toISOString()
        },
        {
          id: 'att_02',
          meeting_id: meeting.id,
          name: 'Bob Builder',
          email: 'bob@acme.com',
          role: 'Engineer',
          is_external: false,
          created_at: new Date().toISOString()
        }
      ],
      documents: [],
      summary_data: {
        meeting_summary: 'Successful alignment on deliverables, architecture, and deployment procedures.',
        topics: ['Frontend Redesign', 'Database Schema', 'Automated Testing', 'Deployment Automation']
      },
      decisions: state.decisions,
      tasks: state.tasks,
      risks: state.risks,
      blockers: [],
      questions: state.questions,
      analysis_warnings: []
    };
  }

  handleGetTasks(params?: { search?: string; status?: string }): Task[] {
    const state = this.getState();
    let res = [...state.tasks];
    if (params?.status) {
      res = res.filter(t => t.status === params.status);
    }
    if (params?.search) {
      const q = params.search.toLowerCase();
      res = res.filter(t => t.title.toLowerCase().includes(q));
    }
    return res;
  }

  handleUpdateTask(id: string, patch: Partial<Task>): Task {
    const state = this.getState();
    const idx = state.tasks.findIndex(t => t.id === id);
    if (idx !== -1) {
      state.tasks[idx] = { ...state.tasks[idx], ...patch, updated_at: new Date().toISOString() };
      this.saveState(state);
      return state.tasks[idx];
    }
    return { ...DEFAULT_TASKS[0], ...patch };
  }

  handleCreateTask(data: Partial<Task>): Task {
    const state = this.getState();
    const newTask: Task = {
      id: `tsk_${Date.now()}`,
      project_id: data.project_id || state.projects[0].id,
      meeting_id: data.meeting_id || state.meetings[0].id,
      title: data.title || 'New Task',
      description: data.description,
      owner_name: data.owner_name || 'Alice Admin',
      owner_status: data.owner_status || 'explicit',
      due_date: data.due_date || new Date(Date.now() + 86400000 * 3).toISOString().split('T')[0],
      due_date_status: data.due_date_status || 'explicit',
      status: (data.status as any) || 'ready',
      priority: (data.priority as any) || 'medium',
      dependencies: [],
      evidence_type: 'manual',
      confirmation_required: false,
      project_name: 'Website Redesign & Brand Identity',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    state.tasks.unshift(newTask);
    this.saveState(state);
    return newTask;
  }

  handleGetDecisions(): Decision[] {
    return this.getState().decisions;
  }

  handleConfirmDecision(id: string): Decision {
    const state = this.getState();
    const idx = state.decisions.findIndex(d => d.id === id);
    if (idx !== -1) {
      state.decisions[idx].status = 'confirmed';
      this.saveState(state);
      return state.decisions[idx];
    }
    return DEFAULT_DECISIONS[0];
  }

  handleRejectDecision(id: string): Decision {
    const state = this.getState();
    const idx = state.decisions.findIndex(d => d.id === id);
    if (idx !== -1) {
      state.decisions[idx].status = 'rejected';
      this.saveState(state);
      return state.decisions[idx];
    }
    return DEFAULT_DECISIONS[0];
  }

  handleGetRisks(): Risk[] {
    return this.getState().risks;
  }

  handleGetQuestions(): UnansweredQuestion[] {
    return this.getState().questions;
  }

  handleGetClients(): Client[] {
    return this.getState().clients;
  }

  handleGetProjects(): Project[] {
    return this.getState().projects;
  }
}

export const mockDataStore = new MockDataStore();
