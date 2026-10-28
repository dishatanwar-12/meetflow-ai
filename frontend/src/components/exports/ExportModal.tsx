import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { api } from '../../services/api';
import { FileSpreadsheet, FileCode, FileText, File, Download } from 'lucide-react';

interface ExportModalProps {
  meetingId: string;
  isOpen: boolean;
  onClose: () => void;
  onOpenGitHubExport: () => void;
}

export const ExportModal: React.FC<ExportModalProps> = ({
  meetingId,
  isOpen,
  onClose,
  onOpenGitHubExport,
}) => {
  const downloadFile = (type: 'csv' | 'json' | 'markdown' | 'pdf') => {
    const url = api.getDownloadUrl(type, meetingId);
    window.open(url, '_blank');
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Export Meeting Outcomes"
      description="Download structured outcomes or export directly to an external task tracker."
      maxWidth="md"
    >
      <div className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {/* CSV */}
          <button
            onClick={() => downloadFile('csv')}
            className="flex items-center gap-3 p-3.5 rounded-xl border border-slate-200 hover:border-brand-800 hover:bg-slate-50 transition-all text-left"
          >
            <div className="p-2.5 bg-emerald-50 text-emerald-700 rounded-lg">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-slate-900">CSV Spreadsheet</div>
              <div className="text-[10px] text-slate-500">Formula-injection safe</div>
            </div>
          </button>

          {/* JSON */}
          <button
            onClick={() => downloadFile('json')}
            className="flex items-center gap-3 p-3.5 rounded-xl border border-slate-200 hover:border-brand-800 hover:bg-slate-50 transition-all text-left"
          >
            <div className="p-2.5 bg-sky-50 text-sky-700 rounded-lg">
              <FileCode className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-slate-900">Structured JSON</div>
              <div className="text-[10px] text-slate-500">Version 1.0 schema</div>
            </div>
          </button>

          {/* Markdown */}
          <button
            onClick={() => downloadFile('markdown')}
            className="flex items-center gap-3 p-3.5 rounded-xl border border-slate-200 hover:border-brand-800 hover:bg-slate-50 transition-all text-left"
          >
            <div className="p-2.5 bg-slate-100 text-slate-700 rounded-lg">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-slate-900">Markdown Brief</div>
              <div className="text-[10px] text-slate-500">Executive summary</div>
            </div>
          </button>

          {/* PDF */}
          <button
            onClick={() => downloadFile('pdf')}
            className="flex items-center gap-3 p-3.5 rounded-xl border border-slate-200 hover:border-brand-800 hover:bg-slate-50 transition-all text-left"
          >
            <div className="p-2.5 bg-rose-50 text-rose-700 rounded-lg">
              <File className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-slate-900">PDF Report</div>
              <div className="text-[10px] text-slate-500">Printable document</div>
            </div>
          </button>
        </div>

        {/* External tracker button */}
        <div className="pt-3 border-t border-slate-100">
          <div className="p-3 bg-brand-50/70 border border-brand-200/80 rounded-xl flex items-center justify-between">
            <div>
              <div className="text-xs font-bold text-brand-950">External Tracker Integration</div>
              <div className="text-[11px] text-brand-700">Sync action items to GitHub Issues</div>
            </div>
            <Button
              size="sm"
              variant="teal"
              onClick={() => {
                onClose();
                onOpenGitHubExport();
              }}
            >
              Export to GitHub
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
};

