import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Alert } from '../ui/Alert';
import { Task } from '../../types';
import { api } from '../../services/api';

interface ConfirmOwnerModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const ConfirmOwnerModal: React.FC<ConfirmOwnerModalProps> = ({
  task,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [ownerName, setOwnerName] = useState(task?.owner_name || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    if (task) {
      setOwnerName(task.owner_name || '');
      setError(null);
    }
  }, [task]);

  if (!task) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ownerName.trim()) {
      setError('Please provide a valid owner name.');
      return;
    }
    setLoading(true);
    setError(null);

    try {
      await api.confirmTaskOwner(task.id, ownerName.trim());
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to confirm owner.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Confirm Task Owner"
      description={`Task: "${task.title}"`}
      maxWidth="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <Alert type="error">{error}</Alert>}

        <p className="text-xs text-slate-500">
          Original Extracted Owner: <span className="font-semibold text-slate-800">{task.owner_name || 'None stated'}</span>
          <br />
          Status: <span className="font-semibold text-amber-600">{task.owner_status}</span>
        </p>

        <Input
          label="Confirmed Owner Name *"
          value={ownerName}
          onChange={(e) => setOwnerName(e.target.value)}
          placeholder="e.g. Priya Sharma"
          required
        />

        <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
          <Button type="button" variant="outline" size="sm" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" size="sm" isLoading={loading}>
            Save & Confirm Owner
          </Button>
        </div>
      </form>
    </Modal>
  );
};

