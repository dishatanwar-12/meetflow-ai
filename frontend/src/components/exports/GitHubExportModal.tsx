import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Alert } from '../ui/Alert';
import { api } from '../../services/api';
import { ExternalLink, CheckCircle, AlertTriangle, ShieldAlert } from 'lucide-react';

interface GitHubExportModalProps {
  meetingId: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const GitHubExportModal: React.FC<GitHubExportModalProps> = ({
  meetingId,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [repository, setRepository] = useState('');
  const [token, setToken] = useState('');
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [executingExport, setExecutingExport] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Preview & Selection states
  const [previewData, setPreviewData] = useState<any | null>(null);
  const [selectedTaskIds, setSelectedTaskIds] = useState<string[]>([]);
  const [allowUnassigned, setAllowUnassigned] = useState(false);
  const [allowUndated, setAllowUndated] = useState(true);
  const [exportResults, setExportResults] = useState<any | null>(null);

  const handleFetchPreview = async () => {
    if (!repository.trim() || !repository.includes('/')) {
      setError("Please provide a valid repository in 'owner/repo' format (e.g., 'acme/client-tracker').");
      return;
    }

    setLoadingPreview(true);
    setError(null);
    setExportResults(null);

    try {
      const data = await api.previewGitHubExport(meetingId, repository.trim());
      setPreviewData(data);
      // Pre-select tasks that are ready
      const readyIds = data.tasks.filter((t: any) => t.is_ready_for_export).map((t: any) => t.task_id);
      setSelectedTaskIds(readyIds);
    } catch (err: any) {
      setError(err.message || 'Failed to generate export preview.');
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleToggleSelect = (taskId: string) => {
    if (selectedTaskIds.includes(taskId)) {
      setSelectedTaskIds(selectedTaskIds.filter((id) => id !== taskId));
    } else {
      setSelectedTaskIds([...selectedTaskIds, taskId]);
    }
  };

  const handleExecuteExport = async () => {
    if (selectedTaskIds.length === 0) {
      setError('Please select at least one task to export.');
      return;
    }

    setExecutingExport(true);
    setError(null);

    try {
      const res = await api.executeGitHubExport(meetingId, {
        repository: repository.trim(),
        personal_access_token: token.trim() || undefined,
        task_ids: selectedTaskIds,
        allow_unassigned_export: allowUnassigned,
        allow_undated_export: allowUndated,
      });

      setExportResults(res);
      onSuccess();
    } catch (err: any) {
      setError(err.message || 'Failed to export issues to GitHub.');
    } finally {
      setExecutingExport(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Export to GitHub Issues"
      description="Preview tasks, resolve uncertainties, and create traceable GitHub issues."
      maxWidth="2xl"
    >
      <div className="space-y-5">
        {error && <Alert type="error">{error}</Alert>}

        {/* Step 1: Repo & Token Input */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="GitHub Repository (owner/repo) *"
            placeholder="e.g. acme-corp/web-app"
            value={repository}
            onChange={(e) => setRepository(e.target.value)}
          />

          <Input
            label="Personal Access Token (PAT)"
            type="password"
            placeholder="ghp_... (or leave empty if configured)"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            helperText="Token requires 'repo' or 'public_repo' scope."
          />
        </div>

        <Button
          type="button"
          size="sm"
          variant="outline"
          onClick={handleFetchPreview}
          isLoading={loadingPreview}
        >
          Inspect & Preview Tasks
        </Button>

        {/* Step 2: Task Preview List */}
        {previewData && (
          <div className="space-y-4 pt-3 border-t border-slate-100">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-700">
                Found {previewData.total_tasks} tasks: {previewData.ready_tasks} ready, {previewData.unresolved_tasks} requiring confirmation.
              </span>
              <button
                onClick={() => setSelectedTaskIds(previewData.tasks.map((t: any) => t.task_id))}
                className="text-brand-900 font-semibold underline"
              >
                Select All
              </button>
            </div>

            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
              {previewData.tasks.map((task: any) => {
                const isSelected = selectedTaskIds.includes(task.task_id);
                return (
                  <div
                    key={task.task_id}
                    onClick={() => handleToggleSelect(task.task_id)}
                    className={`p-3 rounded-xl border text-xs cursor-pointer transition-all flex items-start gap-3 ${
                      isSelected ? 'border-brand-800 bg-brand-50/40' : 'border-slate-200 bg-white'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => {}}
                      className="mt-0.5 rounded text-brand-900 focus:ring-brand-800"
                    />

                    <div className="flex-1 space-y-1 min-w-0">
                      <div className="font-semibold text-slate-900 truncate">{task.title}</div>
                      <div className="text-[11px] text-slate-500">
                        Owner: <span className="font-medium text-slate-800">{task.owner}</span> | Due: <span className="font-medium text-slate-800">{task.due_date}</span>
                      </div>
                      {!task.is_ready_for_export && (
                        <div className="flex items-center gap-1 text-[11px] text-amber-700">
                          <AlertTriangle className="w-3 h-3 text-amber-600" />
                          <span>Unresolved: {task.missing_fields.join(', ')}</span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Overrides */}
            <div className="space-y-2 p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={allowUnassigned}
                  onChange={(e) => setAllowUnassigned(e.target.checked)}
                  className="rounded text-brand-900"
                />
                <span className="font-medium text-slate-700">
                  Allow exporting unassigned tasks (explicit approval to export without a confirmed owner)
                </span>
              </label>
            </div>

            <Button
              type="button"
              variant="teal"
              size="md"
              className="w-full"
              isLoading={executingExport}
              onClick={handleExecuteExport}
            >
              Export {selectedTaskIds.length} Selected Tasks to GitHub
            </Button>
          </div>
        )}

        {/* Step 3: Export Results */}
        {exportResults && (
          <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-3">
            <div className="flex items-center gap-2 text-emerald-900 font-bold text-sm">
              <CheckCircle className="w-5 h-5 text-emerald-600" />
              <span>Export Complete: {exportResults.total_created} issues created.</span>
            </div>

            <div className="space-y-1.5 max-h-40 overflow-y-auto">
              {exportResults.results.map((r: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between text-xs py-1 border-b border-emerald-100 last:border-0">
                  <span className="text-emerald-950 font-medium">Issue #{r.issue_number}</span>
                  {r.issue_url && (
                    <a
                      href={r.issue_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-emerald-800 font-bold underline flex items-center gap-1 hover:text-emerald-950"
                    >
                      Open in GitHub <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                  {r.error && <span className="text-rose-600">{r.error}</span>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};

