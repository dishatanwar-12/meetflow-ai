import React, { useEffect, useState } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Skeleton } from '../components/ui/Skeleton';
import { api } from '../services/api';
import { Risk, UnansweredQuestion } from '../types';
import { AlertTriangle, HelpCircle, CheckCircle2, Quote, Send } from 'lucide-react';

export const RisksQuestionsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'risks' | 'questions'>('risks');
  const [risks, setRisks] = useState<Risk[]>([]);
  const [questions, setQuestions] = useState<UnansweredQuestion[]>([]);
  const [loading, setLoading] = useState(true);

  // Question answer form
  const [answeringId, setAnsweringId] = useState<string | null>(null);
  const [answerText, setAnswerText] = useState('');
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [rList, qList] = await Promise.all([
        api.getRisks(),
        api.getQuestions(),
      ]);
      setRisks(rList);
      setQuestions(qList);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const handleResolveRisk = async (id: string) => {
    setActionLoading(id);
    try {
      await api.resolveRisk(id);
      loadData();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setActionLoading(null);
    }
  };

  const handleAnswerQuestion = async (id: string) => {
    if (!answerText.trim()) return;
    setActionLoading(id);
    try {
      await api.answerQuestion(id, answerText.trim());
      setAnsweringId(null);
      setAnswerText('');
      loadData();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Risks & Questions Register</h1>
        <p className="text-xs text-slate-500 mt-1">
          Review potential blockers, project risks, and open clarification questions needing client input.
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <nav className="flex space-x-6">
          <button
            onClick={() => setActiveTab('risks')}
            className={`py-3 px-1 border-b-2 text-xs sm:text-sm font-medium transition-colors flex items-center gap-2 ${
              activeTab === 'risks'
                ? 'border-brand-900 text-brand-900 font-semibold'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            Risks ({risks.length})
          </button>

          <button
            onClick={() => setActiveTab('questions')}
            className={`py-3 px-1 border-b-2 text-xs sm:text-sm font-medium transition-colors flex items-center gap-2 ${
              activeTab === 'questions'
                ? 'border-brand-900 text-brand-900 font-semibold'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            <HelpCircle className="w-4 h-4 text-sky-600" />
            Unanswered Questions ({questions.filter(q => q.status === 'open').length})
          </button>
        </nav>
      </div>

      {loading ? (
        <div className="space-y-3">
          <Skeleton className="h-28 w-full rounded-xl" />
          <Skeleton className="h-28 w-full rounded-xl" />
        </div>
      ) : activeTab === 'risks' ? (
        <div className="space-y-3">
          {risks.length === 0 ? (
            <Card className="p-12 text-center text-slate-500">
              <p className="text-sm font-medium">No risks recorded.</p>
            </Card>
          ) : (
            risks.map((risk) => (
              <Card key={risk.id} className="p-4 border border-slate-200">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-bold text-slate-900">{risk.description}</span>
                      <Badge variant={risk.status === 'open' ? 'warning' : 'success'}>
                        {risk.status.toUpperCase()}
                      </Badge>
                      {risk.potential_impact && (
                        <Badge variant="neutral">Impact: {risk.potential_impact}</Badge>
                      )}
                    </div>

                    {risk.mitigation && (
                      <p className="text-xs text-slate-600">
                        <span className="font-semibold text-slate-700">Mitigation:</span> {risk.mitigation}
                      </p>
                    )}

                    {risk.evidence_passage && (
                      <p className="text-xs text-slate-500 italic">Evidence: "{risk.evidence_passage}"</p>
                    )}
                  </div>

                  {risk.status === 'open' && (
                    <Button
                      size="sm"
                      variant="outline"
                      isLoading={actionLoading === risk.id}
                      onClick={() => handleResolveRisk(risk.id)}
                    >
                      Mark Mitigated
                    </Button>
                  )}
                </div>
              </Card>
            ))
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {questions.length === 0 ? (
            <Card className="p-12 text-center text-slate-500">
              <p className="text-sm font-medium">No open questions.</p>
            </Card>
          ) : (
            questions.map((q) => (
              <Card key={q.id} className="p-4 border border-slate-200">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-slate-900">❓ {q.question}</span>
                    <Badge variant={q.status === 'open' ? 'warning' : 'success'}>
                      {q.status.toUpperCase()}
                    </Badge>
                  </div>

                  {q.clarification_reason && (
                    <p className="text-xs text-slate-600">
                      <span className="font-semibold text-slate-700">Reason:</span> {q.clarification_reason}
                    </p>
                  )}

                  {q.answer ? (
                    <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-900 mt-2">
                      <span className="font-semibold">Resolved Answer:</span> {q.answer}
                    </div>
                  ) : answeringId === q.id ? (
                    <div className="mt-3 space-y-2">
                      <textarea
                        rows={2}
                        value={answerText}
                        onChange={(e) => setAnswerText(e.target.value)}
                        placeholder="Provide answer or resolution..."
                        className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-brand-800"
                      />
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          variant="primary"
                          isLoading={actionLoading === q.id}
                          onClick={() => handleAnswerQuestion(q.id)}
                        >
                          Submit Answer
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => setAnsweringId(null)}>
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setAnsweringId(q.id);
                        setAnswerText('');
                      }}
                    >
                      Answer Question
                    </Button>
                  )}
                </div>
              </Card>
            ))
          )}
        </div>
      )}
    </div>
  );
};

