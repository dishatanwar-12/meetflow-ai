import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import { Alert } from '../components/ui/Alert';
import { Skeleton } from '../components/ui/Skeleton';
import { api } from '../services/api';
import { Project, Client, ProjectStatus } from '../types';
import { FolderKanban, Plus, Search, Video, CheckSquare, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const ProjectsPage: React.FC = () => {
  const { isPM } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [modalOpen, setModalOpen] = useState(false);

  // Form
  const [name, setName] = useState('');
  const [clientId, setClientId] = useState('');
  const [description, setDescription] = useState('');
  const [goals, setGoals] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [search, statusFilter]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [projList, clientList] = await Promise.all([
        api.getProjects({
          search: search || undefined,
          status: statusFilter || undefined,
        }),
        api.getClients(),
      ]);
      setProjects(projList);
      setClients(clientList);
      if (clientList.length > 0 && !clientId) {
        setClientId(clientList[0].id);
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !clientId) return;

    setSubmitting(true);
    setError(null);
    try {
      await api.createProject({
        name: name.trim(),
        client_id: clientId,
        description: description.trim() || undefined,
        goals: goals.trim() || undefined,
        status: 'active' as ProjectStatus,
      });
      setModalOpen(false);
      setName('');
      setDescription('');
      setGoals('');
      loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to create project.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Projects</h1>
          <p className="text-xs text-slate-500 mt-1">Organize meetings, outcomes, and cross-meeting action items.</p>
        </div>
        {isPM && (
          <Button variant="primary" size="md" onClick={() => setModalOpen(true)}>
            <Plus className="w-4 h-4 mr-1.5" />
            Add Project
          </Button>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search projects..."
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
          <option value="active">Active</option>
          <option value="on_hold">On Hold</option>
          <option value="completed">Completed</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      {/* Projects Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Skeleton className="h-44 rounded-xl" />
          <Skeleton className="h-44 rounded-xl" />
          <Skeleton className="h-44 rounded-xl" />
        </div>
      ) : projects.length === 0 ? (
        <Card className="p-12 text-center text-slate-500">
          <FolderKanban className="w-12 h-12 mx-auto text-slate-400 mb-3" />
          <h3 className="text-sm font-semibold text-slate-800">No projects found</h3>
          <p className="text-xs text-slate-500 mt-1">Create a project to connect client meetings and tasks.</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {projects.map((p) => (
            <Link
              key={p.id}
              to={`/projects/${p.id}`}
              className="group block"
            >
              <Card className="p-5 h-full flex flex-col justify-between hover:border-slate-400 hover:shadow-md transition-all">
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-base font-bold text-slate-900 group-hover:text-brand-900 transition-colors">
                        {p.name}
                      </h3>
                      <p className="text-xs text-slate-500 mt-0.5">Client: {p.client_name || 'N/A'}</p>
                    </div>
                    <Badge variant={p.status === 'active' ? 'success' : 'neutral'}>
                      {p.status.toUpperCase()}
                    </Badge>
                  </div>

                  {p.description && (
                    <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                      {p.description}
                    </p>
                  )}
                </div>

                <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1 font-medium">
                      <Video className="w-3.5 h-3.5 text-slate-400" /> {p.meetings_count || 0}
                    </span>
                    <span className="flex items-center gap-1 font-medium">
                      <CheckSquare className="w-3.5 h-3.5 text-slate-400" /> {p.tasks_count || 0}
                    </span>
                  </div>
                  <span className="text-brand-900 font-semibold group-hover:underline flex items-center gap-0.5">
                    View <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {/* Create Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Create New Project"
        description="Initialize a project workspace for meetings and deliverables."
        maxWidth="md"
      >
        <form onSubmit={handleCreate} className="space-y-4">
          {error && <Alert type="error">{error}</Alert>}
          <Input label="Project Name *" value={name} onChange={(e) => setName(e.target.value)} required />
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Client *</label>
            <select
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
              className="w-full px-3.5 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg focus:ring-1 focus:ring-brand-800"
              required
            >
              <option value="" disabled>Select a client</option>
              {clients.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Description</label>
            <textarea
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3.5 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-brand-800"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Goals</label>
            <textarea
              rows={2}
              value={goals}
              onChange={(e) => setGoals(e.target.value)}
              className="w-full px-3.5 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-brand-800"
            />
          </div>
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <Button type="button" variant="outline" size="sm" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={submitting}>
              Create Project
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
