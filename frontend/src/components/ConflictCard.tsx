import React from 'react';
import { ConflictFinding, ConflictSeverity } from '../types';
import { AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';

interface ConflictCardProps {
  conflict: ConflictFinding;
  onReview?: (decision: 'ACCEPTED_CONFLICT' | 'DISMISSED_FALSE_POSITIVE') => void;
}

const severityBadge: Record<ConflictSeverity, string> = {
  CRITICAL: 'bg-red-500/20 text-red-300 border-red-500/40',
  HIGH: 'bg-orange-500/20 text-orange-300 border-orange-500/40',
  MEDIUM: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40',
  LOW: 'bg-blue-500/20 text-blue-300 border-blue-500/40',
  INFO: 'bg-slate-500/20 text-slate-300 border-slate-500/40',
};

export const ConflictCard: React.FC<ConflictCardProps> = ({ conflict, onReview }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 shadow-sm space-y-4">
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
          <div>
            <h3 className="font-semibold text-white text-base leading-tight">{conflict.category}</h3>
            <span className="text-xs text-slate-400">Confidence: {(conflict.confidence * 100).toFixed(0)}%</span>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`text-xs px-2.5 py-0.5 rounded font-medium border ${severityBadge[conflict.severity]}`}>
            {conflict.severity}
          </span>
          <span
            className={`text-xs px-2 py-0.5 rounded font-mono ${
              conflict.status === 'RESOLVED'
                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                : conflict.status === 'DISMISSED'
                ? 'bg-slate-800 text-slate-400'
                : 'bg-amber-950/60 text-amber-300 border border-amber-800/60'
            }`}
          >
            {conflict.status}
          </span>
        </div>
      </div>

      <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded border border-slate-800/80">
        {conflict.description}
      </p>

      {/* Rules in Contradiction */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
        <div className="bg-slate-950 p-3 rounded border border-slate-800">
          <span className="text-slate-400 uppercase tracking-wider block font-semibold mb-1">Rule A</span>
          <p className="text-slate-200">{conflict.rule_a?.raw_text || conflict.rule_a_id}</p>
        </div>
        <div className="bg-slate-950 p-3 rounded border border-slate-800">
          <span className="text-slate-400 uppercase tracking-wider block font-semibold mb-1">
            {conflict.rule_b_id ? 'Rule B' : 'Context Scope'}
          </span>
          <p className="text-slate-200">
            {conflict.rule_b?.raw_text || conflict.rule_b_id || 'Standalone policy ambiguity / lack of objective criteria.'}
          </p>
        </div>
      </div>

      {/* Action Workbench Buttons */}
      {conflict.status === 'PENDING' && onReview && (
        <div className="pt-2 flex items-center justify-end space-x-3 border-t border-slate-800">
          <button
            onClick={() => onReview('DISMISSED_FALSE_POSITIVE')}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
          >
            <XCircle className="w-3.5 h-3.5" />
            <span>Dismiss (False Positive)</span>
          </button>
          <button
            onClick={() => onReview('ACCEPTED_CONFLICT')}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium bg-indigo-600 hover:bg-indigo-500 text-white transition shadow-sm"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Accept Conflict</span>
          </button>
        </div>
      )}
    </div>
  );
};
