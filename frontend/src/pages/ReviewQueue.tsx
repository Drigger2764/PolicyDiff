import React, { useState } from 'react';
import { CheckSquare, CheckCircle2, XCircle, Scale, ShieldAlert, ArrowRight, CornerDownRight } from 'lucide-react';
import { ConflictFinding } from '../types';
import { submitReview } from '../api/client';

interface ReviewQueueProps {
  conflicts: ConflictFinding[];
  onReviewSubmitted: () => void;
}

export const ReviewQueue: React.FC<ReviewQueueProps> = ({ conflicts, onReviewSubmitted }) => {
  const pending = conflicts.filter((c) => c.status === 'PENDING');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const active = pending.length > 0 && currentIndex < pending.length ? pending[currentIndex] : null;

  const handleAction = async (decision: 'ACCEPTED_CONFLICT' | 'DISMISSED_FALSE_POSITIVE' | 'FLAGGED_FOR_LEGAL') => {
    if (!active) return;
    try {
      setIsSubmitting(true);
      await submitReview(
        active.id,
        decision,
        notes.trim() || undefined,
        decision === 'ACCEPTED_CONFLICT' ? 'Added to audit exceptions log' : undefined
      );
      setIsSubmitting(false);
      setNotes('');
      onReviewSubmitted();
    } catch (e) {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-4 max-w-4xl mx-auto">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-semibold text-slate-100 tracking-tight">Compliance Review Queue</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Rapid auditor triage workflow for pending contradictions and ambiguities
          </p>
        </div>
        <div className="text-xs font-mono bg-slate-900 border border-slate-800 px-3 py-1.5 rounded text-slate-300">
          Pending Queue: <span className="font-bold text-amber-400">{pending.length}</span> remaining
        </div>
      </div>

      {pending.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded p-12 text-center space-y-2">
          <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
          <h2 className="text-sm font-semibold text-slate-100">Review Queue Cleared</h2>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            All detected conflict findings have been reviewed and determinations applied to the audit record.
          </p>
        </div>
      ) : active ? (
        <div className="bg-slate-900 border border-slate-800 rounded p-6 space-y-5">
          {/* Card Progress / Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                Item {currentIndex + 1} of {pending.length}
              </span>
              <span className="text-sm font-bold text-slate-100">{active.category}</span>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                {active.severity}
              </span>
            </div>
            <span className="text-xs font-mono text-slate-400">
              Confidence: {(active.confidence * 100).toFixed(0)}%
            </span>
          </div>

          {/* Finding Description */}
          <div className="space-y-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">
              Flagged Discrepancy
            </span>
            <p className="text-xs text-slate-200 leading-relaxed bg-slate-950 p-3 rounded border border-slate-800">
              {active.description}
            </p>
          </div>

          {/* Dual Text Evidence */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="bg-slate-950 p-3 rounded border border-slate-800 space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                Rule A Text ({active.rule_a_id})
              </span>
              <p className="text-slate-200 font-mono">
                "{active.rule_a?.raw_text || active.rule_a_id}"
              </p>
            </div>

            <div className="bg-slate-950 p-3 rounded border border-slate-800 space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                {active.rule_b_id ? `Rule B Text (${active.rule_b_id})` : 'Target Scope'}
              </span>
              <p className="text-slate-200 font-mono">
                "{active.rule_b?.raw_text || (active.rule_b_id ? active.rule_b_id : 'Ambiguous directive lacking standard metric.')}"
              </p>
            </div>
          </div>

          {/* Review Notes */}
          <div className="space-y-1.5 pt-2 border-t border-slate-800">
            <label className="text-xs font-medium text-slate-300 block">
              Auditor Determination Rationale / Remediation Plan
            </label>
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Confirmed contradiction. Jira ticket POL-402 created to align regional clause..."
              className="w-full bg-slate-950 border border-slate-800 rounded p-2.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600 resize-none"
            />
          </div>

          {/* Decision Buttons */}
          <div className="pt-2 flex items-center justify-between border-t border-slate-800">
            <button
              onClick={() => setCurrentIndex((prev) => (prev > 0 ? prev - 1 : pending.length - 1))}
              className="text-xs text-slate-400 hover:text-slate-200"
            >
              ← Previous Item
            </button>

            <div className="flex items-center space-x-2.5">
              <button
                disabled={isSubmitting}
                onClick={() => handleAction('DISMISSED_FALSE_POSITIVE')}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
              >
                <XCircle className="w-3.5 h-3.5" />
                <span>Dismiss (False Positive)</span>
              </button>

              <button
                disabled={isSubmitting}
                onClick={() => handleAction('FLAGGED_FOR_LEGAL')}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium bg-amber-950/60 hover:bg-amber-900/60 text-amber-200 border border-amber-800/60 transition"
              >
                <Scale className="w-3.5 h-3.5" />
                <span>Escalate to Legal</span>
              </button>

              <button
                disabled={isSubmitting}
                onClick={() => handleAction('ACCEPTED_CONFLICT')}
                className="flex items-center space-x-1.5 px-4 py-1.5 rounded text-xs font-semibold bg-slate-100 hover:bg-white text-slate-900 transition"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Accept Conflict</span>
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
