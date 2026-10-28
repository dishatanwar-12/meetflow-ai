import React, { useEffect, useState } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Skeleton } from '../components/ui/Skeleton';
import { api } from '../services/api';
import { Decision } from '../types';
import { Scale, CheckCircle, XCircle, Search, Quote } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const DecisionsPage: React.FC = () => {
  const { isPM } = useAuth();
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    loadDecisions();
  }, [statusFilter]);

  const loadDecisions = async () => {
    setLoading(true);
    try {
      const data = await api.getDecisions({
        status: statusFilter || undefined,
      });
      setDecisions(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (id: string) => {
    setActionLoading(id);
    try {
      await api.confirmDecision(id);
      loadDecisions();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (id: string) => {
    setActionLoading(id);
    try {
      await api.rejectDecision(id);
      loadDecisions();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Decisions Register</h1>
          <p className="text-xs text-slate-500 mt-1">
            Enterprise log of proposed, confirmed, and superseded architectural and project decisions.
          </p>
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3.5 py-2 text-xs border border-slate-300 rounded-lg bg-white text-slate-700"
        >
          <option value="">All Statuses</option>
          <option value="confirmed">Confirmed</option>
          <option value="proposed">Proposed</option>
          <option value="rejected">Rejected</option>
          <option value="superseded">Superseded</option>
          <option value="disputed">Disputed</option>
        </select>
      </div>

      {loading ? (
        <div className="space-y-3">
          <Skeleton className="h-28 w-full rounded-xl" />
          <Skeleton className="h-28 w-full rounded-xl" />
        </div>
      ) : decisions.length === 0 ? (
        <Card className="p-12 text-center text-slate-500">
          <Scale className="w-12 h-12 mx-auto text-slate-400 mb-3" />
          <h3 className="text-sm font-semibold text-slate-800">No decisions recorded</h3>
          <p className="text-xs text-slate-500 mt-1">Decisions extracted from client meetings will appear here.</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {decisions.map((dec) => (
            <Card key={dec.id} className="p-5 border border-slate-200">
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="text-base font-bold text-slate-900">{dec.title}</h3>
                    <Badge
                      variant={
                        dec.status === 'confirmed' ? 'success' :
                        dec.status === 'proposed' ? 'amber' :
                        dec.status === 'rejected' ? 'danger' : 'neutral'
                      }
                    >
                      {dec.status.toUpperCase()}
                    </Badge>
                    {dec.confirmation_required && (
                      <Badge variant="warning">Confirmation Needed</Badge>
                    )}
                  </div>

                  {dec.description && (
                    <p className="text-xs text-slate-600 leading-relaxed">{dec.description}</p>
                  )}

                  {dec.owner_or_approver && (
                    <div className="text-xs text-slate-500">
                      <span className="font-semibold">Approver:</span> {dec.owner_or_approver}
                    </div>
                  )}

                  {dec.evidence_passage && (
                    <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600 italic flex items-start gap-2">
                      <Quote className="w-3.5 h-3.5 text-slate-400 mt-0.5 flex-shrink-0" />
                      <span>"{dec.evidence_passage}"</span>
                    </div>
                  )}
                </div>

                {isPM && (
                  <div className="flex items-center gap-2 pt-2 md:pt-0">
                    {dec.status !== 'confirmed' && (
                      <Button
                        size="sm"
                        variant="teal"
                        isLoading={actionLoading === dec.id}
                        onClick={() => handleConfirm(dec.id)}
                      >
                        <CheckCircle className="w-3.5 h-3.5 mr-1" /> Confirm
                      </Button>
                    )}
                    {dec.status !== 'rejected' && (
                      <Button
                        size="sm"
                        variant="outline"
                        isLoading={actionLoading === dec.id}
                        onClick={() => handleReject(dec.id)}
                      >
                        <XCircle className="w-3.5 h-3.5 mr-1" /> Reject
                      </Button>
                    )}
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
