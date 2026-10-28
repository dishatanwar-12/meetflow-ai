import React from 'react';
import { Task, TaskStatus } from '../../types';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { UncertaintyBadge } from '../common/UncertaintyBadge';
import { AlertCircle, Clock } from 'lucide-react';

interface TaskKanbanProps {
  tasks: Task[];
  onSelectTask: (task: Task) => void;
  onStatusChange: (taskId: string, newStatus: TaskStatus) => void;
}

const COLUMNS: Array<{ status: TaskStatus; label: string; color: string }> = [
  { status: 'needs_clarification', label: 'Needs Clarification', color: 'border-t-amber-500' },
  { status: 'ready', label: 'Ready', color: 'border-t-brand-700' },
  { status: 'in_progress', label: 'In Progress', color: 'border-t-sky-500' },
  { status: 'blocked', label: 'Blocked', color: 'border-t-rose-500' },
  { status: 'completed', label: 'Completed', color: 'border-t-emerald-500' },
];

export const TaskKanban: React.FC<TaskKanbanProps> = ({
  tasks,
  onSelectTask,
  onStatusChange,
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-4 overflow-x-auto pb-4">
      {COLUMNS.map((col) => {
        const colTasks = tasks.filter((t) => t.status === col.status);
        return (
          <div key={col.status} className="flex flex-col bg-slate-50/70 rounded-xl p-3 border border-slate-200 min-w-[260px]">
            {/* Column Header */}
            <div className={`border-t-4 ${col.color} pt-2 pb-3 px-1 flex items-center justify-between`}>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700">{col.label}</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-200 text-slate-700">
                {colTasks.length}
              </span>
            </div>

            {/* Task Cards */}
            <div className="space-y-2.5 flex-1 overflow-y-auto max-h-[70vh] pr-1">
              {colTasks.map((task) => (
                <div
                  key={task.id}
                  onClick={() => onSelectTask(task)}
                  className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm hover:shadow transition-all cursor-pointer space-y-2"
                >
                  <div className="text-xs font-semibold text-slate-900 leading-snug line-clamp-2">
                    {task.title}
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-500">
                    <span className="truncate max-w-[120px]">{task.project_name || 'Project'}</span>
                    <Badge variant="neutral" size="sm">{task.priority}</Badge>
                  </div>

                  {/* Owner & Due Date Uncertainty */}
                  <div className="pt-1 border-t border-slate-100 space-y-1 text-[11px]">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Owner:</span>
                      <span className="font-semibold text-slate-800 truncate max-w-[100px]">{task.owner_name || 'Unassigned'}</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Due:</span>
                      <span className={`font-semibold ${task.is_overdue ? 'text-rose-600 font-bold' : 'text-slate-800'}`}>
                        {task.due_date || task.date_expression || 'None'}
                      </span>
                    </div>
                  </div>

                  {task.confirmation_required && (
                    <div className="text-[10px] text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200/60 font-semibold">
                      Review Needed
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};
