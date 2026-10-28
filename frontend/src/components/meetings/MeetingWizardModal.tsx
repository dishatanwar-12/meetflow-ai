import React, { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Alert } from '../ui/Alert';
import { api } from '../../services/api';
import { Client, Project } from '../../types';
import { Upload, Plus, Trash2, FileText, CheckCircle2 } from 'lucide-react';

interface MeetingWizardModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (meetingId: string) => void;
}

export const MeetingWizardModal: React.FC<MeetingWizardModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [clients, setClients] = useState<Client[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [title, setTitle] = useState('');
  const [clientId, setClientId] = useState('');
  const [projectId, setProjectId] = useState('');
  const [meetingDate, setMeetingDate] = useState('');
  const [timezone, setTimezone] = useState(Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC');
  const [meetingType, setMeetingType] = useState('status_update');
  const [rawTranscript, setRawTranscript] = useState('');
  const [attendees, setAttendees] = useState<Array<{ name: string; email: string; role: string; speaker_label: string }>>([
    { name: '', email: '', role: '', speaker_label: '' }
  ]);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadInitialData();
    }
  }, [isOpen]);

  const loadInitialData = async () => {
    try {
      const clientList = await api.getClients();
      setClients(clientList);
      if (clientList.length > 0) {
        setClientId(clientList[0].id);
        const projList = await api.getProjects({ client_id: clientList[0].id });
        setProjects(projList);
        if (projList.length > 0) {
          setProjectId(projList[0].id);
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load clients and projects.');
    }
  };

  const handleClientChange = async (newClientId: string) => {
    setClientId(newClientId);
    try {
      const projList = await api.getProjects({ client_id: newClientId });
      setProjects(projList);
      if (projList.length > 0) {
        setProjectId(projList[0].id);
      } else {
        setProjectId('');
      }
    } catch {
      setProjects([]);
      setProjectId('');
    }
  };

  const addAttendee = () => {
    setAttendees([...attendees, { name: '', email: '', role: '', speaker_label: '' }]);
  };

  const removeAttendee = (index: number) => {
    setAttendees(attendees.filter((_, i) => i !== index));
  };

  const updateAttendee = (index: number, field: string, value: string) => {
    const updated = [...attendees];
    updated[index] = { ...updated[index], [field]: value };
    setAttendees(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !clientId || !projectId) {
      setError('Please provide a meeting title, client, and project.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const validAttendees = attendees
        .filter((a) => a.name.trim().length > 0)
        .map((a) => ({
          name: a.name.trim(),
          email: a.email.trim() || undefined,
          role: a.role.trim() || undefined,
          speaker_label: a.speaker_label.trim() || undefined,
        }));

      const meeting = await api.createMeeting({
        title: title.trim(),
        client_id: clientId,
        project_id: projectId,
        meeting_date: meetingDate ? new Date(meetingDate).toISOString() : undefined,
        timezone,
        meeting_type: meetingType,
        raw_transcript: rawTranscript.trim() || undefined,
        attendees: validAttendees,
      });

      // If a file was selected, upload it immediately
      if (uploadedFile) {
        await api.uploadMeetingTranscript(meeting.id, uploadedFile);
      }

      onSuccess(meeting.id);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to create meeting.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create New Meeting"
      description="Ingest notes or upload a transcript to convert discussion into structured actions."
      maxWidth="2xl"
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        {error && <Alert type="error">{error}</Alert>}

        {/* Title */}
        <Input
          label="Meeting Title *"
          placeholder="e.g. Q4 Platform Architecture Review"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />

        {/* Client & Project Selectors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Client *</label>
            <select
              value={clientId}
              onChange={(e) => handleClientChange(e.target.value)}
              className="w-full px-3.5 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-800"
              required
            >
              <option value="" disabled>Select a client</option>
              {clients.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Project *</label>
            <select
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
              className="w-full px-3.5 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-800"
              required
            >
              <option value="" disabled>Select a project</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Date, Timezone & Meeting Type */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Date & Time</label>
            <input
              type="datetime-local"
              value={meetingDate}
              onChange={(e) => setMeetingDate(e.target.value)}
              className="w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-800"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Timezone</label>
            <input
              type="text"
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
              className="w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-800"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Meeting Type</label>
            <select
              value={meetingType}
              onChange={(e) => setMeetingType(e.target.value)}
              className="w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-800"
            >
              <option value="status_update">Status Update</option>
              <option value="discovery">Discovery</option>
              <option value="client_review">Client Review</option>
              <option value="planning">Planning</option>
              <option value="retrospective">Retrospective</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>

        {/* Attendees Section */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
              Attendees (Assists in Identity Resolution)
            </label>
            <button
              type="button"
              onClick={addAttendee}
              className="text-xs text-brand-900 font-semibold hover:text-brand-700 flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" /> Add Attendee
            </button>
          </div>

          <div className="space-y-2 max-h-36 overflow-y-auto pr-1">
            {attendees.map((att, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <input
                  type="text"
                  placeholder="Full Name (e.g. Priya Sharma)"
                  value={att.name}
                  onChange={(e) => updateAttendee(idx, 'name', e.target.value)}
                  className="flex-1 px-3 py-1.5 text-xs border border-slate-300 rounded-md focus:ring-1 focus:ring-brand-800"
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={att.email}
                  onChange={(e) => updateAttendee(idx, 'email', e.target.value)}
                  className="flex-1 px-3 py-1.5 text-xs border border-slate-300 rounded-md focus:ring-1 focus:ring-brand-800"
                />
                <input
                  type="text"
                  placeholder="Speaker label (e.g. Priya)"
                  value={att.speaker_label}
                  onChange={(e) => updateAttendee(idx, 'speaker_label', e.target.value)}
                  className="w-32 px-3 py-1.5 text-xs border border-slate-300 rounded-md focus:ring-1 focus:ring-brand-800"
                />
                {attendees.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeAttendee(idx)}
                    className="p-1.5 text-slate-400 hover:text-rose-600 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Transcript Upload / Paste */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
            Meeting Notes or Transcript
          </label>
          <textarea
            rows={5}
            value={rawTranscript}
            onChange={(e) => setRawTranscript(e.target.value)}
            placeholder="Paste transcript or rough meeting notes here... e.g.:&#10;Priya: I will review the API specifications by Friday.&#10;Alex: We should try to update the dashboard next week."
            className="w-full px-3.5 py-2.5 text-xs font-mono text-slate-800 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-800 font-normal leading-relaxed"
          />
        </div>

        {/* File Upload Attachment */}
        <div className="border border-dashed border-slate-300 rounded-xl p-4 bg-slate-50/50 flex flex-col items-center justify-center text-center">
          <input
            type="file"
            id="file-upload"
            accept=".txt,.pdf,.docx"
            className="hidden"
            onChange={(e) => setUploadedFile(e.target.files?.[0] || null)}
          />
          <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
            {uploadedFile ? (
              <div className="flex items-center gap-2 text-emerald-800 text-xs font-medium">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                <span>{uploadedFile.name} ({(uploadedFile.size / 1024).toFixed(1)} KB)</span>
              </div>
            ) : (
              <>
                <Upload className="w-6 h-6 text-slate-400 mb-1" />
                <span className="text-xs font-medium text-brand-900">Upload document (TXT, PDF, DOCX)</span>
                <span className="text-[10px] text-slate-400 mt-0.5">Maximum file size: 15 MB</span>
              </>
            )}
          </label>
        </div>

        {/* Footer buttons */}
        <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
          <Button type="button" variant="outline" size="sm" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" size="sm" isLoading={loading}>
            Create Meeting & Save Notes
          </Button>
        </div>
      </form>
    </Modal>
  );
};
