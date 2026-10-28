import React, { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { UncertaintyBadge } from '../common/UncertaintyBadge';
import { Task, TaskComment, TaskStatus } from '../../types';
import { api } from '../../services/api';
import { MessageSquare, Quote, Clock, CheckCircle2, User, Send, ExternalLink } from 'lucide-react';

interface TaskDetailModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
}

export const TaskDetailModal: React.FC<TaskDetailModalProps> = ({
  task,
  isOpen,
  onClose,
  onUpdate,
}) => {
  const [comments, setComments] = useState<TaskComment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loadingComments, setLoadingComments] = useState(false);
  const [submittingComment, setSubmittingComment] = useState(false);
  const [statusUpdating, setStatusUpdating] = useState(false);

  useEffect(() => {
    if (task && isOpen) {
      loadComments(task.id);
    }
  }, [task, isOpen]);

  const loadComments = async (taskId: string) => {
    setLoadingComments(true);
    try {
      const data = await api.getTaskComments(taskId);
      setComments(data);
    } catch {
      // ignore
    } finally {
      setLoadingComments(false);
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task || !newComment.trim()) return;

    setSubmittingComment(true);
    try {
      await api.addTaskComment(task.id, newComment.trim());
      setNewComment('');
      loadComments(task.id);
      onUpdate();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleStatusChange = async (newStatus: TaskStatus) => {
    if (!task) return;
    setStatusUpdating(true);
    try {
      await api.updateTask(task.id, { status: newStatus });
      onUpdate();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setStatusUpdating(false);
    }
  };

  if (!task) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={task.title}
      description={`Task ID: ${task.id.slice(0, 8)} | Project: ${task.project_name || 'N/A'}`}
      maxWidth="2xl"
    >
      <div className="space-y-6">
        {/* Status & Priority Row */}
        <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-slate-50 border border-slate-200 rounded-xl">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500 uppercase">Status:</span>
            <select
              value={task.status}
              disabled={statusUpdating}
              onChange={(e) => handleStatusChange(e.target.value as TaskStatus)}
              className="text-xs font-semibold px-2.5 py-1 rounded-md border border-slate-300 bg-white focus:ring-1 focus:ring-brand-800"
            >
              <option value="needs_clarification">Needs Clarification</option>
              <option value="ready">Ready</option>
              <option value="in_progress">In Progress</option>
              <option value="blocked">Blocked</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500 uppercase">Priority:</span>
            <Badge variant="neutral">{task.priority.toUpperCase()}</Badge>
          </div>
        </div>

        {/* Description */}
        {task.description && (
          <div>
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Description</h4>
            <p className="text-sm text-slate-700 leading-relaxed bg-white p-3 rounded-lg border border-slate-100">
              {task.description}
            </p>
          </div>
        )}

        {/* Owner & Deadline Uncertainty breakdown */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-3 border border-slate-200 rounded-xl bg-white space-y-1">
            <div className="text-xs font-semibold text-slate-500 uppercase">Owner Commitment</div>
            <div className="text-sm font-bold text-slate-900">{task.owner_name || 'Unassigned'}</div>
            <div className="pt-1">
              <UncertaintyBadge type="owner" status={task.owner_status} />
            </div>
          </div>

          <div className="p-3 border border-slate-200 rounded-xl bg-white space-y-1">
            <div className="text-xs font-semibold text-slate-500 uppercase">Due Date Commitment</div>
            <div className="text-sm font-bold text-slate-900">{task.due_date || task.date_expression || 'None specified'}</div>
            <div className="pt-1">
              <UncertaintyBadge type="due_date" status={task.due_date_status} dateExpression={task.date_expression} />
            </div>
          </div>
        </div>

        {/* Source Evidence & Offsets */}
        {task.evidence_passage && (
          <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-600">
              <span className="flex items-center gap-1.5">
                <Quote className="w-3.5 h-3.5 text-slate-400" />
                Supporting Transcript Evidence
              </span>
              {task.source_start !== null && task.source_end !== null && (
                <span className="text-[10px] text-slate-400 font-mono">
                  Offset: {task.source_start}–{task.source_end}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-700 italic">"{task.evidence_passage}"</p>
          </div>
        )}

        {/* External Sync URL */}
        {task.external_sync_url && (
          <div className="flex items-center gap-2 p-3 bg-brand-50 border border-brand-200 rounded-xl text-xs text-brand-900">
            <span>Synced to External Tracker:</span>
            <a
              href={task.external_sync_url}
              target="_blank"
              rel="noreferrer"
              className="font-bold underline flex items-center gap-1 hover:text-brand-700"
            >
              View Issue <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        )}

        {/* Activity & Comment Thread */}
        <div className="space-y-3 pt-2 border-t border-slate-100">
          <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <MessageSquare className="w-3.5 h-3.5" />
            Activity & Comments ({comments.length})
          </h4>

          <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
            {loadingComments ? (
              <p className="text-xs text-slate-400 italic">Loading activity...</p>
            ) : comments.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No comments yet.</p>
            ) : (
              comments.map((c) => (
                <div key={c.id} className="p-2.5 bg-slate-50 border border-slate-200/80 rounded-lg text-xs space-y-1">
                  <div className="flex items-center justify-between text-slate-500 text-[11px]">
                    <span className="font-semibold text-slate-800">{c.user_name || 'Team member'}</span>
                    <span>{new Date(c.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-slate-700">{c.content}</p>
                </div>
              ))
            )}
          </div>

          <form onSubmit={handleAddComment} className="flex gap-2 pt-2">
            <input
              type="text"
              placeholder="Add activity note or comment..."
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              className="flex-1 px-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-brand-800"
            />
            <Button size="sm" variant="primary" type="submit" isLoading={submittingComment}>
              <Send className="w-3.5 h-3.5" />
            </Button>
          </form>
        </div>
      </div>
    </Modal>
  );
};
