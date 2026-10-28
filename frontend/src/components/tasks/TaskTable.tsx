import React from 'react';
import { Task } from '../../types';
import { Badge } from '../ui/Badge';
import { UncertaintyBadge } from '../common/UncertaintyBadge';
import { Clock, AlertCircle } from 'lucide-react';

interface TaskTableProps {
  tasks: Task[];
  onSelectTask: (task: Task) => void;
  onConfirmOwner: (task: Task) => void;
  onConfirmDueDate: (task: Task) => void;
}

export const TaskTable: React.FC<TaskTableProps> = ({
  tasks,
  onSelectTask,
  onConfirmOwner,
  onConfirmDueDate,
}) => {
  if (tasks.length === 0) {
    return (
      <div className="p-12 text-center text-slate-500 bg-white rounded-xl border border-slate-200">
        <p className="text-sm font-medium">No tasks found matching current filters.</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              <th className="py-3 px-4">Task</th>
              <th className="py-3 px-4">Owner & Certainty</th>
              <th className="py-3 px-4">Due Date</th>
              <th className="py-3 px-4">Priority</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-xs text-slate-800">
            {tasks.map((task) => (
              <tr
                key={task.id}
                className="hover:bg-slate-50/70 transition-colors cursor-pointer"
                onClick={() => onSelectTask(task)}
              >
                {/* Title & Project */}
                <td className="py-3 px-4 font-medium max-w-xs">
                  <div className="font-semibold text-slate-900 truncate">{task.title}</div>
                  <div className="text-[11px] text-slate-500 truncate">
                    {task.project_name || 'Project'} • {task.meeting_title || 'Meeting'}
                  </div>
                </td>

                {/* Owner & Uncertainty Badge */}
                <td className="py-3 px-4" onClick={(e) => e.stopPropagation()}>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-slate-800">{task.owner_name || 'Unassigned'}</span>
                    <UncertaintyBadge type="owner" status={task.owner_status} />
                  </div>
                  {task.owner_status !== 'user_confirmed' && (
                    <button
                      onClick={() => onConfirmOwner(task)}
                      className="text-[10px] text-brand-900 font-semibold underline hover:text-brand-700 mt-0.5 block"
                    >
                      Confirm Owner
                    </button>
                  )}
                </td>

                {/* Due Date & Overdue flag */}
                <td className="py-3 px-4" onClick={(e) => e.stopPropagation()}>
                  <div className="flex items-center gap-1.5">
                    <span className={`font-medium ${task.is_overdue ? 'text-rose-600 font-bold' : 'text-slate-800'}`}>
                      {task.due_date || task.date_expression || 'None'}
                    </span>
                    <UncertaintyBadge type="due_date" status={task.due_date_status} dateExpression={task.date_expression} />
                  </div>
                  {task.is_overdue && (
                    <span className="text-[10px] text-rose-600 font-bold flex items-center gap-1 mt-0.5">
                      <AlertCircle className="w-3 h-3" /> Overdue
                    </span>
                  )}
                  {task.due_date_status !== 'user_confirmed' && (
                    <button
                      onClick={() => onConfirmDueDate(task)}
                      className="text-[10px] text-brand-900 font-semibold underline hover:text-brand-700 mt-0.5 block"
                    >
                      Confirm Date
                    </button>
                  )}
                </td>

                {/* Priority */}
                <td className="py-3 px-4">
                  <Badge variant="neutral">{task.priority.toUpperCase()}</Badge>
                </td>

                {/* Status */}
                <td className="py-3 px-4">
                  <Badge
                    variant={
                      task.status === 'completed' ? 'success' :
                      task.status === 'in_progress' ? 'info' :
                      task.status === 'needs_clarification' ? 'amber' : 'neutral'
                    }
                  >
                    {task.status.replace('_', ' ')}
                  </Badge>
                </td>

                {/* Actions */}
                <td className="py-3 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                  <button
                    onClick={() => onSelectTask(task)}
                    className="text-xs font-semibold text-brand-900 hover:text-brand-700 underline"
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
