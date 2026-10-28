import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Skeleton } from '../components/ui/Skeleton';
import { api } from '../services/api';
import { Meeting } from '../types';
import { Video, Plus, Search, Clock, ArrowRight, CheckSquare, Scale } from 'lucide-react';
import { MeetingWizardModal } from '../components/meetings/MeetingWizardModal';

export const MeetingsPage: React.FC = () => {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [wizardOpen, setWizardOpen] = useState(false);

  useEffect(() => {
    loadMeetings();
  }, [search, statusFilter]);

  const loadMeetings = async () => {
    setLoading(true);
    try {
      const data = await api.getMeetings({
        search: search || undefined,
        status: statusFilter || undefined,
      });
      setMeetings(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Meetings</h1>
          <p className="text-xs text-slate-500 mt-1">
            Capture, analyze, and review client meetings and action items.
          </p>
        </div>
        <Button variant="primary" size="md" onClick={() => setWizardOpen(true)}>
          <Plus className="w-4 h-4 mr-1.5" />
          New Meeting
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search meetings by title, description or notes..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-brand-800 bg-white"
          />
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3.5 py-2 text-xs border border-slate-300 rounded-lg bg-white text-slate-700"
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="processing">Processing</option>
          <option value="reviewed">Reviewed</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      {/* Meetings List */}
      {loading ? (
        <div className="space-y-3">
          <Skeleton className="h-20 w-full rounded-xl" />
          <Skeleton className="h-20 w-full rounded-xl" />
          <Skeleton className="h-20 w-full rounded-xl" />
        </div>
      ) : meetings.length === 0 ? (
        <Card className="p-12 text-center text-slate-500">
          <Video className="w-12 h-12 mx-auto text-slate-400 mb-3" />
          <h3 className="text-sm font-semibold text-slate-800">No meetings recorded</h3>
          <p className="text-xs text-slate-500 mt-1">Click "New Meeting" to ingest notes or upload a transcript.</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {meetings.map((m) => (
            <Link key={m.id} to={`/meetings/${m.id}`}>
              <Card className="p-5 hover:border-slate-400 hover:shadow-sm transition-all h-full flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="text-base font-bold text-slate-900 line-clamp-1">{m.title}</h3>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {m.client_name || 'Client'} • {m.project_name || 'Project'}
                      </p>
                    </div>
                    <Badge variant={m.status === 'reviewed' ? 'success' : m.status === 'processing' ? 'info' : 'amber'}>
                      {m.status.toUpperCase()}
                    </Badge>
                  </div>

                  <div className="flex items-center gap-2 text-xs text-slate-400 pt-1">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{m.meeting_date ? new Date(m.meeting_date).toLocaleString() : 'Date unspecified'}</span>
                    <span>({m.timezone})</span>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1 font-medium">
                      <CheckSquare className="w-3.5 h-3.5 text-slate-400" /> {m.tasks_count || 0} Actions
                    </span>
                    <span className="flex items-center gap-1 font-medium">
                      <Scale className="w-3.5 h-3.5 text-slate-400" /> {m.decisions_count || 0} Decisions
                    </span>
                  </div>
                  <span className="text-brand-900 font-semibold flex items-center gap-0.5">
                    Workspace <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}

      <MeetingWizardModal
        isOpen={wizardOpen}
        onClose={() => setWizardOpen(false)}
        onSuccess={(id) => {
          window.location.href = `/meetings/${id}`;
        }}
      />
    </div>
  );
};

