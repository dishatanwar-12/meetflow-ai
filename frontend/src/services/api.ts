import {
  AuthResponse,
  User,
  Client,
  Project,
  Meeting,
  MeetingReviewWorkspaceData,
  Decision,
  Task,
  TaskComment,
  Risk,
  UnansweredQuestion,
  DashboardStats,
  TimelineItem,
  ContradictionConflict
} from '../types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

class ApiClient {
  private getHeaders(isFormData = false): HeadersInit {
    const headers: Record<string, string> = {};
    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
    }
    const token = localStorage.getItem('meetflow_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const isFormData = options.body instanceof FormData;
    const headers = { ...this.getHeaders(isFormData), ...options.headers };

    const url = `${BASE_URL}${endpoint}`;
    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
      localStorage.removeItem('meetflow_token');
      localStorage.removeItem('meetflow_user');
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        window.location.href = '/login';
      }
    }

    if (!response.ok) {
      let errorMessage = `Request failed with status ${response.status}`;
      try {
        const errorJson = await response.json();
        errorMessage = errorJson.detail || errorJson.message || errorMessage;
      } catch {
        // use default
      }
      throw new Error(errorMessage);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json() as Promise<T>;
  }

  // Auth
  async login(email: string, password: string):Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(data: { email: string; password: string; full_name: string; organization_name: string; role?: string }): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  // Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    return this.request<DashboardStats>('/dashboard/stats');
  }

  // Clients
  async getClients(search?: string): Promise<Client[]> {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.request<Client[]>(`/clients${query}`);
  }

  async createClient(data: Partial<Client>): Promise<Client> {
    return this.request<Client>('/clients', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateClient(id: string, data: Partial<Client>): Promise<Client> {
    return this.request<Client>(`/clients/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Projects
  async getProjects(params?: { client_id?: string; status?: string; search?: string }): Promise<Project[]> {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request<Project[]>(`/projects${query ? `?${query}` : ''}`);
  }

  async getProject(id: string): Promise<Project> {
    return this.request<Project>(`/projects/${id}`);
  }

  async createProject(data: Partial<Project>): Promise<Project> {
    return this.request<Project>('/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateProject(id: string, data: Partial<Project>): Promise<Project> {
    return this.request<Project>(`/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async getProjectTimeline(id: string): Promise<TimelineItem[]> {
    return this.request<TimelineItem[]>(`/projects/${id}/timeline`);
  }

  async getProjectConflicts(id: string): Promise<ContradictionConflict[]> {
    return this.request<ContradictionConflict[]>(`/projects/${id}/conflicts`);
  }

  // Meetings
  async getMeetings(params?: { project_id?: string; client_id?: string; status?: string; search?: string }): Promise<Meeting[]> {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request<Meeting[]>(`/meetings${query ? `?${query}` : ''}`);
  }

  async getMeeting(id: string): Promise<Meeting> {
    return this.request<Meeting>(`/meetings/${id}`);
  }

  async createMeeting(data: any): Promise<Meeting> {
    return this.request<Meeting>('/meetings', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateMeeting(id: string, data: Partial<Meeting>): Promise<Meeting> {
    return this.request<Meeting>(`/meetings/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async uploadMeetingTranscript(meetingId: string, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.request<any>(`/meetings/${meetingId}/upload`, {
      method: 'POST',
      body: formData,
    });
  }

  async analyzeMeeting(meetingId: string): Promise<{ success: boolean; message: string; meeting_id: string; status: string }> {
    return this.request<{ success: boolean; message: string; meeting_id: string; status: string }>(
      `/meetings/${meetingId}/analyze`,
      { method: 'POST' }
    );
  }

  async getMeetingReviewWorkspace(meetingId: string): Promise<MeetingReviewWorkspaceData> {
    return this.request<MeetingReviewWorkspaceData>(`/meetings/${meetingId}/review`);
  }

  // Decisions
  async getDecisions(params?: { meeting_id?: string; project_id?: string; status?: string }): Promise<Decision[]> {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request<Decision[]>(`/decisions${query ? `?${query}` : ''}`);
  }

  async updateDecision(id: string, data: Partial<Decision>): Promise<Decision> {
    return this.request<Decision>(`/decisions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async confirmDecision(id: string): Promise<Decision> {
    return this.request<Decision>(`/decisions/${id}/confirm`, { method: 'POST' });
  }

  async rejectDecision(id: string): Promise<Decision> {
    return this.request<Decision>(`/decisions/${id}/reject`, { method: 'POST' });
  }

  // Tasks
  async getTasks(params?: {
    project_id?: string;
    meeting_id?: string;
    status?: string;
    priority?: string;
    needs_confirmation?: boolean;
    overdue_only?: boolean;
    search?: string;
  }): Promise<Task[]> {
    const cleanParams: Record<string, string> = {};
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') {
          cleanParams[k] = String(v);
        }
      });
    }
    const query = new URLSearchParams(cleanParams).toString();
    return this.request<Task[]>(`/tasks${query ? `?${query}` : ''}`);
  }

  async getTask(id: string): Promise<Task> {
    return this.request<Task>(`/tasks/${id}`);
  }

  async createTask(data: Partial<Task>): Promise<Task> {
    return this.request<Task>('/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTask(id: string, data: Partial<Task>): Promise<Task> {
    return this.request<Task>(`/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async confirmTaskOwner(id: string, owner_name: string, owner_user_id?: string): Promise<Task> {
    return this.request<Task>(`/tasks/${id}/confirm-owner`, {
      method: 'POST',
      body: JSON.stringify({ owner_name, owner_user_id }),
    });
  }

  async confirmTaskDueDate(id: string, due_date: string): Promise<Task> {
    return this.request<Task>(`/tasks/${id}/confirm-due-date`, {
      method: 'POST',
      body: JSON.stringify({ due_date }),
    });
  }

  async getTaskComments(taskId: string): Promise<TaskComment[]> {
    return this.request<TaskComment[]>(`/tasks/${taskId}/comments`);
  }

  async addTaskComment(taskId: string, content: string): Promise<TaskComment> {
    return this.request<TaskComment>(`/tasks/${taskId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
  }

  // Risks & Questions
  async getRisks(params?: { meeting_id?: string; project_id?: string }): Promise<Risk[]> {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request<Risk[]>(`/risks${query ? `?${query}` : ''}`);
  }

  async resolveRisk(id: string): Promise<Risk> {
    return this.request<Risk>(`/risks/${id}/resolve`, { method: 'POST' });
  }

  async getQuestions(params?: { meeting_id?: string; project_id?: string }): Promise<UnansweredQuestion[]> {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request<UnansweredQuestion[]>(`/questions${query ? `?${query}` : ''}`);
  }

  async answerQuestion(id: string, answer: string): Promise<UnansweredQuestion> {
    return this.request<UnansweredQuestion>(`/questions/${id}/answer`, {
      method: 'POST',
      body: JSON.stringify({ answer }),
    });
  }

  // Exports
  getDownloadUrl(type: 'csv' | 'json' | 'markdown' | 'pdf', meetingId: string): string {
    const token = localStorage.getItem('meetflow_token') || '';
    return `${BASE_URL}/exports/meetings/${meetingId}/${type}?token=${token}`;
  }

  async previewGitHubExport(meetingId: string, repository: string): Promise<any> {
    return this.request<any>(
      `/exports/meetings/${meetingId}/github/preview?repository=${encodeURIComponent(repository)}`,
      { method: 'POST' }
    );
  }

  async executeGitHubExport(meetingId: string, data: any): Promise<any> {
    return this.request<any>(`/exports/meetings/${meetingId}/github/export`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // System
  async getSystemProviders(): Promise<any> {
    return this.request<any>('/system/providers');
  }

  async getSystemHealth(): Promise<any> {
    return this.request<any>('/system/health');
  }
}

export const api = new ApiClient();

