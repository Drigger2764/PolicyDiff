import React, { useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Scale,
  Search,
  Filter,
  ArrowRight,
  ShieldAlert,
  FileText,
} from 'lucide-react';
import { ConflictFinding, ConflictCategory, ConflictSeverity, ConflictStatus } from '../types';
import { submitReview } from '../api/client';

interface ConflictInvestigationProps {
  conflicts: ConflictFinding[];
  onReviewCompleted: () => void;
  selectedConflictId?: string;
}

export const ConflictInvestigation: React.FC<ConflictInvestigationProps> = ({
  conflicts,
  onReviewCompleted,
  selectedConflictId,
}) => {
  const [activeConflict, setActiveConflict] = useState<ConflictFinding | null>(
    conflicts.find((c) => c.id === selectedConflictId) || (conflicts.length > 0 ? conflicts[0] : null)
  );

  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [reviewNotes, setReviewNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const filtered = conflicts.filter((c) => {
    const matchesCat = categoryFilter === 'ALL' || c.category === categoryFilter;
    const matchesStat = statusFilter === 'ALL' || c.status === statusFilter;
    const matchesSearch =
      c.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.rule_a_id.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCat && matchesStat && matchesSearch;
  });

  const handleDecision = async (decision: 'ACCEPTED_CONFLICT' | 'DISMISSED_FALSE_POSITIVE' | 'FLAGGED_FOR_LEGAL') => {
    if (!activeConflict) return;
    try {
      setIsSubmitting(true);
      await submitReview(
        activeConflict.id,
        decision,
        reviewNotes.trim() || undefined,
        decision === 'ACCEPTED_CONFLICT' ? 'Acknowledged contradiction in policy audit log' : undefined
      );
      setIsSubmitting(false);
      setReviewNotes('');
      onReviewCompleted();
    } catch (e) {
      setIsSubmitting(false);
    }
  };

  const categories = [
    'ALL',
    'Direct contradiction',
    'Conditional contradiction',
    'Missing exception',
    'Superseded rule',
    'Ambiguous instruction',
    'Harmless wording change',
  ];

  return (
    <div className="space-y-4">
      {/* Top Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-semibold text-slate-100 tracking-tight">Conflict Investigation Workbench</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Audit pairwise deontic contradictions, missing exceptions, and policy ambiguities
          </p>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-slate-900 p-3 rounded border border-slate-800">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-2.5 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search findings by keyword..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-slate-600"
          />
        </div>

        <div>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600"
          >
            {categories.map((c) => (
              <option key={c} value={c}>
                {c === 'ALL' ? 'All Conflict Categories' : c}
              </option>
            ))}
          </select>
        </div>

        <div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600"
          >
            <option value="ALL">All Review Statuses</option>
            <option value="PENDING">Pending Review</option>
            <option value="RESOLVED">Resolved / Accepted</option>
            <option value="DISMISSED">Dismissed (False Positive)</option>
          </select>
        </div>
      </div>

      {/* Dual Pane Layout: Findings List on Left, Active Evidence on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left column: Findings List */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded overflow-hidden max-h-[720px] flex flex-col">
          <div className="p-3 border-b border-slate-800 bg-slate-950/40 text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center justify-between">
            <span>Findings ({filtered.length})</span>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-slate-800/80">
            {filtered.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-xs">No conflicts match filters.</div>
            ) : (
              filtered.map((c) => {
                const isSelected = activeConflict?.id === c.id;
                return (
                  <div
                    key={c.id}
                    onClick={() => setActiveConflict(c)}
                    className={`p-3.5 cursor-pointer transition ${
                      isSelected
                        ? 'bg-slate-800 text-slate-100 border-l-2 border-slate-200'
                        : 'hover:bg-slate-800/40 text-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-xs truncate max-w-[200px]">{c.category}</span>
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                          c.severity === 'CRITICAL'
                            ? 'bg-red-500/20 text-red-300'
                            : c.severity === 'HIGH'
                            ? 'bg-amber-500/20 text-amber-300'
                            : 'bg-slate-700 text-slate-300'
                        }`}
                      >
                        {c.severity}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">{c.description}</p>
                    <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                      <span>Conf: {(c.confidence * 100).toFixed(0)}%</span>
                      <span
                        className={
                          c.status === 'RESOLVED'
                            ? 'text-emerald-400'
                            : c.status === 'DISMISSED'
                            ? 'text-slate-400'
                            : 'text-amber-400'
                        }
                      >
                        {c.status}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right column: Active Finding Evidence and Review Decision Panel */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded p-5 space-y-4">
          {activeConflict ? (
            <>
              {/* Finding Title & Badges */}
              <div className="flex items-start justify-between border-b border-slate-800 pb-3">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-bold text-slate-100">{activeConflict.category}</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                      {activeConflict.severity}
                    </span>
                  </div>
                  <span className="text-xs text-slate-400 font-mono mt-0.5 block">
                    ID: {activeConflict.id.slice(0, 12)} • Detection Confidence: {(activeConflict.confidence * 100).toFixed(0)}%
                  </span>
                </div>

                <span
                  className={`text-xs px-2.5 py-1 rounded font-mono font-semibold ${
                    activeConflict.status === 'RESOLVED'
                      ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                      : activeConflict.status === 'DISMISSED'
                      ? 'bg-slate-800 text-slate-400'
                      : 'bg-amber-950/60 text-amber-300 border border-amber-800/60'
                  }`}
                >
                  {activeConflict.status}
                </span>
              </div>

              {/* Finding Explanation */}
              <div className="space-y-1">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">
                  Automated Contradiction Rationale
                </span>
                <p className="text-xs text-slate-200 leading-relaxed bg-slate-950 p-3 rounded border border-slate-800">
                  {activeConflict.description}
                </p>
              </div>

              {/* Side-by-side Evidence Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {/* Rule A Evidence */}
                <div className="bg-slate-950 border border-slate-800 rounded p-3.5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Rule A</span>
                    <span className="font-mono text-[10px] text-slate-400">{activeConflict.rule_a_id}</span>
                  </div>
                  <div className="text-xs text-slate-200 font-mono bg-slate-900/80 p-2.5 rounded border border-slate-800">
                    "{activeConflict.rule_a?.raw_text || 'See source text reference.'}"
                  </div>
                  {activeConflict.rule_a && (
                    <div className="text-[10px] text-slate-400 space-y-0.5">
                      <div>Subject: <span className="text-slate-300">{activeConflict.rule_a.subject}</span></div>
                      <div>Obligation: <span className="text-slate-200 font-bold">{activeConflict.rule_a.obligation}</span></div>
                    </div>
                  )}
                </div>

                {/* Rule B Evidence */}
                <div className="bg-slate-950 border border-slate-800 rounded p-3.5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      {activeConflict.rule_b_id ? 'Rule B (Counterpart)' : 'Target Scope'}
                    </span>
                    <span className="font-mono text-[10px] text-slate-400">{activeConflict.rule_b_id || 'Standalone'}</span>
                  </div>
                  <div className="text-xs text-slate-200 font-mono bg-slate-900/80 p-2.5 rounded border border-slate-800">
                    "{activeConflict.rule_b?.raw_text || (activeConflict.rule_b_id ? 'See source text reference.' : 'Unquantified standard / lack of operational metric.')}"
                  </div>
                  {activeConflict.rule_b && (
                    <div className="text-[10px] text-slate-400 space-y-0.5">
                      <div>Subject: <span className="text-slate-300">{activeConflict.rule_b.subject}</span></div>
                      <div>Obligation: <span className="text-slate-200 font-bold">{activeConflict.rule_b.obligation}</span></div>
                    </div>
                  )}
                </div>
              </div>

              {/* Review Determination Actions */}
              <div className="pt-3 border-t border-slate-800 space-y-3">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">
                  Human Determination & Rationale
                </span>

                <textarea
                  rows={2}
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  placeholder="Record auditor notes, clarification ticket reference, or legal guidance..."
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600 resize-none"
                />

                <div className="flex items-center justify-end space-x-2">
                  <button
                    disabled={isSubmitting}
                    onClick={() => handleDecision('DISMISSED_FALSE_POSITIVE')}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    <span>Dismiss (False Positive)</span>
                  </button>

                  <button
                    disabled={isSubmitting}
                    onClick={() => handleDecision('FLAGGED_FOR_LEGAL')}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium bg-amber-950/60 hover:bg-amber-900/60 text-amber-200 border border-amber-800/60 transition"
                  >
                    <Scale className="w-3.5 h-3.5" />
                    <span>Flag for Legal Review</span>
                  </button>

                  <button
                    disabled={isSubmitting}
                    onClick={() => handleDecision('ACCEPTED_CONFLICT')}
                    className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded text-xs font-semibold bg-slate-100 hover:bg-white text-slate-900 transition"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Confirm Contradiction</span>
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="p-12 text-center text-slate-400 text-xs">
              Select a conflict from the left panel to inspect original text evidence.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
