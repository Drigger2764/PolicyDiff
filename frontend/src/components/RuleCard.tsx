import React from 'react';
import { StructuredRule, ObligationType } from '../types';
import { FileText, Tag, AlertCircle } from 'lucide-react';

interface RuleCardProps {
  rule: StructuredRule;
}

const obligationColors: Record<ObligationType, string> = {
  MUST: 'bg-red-950/80 text-red-300 border-red-700/60',
  MUST_NOT: 'bg-rose-950/90 text-rose-200 border-rose-600',
  SHOULD: 'bg-amber-950/80 text-amber-300 border-amber-700/60',
  MAY: 'bg-emerald-950/80 text-emerald-300 border-emerald-700/60',
  CANNOT: 'bg-slate-800 text-slate-300 border-slate-700',
};

export const RuleCard: React.FC<RuleCardProps> = ({ rule }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 shadow-sm hover:border-slate-700 transition">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Tag className="w-4 h-4 text-indigo-400" />
          <span className="font-mono text-sm font-semibold text-indigo-300">{rule.rule_id}</span>
        </div>
        <span
          className={`text-xs px-2.5 py-1 rounded-md font-semibold border ${
            obligationColors[rule.obligations] || 'bg-slate-800 text-slate-300 border-slate-700'
          }`}
        >
          {rule.obligations}
        </span>
      </div>

      <div className="space-y-2 mb-4 text-sm">
        <div>
          <span className="text-slate-400 text-xs uppercase tracking-wider block font-medium">Subject</span>
          <span className="text-white font-medium">{rule.subject}</span>
        </div>

        <div className="grid grid-cols-2 gap-2 pt-1">
          <div>
            <span className="text-slate-400 text-xs uppercase tracking-wider block font-medium">Action</span>
            <span className="text-indigo-200 font-mono text-xs bg-slate-800 px-2 py-0.5 rounded inline-block">
              {rule.action}
            </span>
          </div>
          <div>
            <span className="text-slate-400 text-xs uppercase tracking-wider block font-medium">Target Object</span>
            <span className="text-slate-200 font-mono text-xs bg-slate-800 px-2 py-0.5 rounded inline-block">
              {rule.object}
            </span>
          </div>
        </div>

        {rule.conditions && rule.conditions.length > 0 && (
          <div className="pt-2">
            <span className="text-slate-400 text-xs uppercase tracking-wider block font-medium">Conditions</span>
            <ul className="list-disc list-inside text-xs text-slate-300 space-y-0.5 mt-0.5">
              {rule.conditions.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </div>
        )}

        {rule.exceptions && rule.exceptions.length > 0 && (
          <div className="pt-2">
            <span className="text-amber-400/90 text-xs uppercase tracking-wider block font-medium flex items-center space-x-1">
              <AlertCircle className="w-3 h-3 text-amber-400" />
              <span>Exceptions</span>
            </span>
            <ul className="list-disc list-inside text-xs text-amber-200/90 space-y-0.5 mt-0.5">
              {rule.exceptions.map((e, i) => (
                <li key={i}>{e}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center space-x-1 truncate mr-2">
          <FileText className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          <span className="truncate">{rule.source_document}</span>
        </div>
        <span className="text-slate-500 shrink-0">{rule.source_section}</span>
      </div>
    </div>
  );
};
