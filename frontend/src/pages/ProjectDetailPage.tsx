import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Alert } from '../components/ui/Alert';
import { Skeleton } from '../components/ui/Skeleton';
import { api } from '../services/api';
import { Project, Meeting, TimelineItem, ContradictionConflict } from '../types';
import {
  FolderKanban,
  Video,
  Plus,
  Clock,
  AlertTriangle,
  Scale,
  CheckSquare,
  ArrowRight
} from 'lucide-react';
import { MeetingWizardModal } from '../components/meetings/MeetingWizardModal';

export const ProjectDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [conflicts, setConflicts] = useState<ContradictionConflict[]>([]);
  const [loading, setLoading] = useState(true);
  const [wizardOpen, setWizardOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'meetings' | 'timeline' | 'conflicts'>('meetings');

  useEffect(() => {
    if (id) {
      loadProjectData(id);
    }
  }, [id]);

  const loadProjectData = async (projectId: string) => {
    setLoading(true);
    try {
      const [proj, mList, tLine, cList] = await Promise.all([
        api.getProject(projectId),
        api.getMeetings({ project_id: projectId }),
        api.getProjectTimeline(projectId),
        api.getProjectConflicts(projectId),
      ]);
      setProject(proj);
      setMeetings(mList);
      setTimeline(tLine);
      setConflicts(cList);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-44 w-full" />
      </div>
    );
  }

  if (!project) {
    return <Alert type="error">Project not found.</Alert>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900">{project.name}</h1>
            <Badge variant={project.status === 'active' ? 'success' : 'neutral'}>
              {project.status.toUpperCase()}
            </Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Client: <span className="font-semibold text-slate-700">{project.client_name || 'N/A'}</span>
          </p>
        </div>

        <Button variant="primary" size="md" onClick={() => setWizardOpen(true)}>
          <Plus className="w-4 h-4 mr-1.5" />
          Add Meeting
        </Button>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <nav className="flex space-x-6">
          <button
            onClick={() => setActiveTab('meetings')}
            className={`py-3 px-1 border-b-2 text-xs sm:text-sm font-medium transition-colors ${
              activeTab === 'meetings'
                ? 'border-brand-900 text-brand-900 font-semibold'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            Meetings ({meetings.length})
          </button>

          <button
            onClick={() => setActiveTab('timeline')}
            className={`py-3 px-1 border-b-2 text-xs sm:text-sm font-medium transition-colors ${
              activeTab === 'timeline'
                ? 'border-brand-900 text-brand-900 font-semibold'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            Chronological Timeline ({timeline.length})
          </button>

          <button
            onClick={() => setActiveTab('conflicts')}
            className={`py-3 px-1 border-b-2 text-xs sm:text-sm font-medium transition-colors flex items-center gap-1.5 ${
              activeTab === 'conflicts'
                ? 'border-brand-900 text-brand-900 font-semibold'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            Contradiction Detector
            {conflicts.length > 0 && (
              <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
                {conflicts.length}
              </span>
            )}
          </button>
        </nav>
      </div>

      {/* Tab: Meetings */}
      {activeTab === 'meetings' && (
        <div className="space-y-4">
          {meetings.length === 0 ? (
            <Card className="p-12 text-center text-slate-500">
              <Video className="w-12 h-12 mx-auto text-slate-400 mb-3" />
              <h3 className="text-sm font-semibold text-slate-800">No meetings yet</h3>
              <p className="text-xs text-slate-500 mt-1">Create a meeting to ingest notes and extract action items.</p>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {meetings.map((m) => (
                <Link key={m.id} to={`/meetings/${m.id}`}>
                  <Card className="p-4 hover:border-slate-400 transition-all">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <h4 className="text-sm font-bold text-slate-900">{m.title}</h4>
                        <div className="text-xs text-slate-500 flex items-center gap-2">
                          <Clock className="w-3.5 h-3.5" />
                          {m.meeting_date ? new Date(m.meeting_date).toLocaleDateString() : 'Date unspecified'}
                        </div>
                      </div>
                      <Badge variant={m.status === 'reviewed' ? 'success' : 'amber'}>
                        {m.status.toUpperCase()}
                      </Badge>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                      <span>{m.tasks_count || 0} Action Items</span>
                      <span className="text-brand-900 font-semibold flex items-center gap-1">
                        Open Review <ArrowRight className="w-3 h-3" />
                      </span>
                    </div>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab: Timeline */}
      {activeTab === 'timeline' && (
        <div className="relative pl-6 border-l-2 border-slate-200 space-y-6">
          {timeline.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No timeline events recorded.</p>
          ) : (
            timeline.map((item) => (
              <div key={item.id} className="relative">
                {/* Dot */}
                <div className={`absolute -left-[31px] top-1 w-4 h-4 rounded-full border-2 border-white shadow-sm ${
                  item.type === 'meeting' ? 'bg-brand-900' :
                  item.type === 'decision' ? 'bg-accent-500' : 'bg-slate-500'
                }`} />

                <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-900">{item.title}</span>
                      <Badge variant="neutral" size="sm">{item.type.toUpperCase()}</Badge>
                    </div>
                    <span className="text-[11px] text-slate-400">
                      {new Date(item.timestamp).toLocaleString()}
                    </span>
                  </div>
                  {item.details && (
                    <p className="text-xs text-slate-600 leading-relaxed">{item.details}</p>
                  )}
                  {item.meeting_title && (
                    <div className="text-[10px] text-slate-400 pt-1">Source: {item.meeting_title}</div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab: Conflicts */}
      {activeTab === 'conflicts' && (
        <div className="space-y-4">
          <Alert type="info" title="Cross-Meeting Contradiction Detection">
            MeetFlow AI compares statements across all meetings in this project. Conflicting decisions and changed deadlines are flagged for human review rather than silently overwritten.
          </Alert>

          {conflicts.length === 0 ? (
            <Card className="p-8 text-center text-slate-500 text-xs">
              No conflicting commitments or contradictory decisions detected between meetings in this project.
            </Card>
          ) : (
            conflicts.map((conflict) => (
              <Card key={conflict.id} className="p-4 border-l-4 border-l-amber-500 bg-white">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    <span className="text-sm font-bold text-slate-900">{conflict.title}</span>
                    <Badge variant="amber">UNRESOLVED</Badge>
                  </div>

                  <p className="text-xs text-slate-600">{conflict.description}</p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-3 bg-slate-50 rounded-lg text-xs border border-slate-200">
                    <div>
                      <div className="font-semibold text-slate-800">{conflict.first_meeting_title}:</div>
                      <p className="text-slate-600 italic mt-0.5">"{conflict.first_statement}"</p>
                    </div>
                    <div>
                      <div className="font-semibold text-slate-800">{conflict.second_meeting_title}:</div>
                      <p className="text-slate-600 italic mt-0.5">"{conflict.second_statement}"</p>
                    </div>
                  </div>

                  {conflict.suggested_resolution && (
                    <p className="text-[11px] text-amber-900 font-medium">
                      Resolution Guidance: {conflict.suggested_resolution}
                    </p>
                  )}
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {project && (
        <MeetingWizardModal
          isOpen={wizardOpen}
          onClose={() => setWizardOpen(false)}
          onSuccess={() => loadProjectData(project.id)}
        />
      )}
    </div>
  );
};
