import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Alert } from '../ui/Alert';
import { Task } from '../../types';
import { api } from '../../services/api';

interface ConfirmDueDateModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const ConfirmDueDateModal: React.FC<ConfirmDueDateModalProps> = ({
  task,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [dueDate, setDueDate] = useState(task?.due_date || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    if (task) {
      setDueDate(task.due_date || '');
      setError(null);
    }
  }, [task]);

  if (!task) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!dueDate) {
      setError('Please select a valid calendar due date.');
      return;
    }
    setLoading(true);
    setError(null);

    try {
      await api.confirmTaskDueDate(task.id, dueDate);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to confirm deadline.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Confirm Task Due Date"
      description={`Task: "${task.title}"`}
      maxWidth="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <Alert type="error">{error}</Alert>}

        <p className="text-xs text-slate-500">
          Source Date Expression: <span className="font-semibold text-slate-800">{task.date_expression || 'None stated'}</span>
          <br />
          Status: <span className="font-semibold text-amber-600">{task.due_date_status}</span>
        </p>

        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
            Confirmed Calendar Date *
          </label>
          <input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="w-full px-3.5 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-800"
            required
          />
        </div>

        <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
          <Button type="button" variant="outline" size="sm" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" size="sm" isLoading={loading}>
            Save & Confirm Date
          </Button>
        </div>
      </form>
    </Modal>
  );
};
