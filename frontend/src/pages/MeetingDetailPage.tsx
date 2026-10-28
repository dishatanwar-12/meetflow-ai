import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Alert } from '../components/ui/Alert';
import { Skeleton } from '../components/ui/Skeleton';
import { api } from '../services/api';
import { MeetingReviewWorkspaceData, Task } from '../types';
import { ReviewWorkspace } from '../components/meetings/ReviewWorkspace';
import { ConfirmOwnerModal } from '../components/tasks/ConfirmOwnerModal';
import { ConfirmDueDateModal } from '../components/tasks/ConfirmDueDateModal';
import { TaskDetailModal } from '../components/tasks/TaskDetailModal';
import { ExportModal } from '../components/exports/ExportModal';
import { GitHubExportModal } from '../components/exports/GitHubExportModal';
import { Sparkles, Download, Clock, ArrowLeft, RefreshCw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const MeetingDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isPM } = useAuth();

  const [workspaceData, setWorkspaceData] = useState<MeetingReviewWorkspaceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Modal states
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [ownerModalOpen, setOwnerModalOpen] = useState(false);
  const [dueDateModalOpen, setDueDateModalOpen] = useState(false);
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [githubModalOpen, setGithubModalOpen] = useState(false);

  useEffect(() => {
    if (id) {
      loadWorkspace(id);
    }
  }, [id]);

  const loadWorkspace = async (meetingId: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getMeetingReviewWorkspace(meetingId);
      setWorkspaceData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load meeting review workspace.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!id) return;
    setAnalyzing(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const res = await api.analyzeMeeting(id);
      setSuccessMsg(res.message || 'Analysis completed successfully.');
      await loadWorkspace(id);
    } catch (err: any) {
      setError(err.message || 'AI inference failed. Please verify NVIDIA API configuration.');
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-44 w-full rounded-xl" />
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
    );
  }

  if (!workspaceData) {
    return (
      <div className="space-y-4">
        <Alert type="error">{error || 'Meeting not found.'}</Alert>
        <Button variant="outline" size="sm" onClick={() => navigate('/meetings')}>
          <ArrowLeft className="w-4 h-4 mr-1.5" /> Back to Meetings
        </Button>
      </div>
    );
  }

  const { meeting } = workspaceData;

  return (
    <div className="space-y-6">
      {/* Top Navigation Back Link */}
      <button
        onClick={() => navigate('/meetings')}
        className="text-xs font-semibold text-slate-500 hover:text-slate-800 flex items-center gap-1.5 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Meetings
      </button>

      {/* Meeting Header Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2.5 flex-wrap">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900">{meeting.title}</h1>
            <Badge variant={meeting.status === 'reviewed' ? 'success' : meeting.status === 'processing' ? 'info' : 'amber'}>
              {meeting.status.toUpperCase()}
            </Badge>
          </div>

          <div className="flex items-center gap-4 text-xs text-slate-500 flex-wrap">
            <span>Client: <b className="text-slate-700">{meeting.client_name || 'N/A'}</b></span>
            <span>•</span>
            <span>Project: <b className="text-slate-700">{meeting.project_name || 'N/A'}</b></span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {meeting.meeting_date ? new Date(meeting.meeting_date).toLocaleString() : 'Date unspecified'} ({meeting.timezone})
            </span>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setExportModalOpen(true)}
          >
            <Download className="w-4 h-4 mr-1.5" />
            Export Outcomes
          </Button>

          {isPM && (
            <Button
              variant="primary"
              size="sm"
              isLoading={analyzing}
              onClick={handleAnalyze}
              className="bg-brand-900 hover:bg-brand-800 text-white"
            >
              <Sparkles className="w-4 h-4 mr-1.5 text-accent-100" />
              {meeting.status === 'reviewed' ? 'Re-Analyze with NVIDIA NIM' : 'Analyze with NVIDIA NIM'}
            </Button>
          )}
        </div>
      </div>

      {/* Notifications */}
      {error && <Alert type="error" title="Analysis Error">{error}</Alert>}
      {successMsg && <Alert type="success">{successMsg}</Alert>}

      {/* Review Workspace Component */}
      <ReviewWorkspace
        data={workspaceData}
        onRefresh={() => id && loadWorkspace(id)}
        onOpenTaskDetail={(t) => {
          setSelectedTask(t);
          setDetailModalOpen(true);
        }}
        onOpenConfirmOwner={(t) => {
          setSelectedTask(t);
          setOwnerModalOpen(true);
        }}
        onOpenConfirmDueDate={(t) => {
          setSelectedTask(t);
          setDueDateModalOpen(true);
        }}
      />

      {/* Modals */}
      <TaskDetailModal
        task={selectedTask}
        isOpen={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        onUpdate={() => id && loadWorkspace(id)}
      />

      <ConfirmOwnerModal
        task={selectedTask}
        isOpen={ownerModalOpen}
        onClose={() => setOwnerModalOpen(false)}
        onSuccess={() => id && loadWorkspace(id)}
      />

      <ConfirmDueDateModal
        task={selectedTask}
        isOpen={dueDateModalOpen}
        onClose={() => setDueDateModalOpen(false)}
        onSuccess={() => id && loadWorkspace(id)}
      />

      <ExportModal
        meetingId={meeting.id}
        isOpen={exportModalOpen}
        onClose={() => setExportModalOpen(false)}
        onOpenGitHubExport={() => setGithubModalOpen(true)}
      />

      <GitHubExportModal
        meetingId={meeting.id}
        isOpen={githubModalOpen}
        onClose={() => setGithubModalOpen(false)}
        onSuccess={() => id && loadWorkspace(id)}
      />
    </div>
  );
};
