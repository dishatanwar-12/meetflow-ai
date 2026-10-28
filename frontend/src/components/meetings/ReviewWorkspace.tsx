import React, { useState } from 'react';
import { MeetingReviewWorkspaceData, Decision, Task, Risk, Blocker, UnansweredQuestion } from '../../types';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { Alert } from '../ui/Alert';
import { UncertaintyBadge } from '../common/UncertaintyBadge';
import { api } from '../../services/api';
import {
  FileText,
  Scale,
  CheckSquare,
  AlertTriangle,
  HelpCircle,
  Quote,
  CheckCircle,
  XCircle,
  Calendar,
  UserCheck,
  Search,
  ExternalLink,
  MessageSquare
} from 'lucide-react';

interface ReviewWorkspaceProps {
  data: MeetingReviewWorkspaceData;
  onRefresh: () => void;
  onOpenTaskDetail: (task: Task) => void;
  onOpenConfirmOwner: (task: Task) => void;
  onOpenConfirmDueDate: (task: Task) => void;
}

export const ReviewWorkspace: React.FC<ReviewWorkspaceProps> = ({
  data,
  onRefresh,
  onOpenTaskDetail,
  onOpenConfirmOwner,
  onOpenConfirmDueDate,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'decisions' | 'tasks' | 'risks' | 'questions' | 'transcript'>('overview');
  const [transcriptSearch, setTranscriptSearch] = useState('');
  const [highlightedText, setHighlightedText] = useState<string | null>(null);
  const [answeringQuestionId, setAnsweringQuestionId] = useState<string | null>(null);
  const [questionAnswer, setQuestionAnswer] = useState('');
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const { meeting, summary_data, decisions, tasks, risks, blockers, questions, analysis_warnings } = data;

  // Jump from evidence quote directly to the Transcript tab and highlight the passage
  const jumpToTranscript = (passage?: string) => {
    if (!passage) return;
    setHighlightedText(passage);
    setActiveTab('transcript');
  };

  const handleConfirmDecision = async (id: string) => {
    setActionLoading(id);
    try {
      await api.confirmDecision(id);
      onRefresh();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setActionLoading(null);
    }
  };

  const handleRejectDecision = async (id: string) => {
    setActionLoading(id);
    try {
      await api.rejectDecision(id);
      onRefresh();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setActionLoading(null);
    }
  };

  const handleAnswerQuestion = async (id: string) => {
    if (!questionAnswer.trim()) return;
    setActionLoading(id);
    try {
      await api.answerQuestion(id, questionAnswer.trim());
      setAnsweringQuestionId(null);
      setQuestionAnswer('');
      onRefresh();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setActionLoading(null);
    }
  };

  const handleResolveRisk = async (id: string) => {
    setActionLoading(id);
    try {
      await api.resolveRisk(id);
      onRefresh();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setActionLoading(null);
    }
  };

  const tabs = [
    { key: 'overview', label: 'Overview', icon: FileText, count: null },
    { key: 'decisions', label: 'Decisions', icon: Scale, count: decisions.length },
    { key: 'tasks', label: 'Action Items', icon: CheckSquare, count: tasks.length },
    { key: 'risks', label: 'Risks & Blockers', icon: AlertTriangle, count: risks.length + blockers.length },
    { key: 'questions', label: 'Questions', icon: HelpCircle, count: questions.filter(q => q.status === 'open').length },
    { key: 'transcript', label: 'Transcript', icon: Quote, count: null },
  ];

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="border-b border-slate-200">
        <nav className="flex space-x-2 sm:space-x-4 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`py-3 px-3 sm:px-4 border-b-2 font-medium text-xs sm:text-sm flex items-center gap-2 whitespace-nowrap transition-colors ${
                  isActive
                    ? 'border-brand-900 text-brand-900 font-semibold'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
                {tab.count !== null && tab.count > 0 && (
                  <span className={`px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                    isActive ? 'bg-brand-900 text-white' : 'bg-slate-100 text-slate-600'
                  }`}>
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab 1: Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {analysis_warnings && analysis_warnings.length > 0 && (
            <Alert type="warning" title="Data Uncertainty Warnings">
              <ul className="list-disc pl-4 space-y-1 mt-1">
                {analysis_warnings.map((warn, i) => (
                  <li key={i}>{warn}</li>
                ))}
              </ul>
            </Alert>
          )}

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="p-4 bg-white border border-slate-200">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Tasks</div>
              <div className="text-2xl font-bold text-slate-900 mt-1">{tasks.length}</div>
              <div className="text-xs text-amber-600 font-medium mt-1">
                {tasks.filter(t => t.confirmation_required).length} need review
              </div>
            </Card>

            <Card className="p-4 bg-white border border-slate-200">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Decisions</div>
              <div className="text-2xl font-bold text-slate-900 mt-1">{decisions.length}</div>
              <div className="text-xs text-emerald-600 font-medium mt-1">
                {decisions.filter(d => d.status === 'confirmed').length} confirmed
              </div>
            </Card>

            <Card className="p-4 bg-white border border-slate-200">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Open Risks</div>
              <div className="text-2xl font-bold text-slate-900 mt-1">{risks.filter(r => r.status === 'open').length}</div>
              <div className="text-xs text-slate-500 mt-1">{blockers.length} blockers</div>
            </Card>

            <Card className="p-4 bg-white border border-slate-200">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Open Questions</div>
              <div className="text-2xl font-bold text-slate-900 mt-1">{questions.filter(q => q.status === 'open').length}</div>
              <div className="text-xs text-brand-600 font-medium mt-1">Requiring answers</div>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Executive Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-700 leading-relaxed">
                {summary_data?.meeting_summary || 'No executive summary generated yet.'}
              </p>

              {summary_data?.topics && summary_data.topics.length > 0 && (
                <div className="mt-5 pt-4 border-t border-slate-100">
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Key Discussion Topics</h4>
                  <div className="flex flex-wrap gap-2">
                    {summary_data.topics.map((topic, i) => (
                      <span key={i} className="px-3 py-1 bg-slate-100 text-slate-800 rounded-full text-xs font-medium">
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tab 2: Decisions */}
      {activeTab === 'decisions' && (
        <div className="space-y-4">
          {decisions.length === 0 ? (
            <Card className="p-12 text-center text-slate-500">
              <Scale className="w-10 h-10 mx-auto text-slate-400 mb-2" />
              <p className="text-sm font-medium">No decisions recorded for this meeting.</p>
            </Card>
          ) : (
            decisions.map((dec) => (
              <Card key={dec.id} className="p-5 border border-slate-200 hover:border-slate-300 transition-colors">
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h4 className="text-base font-semibold text-slate-900">{dec.title}</h4>
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
                        <span className="font-semibold">Approver/Owner:</span> {dec.owner_or_approver}
                      </div>
                    )}

                    {dec.evidence_passage && (
                      <div
                        onClick={() => jumpToTranscript(dec.evidence_passage)}
                        className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600 italic cursor-pointer hover:bg-slate-100 transition-colors flex items-start gap-2"
                        title="Click to view in transcript"
                      >
                        <Quote className="w-3.5 h-3.5 text-slate-400 mt-0.5 flex-shrink-0" />
                        <span className="flex-1">"{dec.evidence_passage}"</span>
                        <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    {dec.status !== 'confirmed' && (
                      <Button
                        size="sm"
                        variant="teal"
                        isLoading={actionLoading === dec.id}
                        onClick={() => handleConfirmDecision(dec.id)}
                      >
                        <CheckCircle className="w-3.5 h-3.5 mr-1" /> Confirm
                      </Button>
                    )}
                    {dec.status !== 'rejected' && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="hover:text-rose-600"
                        isLoading={actionLoading === dec.id}
                        onClick={() => handleRejectDecision(dec.id)}
                      >
                        <XCircle className="w-3.5 h-3.5 mr-1" /> Reject
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Tab 3: Action Items */}
      {activeTab === 'tasks' && (
        <div className="space-y-4">
          {tasks.length === 0 ? (
            <Card className="p-12 text-center text-slate-500">
              <CheckSquare className="w-10 h-10 mx-auto text-slate-400 mb-2" />
              <p className="text-sm font-medium">No action items extracted.</p>
            </Card>
          ) : (
            <div className="grid grid-cols-1 gap-3">
              {tasks.map((task) => (
                <Card key={task.id} className="p-4 border border-slate-200 hover:shadow-sm transition-all">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div className="space-y-1.5 flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-semibold text-slate-900">{task.title}</span>
                        <Badge
                          variant={
                            task.status === 'completed' ? 'success' :
                            task.status === 'in_progress' ? 'info' :
                            task.status === 'needs_clarification' ? 'amber' : 'neutral'
                          }
                        >
                          {task.status.replace('_', ' ')}
                        </Badge>
                        <Badge variant="neutral">Priority: {task.priority}</Badge>
                      </div>

                      {task.description && (
                        <p className="text-xs text-slate-600 line-clamp-2">{task.description}</p>
                      )}

                      {/* Owner & Due Date Uncertainty Indicators */}
                      <div className="flex flex-wrap items-center gap-3 text-xs pt-1">
                        <div className="flex items-center gap-1.5">
                          <span className="text-slate-400 font-medium">Owner:</span>
                          <span className="font-semibold text-slate-800">{task.owner_name || 'Unassigned'}</span>
                          <UncertaintyBadge type="owner" status={task.owner_status} />
                          {task.owner_status !== 'user_confirmed' && (
                            <button
                              onClick={() => onOpenConfirmOwner(task)}
                              className="text-[11px] text-brand-900 font-semibold underline hover:text-brand-700 ml-1"
                            >
                              Assign / Confirm
                            </button>
                          )}
                        </div>

                        <div className="flex items-center gap-1.5">
                          <span className="text-slate-400 font-medium">Due Date:</span>
                          <span className="font-semibold text-slate-800">{task.due_date || task.date_expression || 'None'}</span>
                          <UncertaintyBadge type="due_date" status={task.due_date_status} dateExpression={task.date_expression} />
                          {task.due_date_status !== 'user_confirmed' && (
                            <button
                              onClick={() => onOpenConfirmDueDate(task)}
                              className="text-[11px] text-brand-900 font-semibold underline hover:text-brand-700 ml-1"
                            >
                              Set / Confirm
                            </button>
                          )}
                        </div>
                      </div>

                      {task.confirmation_reason && (
                        <p className="text-[11px] text-amber-700 bg-amber-50/60 px-2 py-0.5 rounded border border-amber-200/50 inline-block">
                          Note: {task.confirmation_reason}
                        </p>
                      )}

                      {task.evidence_passage && (
                        <div
                          onClick={() => jumpToTranscript(task.evidence_passage)}
                          className="text-xs text-slate-500 italic hover:text-brand-900 cursor-pointer flex items-center gap-1 pt-0.5"
                        >
                          <Quote className="w-3 h-3 text-slate-400" />
                          <span className="truncate">"{task.evidence_passage}"</span>
                          <span className="text-[10px] text-brand-900 underline font-semibold ml-1">View in transcript</span>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2 pt-2 md:pt-0">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => onOpenTaskDetail(task)}
                        className="text-xs"
                      >
                        <MessageSquare className="w-3.5 h-3.5 mr-1" />
                        Details ({task.comments_count || 0})
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Risks & Blockers */}
      {activeTab === 'risks' && (
        <div className="space-y-6">
          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              Identified Risks ({risks.length})
            </h4>
            {risks.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No significant risks flagged in this meeting.</p>
            ) : (
              <div className="space-y-3">
                {risks.map((risk) => (
                  <Card key={risk.id} className="p-4 border border-slate-200">
                    <div className="flex items-start justify-between gap-4">
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-slate-900">{risk.description}</span>
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
                          <p
                            onClick={() => jumpToTranscript(risk.evidence_passage)}
                            className="text-xs text-slate-500 italic cursor-pointer hover:underline"
                          >
                            Evidence: "{risk.evidence_passage}"
                          </p>
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
                ))}
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-slate-200">
            <h4 className="text-sm font-semibold text-slate-900 mb-3 flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-sky-600" />
              Blockers & Dependencies ({blockers.length})
            </h4>
            {blockers.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No blockers identified.</p>
            ) : (
              <div className="space-y-3">
                {blockers.map((blocker) => (
                  <Card key={blocker.id} className="p-4 border border-slate-200">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-slate-900">{blocker.description}</span>
                      <Badge variant="neutral">{blocker.dependency_type}</Badge>
                    </div>
                    {blocker.resolution_question && (
                      <p className="text-xs text-sky-700 mt-1">Resolution Question: {blocker.resolution_question}</p>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 5: Questions */}
      {activeTab === 'questions' && (
        <div className="space-y-4">
          {questions.length === 0 ? (
            <Card className="p-12 text-center text-slate-500">
              <HelpCircle className="w-10 h-10 mx-auto text-slate-400 mb-2" />
              <p className="text-sm font-medium">All questions have been resolved.</p>
            </Card>
          ) : (
            questions.map((q) => (
              <Card key={q.id} className="p-4 border border-slate-200">
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-semibold text-slate-900">❓ {q.question}</span>
                      <Badge variant={q.status === 'open' ? 'warning' : 'success'}>
                        {q.status.toUpperCase()}
                      </Badge>
                    </div>
                  </div>

                  {q.clarification_reason && (
                    <p className="text-xs text-slate-600">
                      <span className="font-semibold text-slate-700">Why Clarification is Needed:</span> {q.clarification_reason}
                    </p>
                  )}

                  {q.suggested_person && (
                    <p className="text-xs text-slate-500">
                      <span className="font-semibold">Suggested to ask:</span> {q.suggested_person}
                    </p>
                  )}

                  {q.evidence_passage && (
                    <p
                      onClick={() => jumpToTranscript(q.evidence_passage)}
                      className="text-xs text-slate-500 italic cursor-pointer hover:underline"
                    >
                      Source Evidence: "{q.evidence_passage}"
                    </p>
                  )}

                  {q.answer ? (
                    <div className="p-3 bg-emerald-50/70 border border-emerald-200 rounded-lg text-xs text-emerald-900 mt-2">
                      <span className="font-semibold">Answer:</span> {q.answer}
                      {q.answered_by_name && (
                        <span className="text-[10px] text-emerald-700 block mt-0.5">Answered by {q.answered_by_name}</span>
                      )}
                    </div>
                  ) : answeringQuestionId === q.id ? (
                    <div className="mt-3 space-y-2">
                      <textarea
                        rows={2}
                        value={questionAnswer}
                        onChange={(e) => setQuestionAnswer(e.target.value)}
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
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => setAnsweringQuestionId(null)}
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="pt-1">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setAnsweringQuestionId(q.id);
                          setQuestionAnswer('');
                        }}
                      >
                        Provide Answer
                      </Button>
                    </div>
                  )}
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Tab 6: Transcript */}
      {activeTab === 'transcript' && (
        <Card>
          <CardHeader>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 w-full">
              <CardTitle>Meeting Transcript</CardTitle>
              <div className="relative w-full sm:w-64">
                <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search in transcript..."
                  value={transcriptSearch}
                  onChange={(e) => setTranscriptSearch(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-brand-800"
                />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {highlightedText && (
              <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 flex items-center justify-between">
                <span>Highlighting source passage from outcome selection: <b>"{highlightedText}"</b></span>
                <button
                  onClick={() => setHighlightedText(null)}
                  className="text-amber-800 font-semibold underline ml-2"
                >
                  Clear Highlight
                </button>
              </div>
            )}

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg max-h-[600px] overflow-y-auto font-mono text-xs text-slate-800 leading-relaxed whitespace-pre-wrap">
              {meeting.raw_transcript ? (
                meeting.raw_transcript.split('\n').map((line, idx) => {
                  const isHighlighted = highlightedText && line.toLowerCase().includes(highlightedText.toLowerCase());
                  const isSearched = transcriptSearch && line.toLowerCase().includes(transcriptSearch.toLowerCase());

                  return (
                    <div
                      key={idx}
                      className={`py-0.5 px-1 rounded ${
                        isHighlighted ? 'bg-amber-200 font-bold' : isSearched ? 'bg-sky-100' : ''
                      }`}
                    >
                      {line}
                    </div>
                  );
                })
              ) : (
                <span className="text-slate-400 italic">No transcript recorded for this meeting.</span>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
