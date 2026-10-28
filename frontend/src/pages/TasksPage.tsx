import React, { useEffect, useState } from 'react';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Skeleton } from '../components/ui/Skeleton';
import { api } from '../services/api';
import { Task, TaskStatus, TaskPriority } from '../types';
import { TaskTable } from '../components/tasks/TaskTable';
import { TaskKanban } from '../components/tasks/TaskKanban';
import { TaskDetailModal } from '../components/tasks/TaskDetailModal';
import { ConfirmOwnerModal } from '../components/tasks/ConfirmOwnerModal';
import { ConfirmDueDateModal } from '../components/tasks/ConfirmDueDateModal';
import { LayoutList, Columns3, Search, Filter, AlertTriangle, ShieldAlert } from 'lucide-react';

export const TasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'table' | 'kanban'>('table');

  // Filter states
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [needsConfirmationOnly, setNeedsConfirmationOnly] = useState(false);
  const [overdueOnly, setOverdueOnly] = useState(false);

  // Modal states
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [ownerModalOpen, setOwnerModalOpen] = useState(false);
  const [dueDateModalOpen, setDueDateModalOpen] = useState(false);

  useEffect(() => {
    loadTasks();
  }, [search, statusFilter, priorityFilter, needsConfirmationOnly, overdueOnly]);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const data = await api.getTasks({
        search: search || undefined,
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
        needs_confirmation: needsConfirmationOnly ? true : undefined,
        overdue_only: overdueOnly ? true : undefined,
      });
      setTasks(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (taskId: string, newStatus: TaskStatus) => {
    try {
      await api.updateTask(taskId, { status: newStatus });
      loadTasks();
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Task Management Board</h1>
          <p className="text-xs text-slate-500 mt-1">
            Track commitments, verify owners and dates, and monitor progress across all meetings.
          </p>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200">
          <button
            onClick={() => setViewMode('table')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 transition-colors ${
              viewMode === 'table' ? 'bg-white text-brand-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <LayoutList className="w-3.5 h-3.5" /> Table
          </button>
          <button
            onClick={() => setViewMode('kanban')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 transition-colors ${
              viewMode === 'kanban' ? 'bg-white text-brand-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Columns3 className="w-3.5 h-3.5" /> Kanban
          </button>
        </div>
      </div>

      {/* Filter Row */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="w-4 h-4 absolute left-3.5 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search tasks..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-brand-800 bg-white"
          />
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 text-xs border border-slate-300 rounded-lg bg-white text-slate-700"
        >
          <option value="">All Statuses</option>
          <option value="needs_clarification">Needs Clarification</option>
          <option value="ready">Ready</option>
          <option value="in_progress">In Progress</option>
          <option value="blocked">Blocked</option>
          <option value="completed">Completed</option>
        </select>

        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          className="px-3 py-2 text-xs border border-slate-300 rounded-lg bg-white text-slate-700"
        >
          <option value="">All Priorities</option>
          <option value="urgent">Urgent</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        {/* Needs confirmation toggle button */}
        <button
          onClick={() => setNeedsConfirmationOnly(!needsConfirmationOnly)}
          className={`px-3 py-2 rounded-lg text-xs font-semibold border flex items-center gap-1.5 transition-colors ${
            needsConfirmationOnly
              ? 'bg-amber-50 border-amber-300 text-amber-900'
              : 'bg-white border-slate-300 text-slate-600 hover:bg-slate-50'
          }`}
        >
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
          Needs Confirmation
        </button>

        {/* Overdue only toggle button */}
        <button
          onClick={() => setOverdueOnly(!overdueOnly)}
          className={`px-3 py-2 rounded-lg text-xs font-semibold border flex items-center gap-1.5 transition-colors ${
            overdueOnly
              ? 'bg-rose-50 border-rose-300 text-rose-900'
              : 'bg-white border-slate-300 text-slate-600 hover:bg-slate-50'
          }`}
        >
          <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
          Overdue Only
        </button>
      </div>

      {/* Task Content */}
      {loading ? (
        <div className="space-y-3">
          <Skeleton className="h-16 w-full rounded-xl" />
          <Skeleton className="h-16 w-full rounded-xl" />
          <Skeleton className="h-16 w-full rounded-xl" />
        </div>
      ) : viewMode === 'table' ? (
        <TaskTable
          tasks={tasks}
          onSelectTask={(t) => {
            setSelectedTask(t);
            setDetailModalOpen(true);
          }}
          onConfirmOwner={(t) => {
            setSelectedTask(t);
            setOwnerModalOpen(true);
          }}
          onConfirmDueDate={(t) => {
            setSelectedTask(t);
            setDueDateModalOpen(true);
          }}
        />
      ) : (
        <TaskKanban
          tasks={tasks}
          onSelectTask={(t) => {
            setSelectedTask(t);
            setDetailModalOpen(true);
          }}
          onStatusChange={handleStatusChange}
        />
      )}

      {/* Modals */}
      <TaskDetailModal
        task={selectedTask}
        isOpen={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        onUpdate={loadTasks}
      />

      <ConfirmOwnerModal
        task={selectedTask}
        isOpen={ownerModalOpen}
        onClose={() => setOwnerModalOpen(false)}
        onSuccess={loadTasks}
      />

      <ConfirmDueDateModal
        task={selectedTask}
        isOpen={dueDateModalOpen}
        onClose={() => setDueDateModalOpen(false)}
        onSuccess={loadTasks}
      />
    </div>
  );
};
