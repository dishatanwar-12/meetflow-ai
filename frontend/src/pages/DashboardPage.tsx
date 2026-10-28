import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Skeleton } from '../components/ui/Skeleton';
import { api } from '../services/api';
import { DashboardStats } from '../types';
import {
  Video,
  CheckSquare,
  AlertTriangle,
  HelpCircle,
  Plus,
  ArrowRight,
  Sparkles,
  Clock,
  ShieldAlert
} from 'lucide-react';
import { MeetingWizardModal } from '../components/meetings/MeetingWizardModal';

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [wizardOpen, setWizardOpen] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoading(true);
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Meeting-to-Action Dashboard</h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time meeting outcome intelligence and commitment tracking.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="primary" size="md" onClick={() => setWizardOpen(true)}>
            <Plus className="w-4 h-4 mr-1.5" />
            New Meeting
          </Button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-5 border-l-4 border-l-brand-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Total Meetings</span>
            <Video className="w-4 h-4 text-brand-800" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900 mt-2">
            {loading ? <Skeleton className="h-8 w-16" /> : stats?.total_meetings || 0}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            {stats?.analyzed_meetings || 0} analyzed with NVIDIA NIM
          </div>
        </Card>

        <Card className="p-5 border-l-4 border-l-amber-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Needs Confirmation</span>
            <AlertTriangle className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900 mt-2">
            {loading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              (stats?.tasks_needing_owner_confirmation || 0) + (stats?.tasks_needing_deadline_confirmation || 0)
            )}
          </div>
          <div className="text-xs text-amber-700 font-medium mt-1">
            {stats?.tasks_needing_owner_confirmation || 0} owners, {stats?.tasks_needing_deadline_confirmation || 0} dates
          </div>
        </Card>

        <Card className="p-5 border-l-4 border-l-rose-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Overdue Tasks</span>
            <ShieldAlert className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900 mt-2">
            {loading ? <Skeleton className="h-8 w-16" /> : stats?.overdue_tasks || 0}
          </div>
          <div className="text-xs text-slate-500 mt-1">Confirmed valid deadlines</div>
        </Card>

        <Card className="p-5 border-l-4 border-l-accent-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Open Questions</span>
            <HelpCircle className="w-4 h-4 text-accent-500" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900 mt-2">
            {loading ? <Skeleton className="h-8 w-16" /> : stats?.open_questions || 0}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            {stats?.unresolved_risks || 0} unresolved risks
          </div>
        </Card>
      </div>

      {/* Two Column Section: Recent Meetings & Active Projects */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Meetings */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Meetings</CardTitle>
            <Link to="/meetings" className="text-xs font-semibold text-brand-900 hover:underline flex items-center gap-1">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </CardHeader>
          <CardContent className="divide-y divide-slate-100 p-0">
            {loading ? (
              <div className="p-6 space-y-3">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : !stats?.recent_meetings || stats.recent_meetings.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                No meetings recorded yet. Click "New Meeting" to start.
              </div>
            ) : (
              stats.recent_meetings.map((m) => (
                <Link
                  key={m.id}
                  to={`/meetings/${m.id}`}
                  className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors block"
                >
                  <div className="space-y-1">
                    <div className="text-sm font-semibold text-slate-900">{m.title}</div>
                    <div className="text-xs text-slate-400">
                      {m.meeting_date ? new Date(m.meeting_date).toLocaleDateString() : 'Date unspecified'}
                    </div>
                  </div>
                  <Badge variant={m.status === 'reviewed' ? 'success' : 'amber'}>
                    {m.status.toUpperCase()}
                  </Badge>
                </Link>
              ))
            )}
          </CardContent>
        </Card>

        {/* Recently Updated Projects */}
        <Card>
          <CardHeader>
            <CardTitle>Active Projects</CardTitle>
            <Link to="/projects" className="text-xs font-semibold text-brand-900 hover:underline flex items-center gap-1">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </CardHeader>
          <CardContent className="divide-y divide-slate-100 p-0">
            {loading ? (
              <div className="p-6 space-y-3">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : !stats?.recent_projects || stats.recent_projects.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                No active projects found.
              </div>
            ) : (
              stats.recent_projects.map((p) => (
                <Link
                  key={p.id}
                  to={`/projects/${p.id}`}
                  className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors block"
                >
                  <div className="space-y-1">
                    <div className="text-sm font-semibold text-slate-900">{p.name}</div>
                    <div className="text-xs text-slate-400">Client: {p.client_name || 'N/A'}</div>
                  </div>
                  <Badge variant="neutral">{p.status.toUpperCase()}</Badge>
                </Link>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      <MeetingWizardModal
        isOpen={wizardOpen}
        onClose={() => setWizardOpen(false)}
        onSuccess={(id) => {
          loadStats();
          window.location.href = `/meetings/${id}`;
        }}
      />
    </div>
  );
};

