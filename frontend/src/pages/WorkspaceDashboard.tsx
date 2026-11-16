import React from 'react';
import {
  FileText,
  AlertTriangle,
  CheckCircle2,
  Play,
  Layers,
  ArrowRight,
  ShieldCheck,
  RefreshCw,
} from 'lucide-react';
import { ConflictFinding, Document } from '../types';

interface WorkspaceDashboardProps {
  workspaceName: string;
  documents: Document[];
  conflicts: ConflictFinding[];
  isAnalyzing: boolean;
  onRunAnalysis: () => void;
  onNavigate: (page: any) => void;
  onSelectConflict: (conflict: ConflictFinding) => void;
}

export const WorkspaceDashboard: React.FC<WorkspaceDashboardProps> = ({
  workspaceName,
  documents,
  conflicts,
  isAnalyzing,
  onRunAnalysis,
  onNavigate,
  onSelectConflict,
}) => {
  const pendingConflicts = conflicts.filter((c) => c.status === 'PENDING');
  const resolvedConflicts = conflicts.filter((c) => c.status === 'RESOLVED');
  const criticalCount = conflicts.filter((c) => c.severity === 'CRITICAL').length;
  const highCount = conflicts.filter((c) => c.severity === 'HIGH').length;
  const resolutionRate = conflicts.length > 0 ? ((resolvedConflicts.length / conflicts.length) * 100).toFixed(0) : '0';

  return (
    <div className="space-y-6">
      {/* Top Banner / Actions */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-100 tracking-tight">{workspaceName}</h1>
          <p className="text-xs text-slate-400 mt-0.5">Policy Document Compliance & Deontic Governance Overview</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => onNavigate('upload')}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded text-xs font-medium transition"
          >
            + Upload Policy
          </button>
          <button
            onClick={onRunAnalysis}
            disabled={isAnalyzing || documents.length === 0}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-slate-100 hover:bg-white text-slate-900 rounded text-xs font-semibold transition disabled:opacity-50 shadow-sm"
          >
            {isAnalyzing ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-slate-900" />
                <span>Analyzing Rules...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current text-slate-900" />
                <span>Run Contradiction Engine</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Metric KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded">
          <span className="text-[11px] font-medium uppercase tracking-wider text-slate-400 block">Total Policies</span>
          <div className="text-2xl font-bold text-slate-100 mt-1">{documents.length}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Active across revisions</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded">
          <span className="text-[11px] font-medium uppercase tracking-wider text-slate-400 block">Conflict Findings</span>
          <div className="text-2xl font-bold text-slate-100 mt-1">{conflicts.length}</div>
          <span className="text-[11px] text-amber-400 mt-1 block font-medium">
            {criticalCount} Critical • {highCount} High
          </span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded">
          <span className="text-[11px] font-medium uppercase tracking-wider text-slate-400 block">Pending Review</span>
          <div className="text-2xl font-bold text-slate-100 mt-1">{pendingConflicts.length}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Awaiting analyst action</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded">
          <span className="text-[11px] font-medium uppercase tracking-wider text-slate-400 block">Resolution Rate</span>
          <div className="text-2xl font-bold text-slate-100 mt-1">{resolutionRate}%</div>
          <span className="text-[11px] text-emerald-400 mt-1 block">{resolvedConflicts.length} determinations applied</span>
        </div>
      </div>

      {/* Investigation Workbench Quick Triage */}
      <div className="bg-slate-900 border border-slate-800 rounded">
        <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
              High Priority Discrepancies ({conflicts.slice(0, 5).length})
            </h2>
          </div>
          <button
            onClick={() => onNavigate('conflicts')}
            className="text-xs text-slate-400 hover:text-slate-200 flex items-center space-x-1 transition font-medium"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {conflicts.length === 0 ? (
          <div className="p-8 text-center">
            <ShieldCheck className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <h3 className="text-sm font-medium text-slate-300">No conflicts currently recorded</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              Upload policies into this workspace and click "Run Contradiction Engine" to extract deontic rules and identify gaps.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-slate-800/80">
            {conflicts.slice(0, 5).map((c) => (
              <div
                key={c.id}
                onClick={() => onSelectConflict(c)}
                className="p-4 hover:bg-slate-800/40 cursor-pointer transition flex items-start justify-between gap-4"
              >
                <div className="space-y-1 max-w-3xl">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-semibold text-slate-200">{c.category}</span>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded font-medium border ${
                        c.severity === 'CRITICAL'
                          ? 'bg-red-500/10 text-red-300 border-red-500/30'
                          : c.severity === 'HIGH'
                          ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                          : 'bg-slate-800 text-slate-300 border-slate-700'
                      }`}
                    >
                      {c.severity}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">{(c.confidence * 100).toFixed(0)}% confidence</span>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">{c.description}</p>
                </div>

                <div className="text-right shrink-0">
                  <span
                    className={`text-[11px] px-2 py-0.5 rounded font-mono ${
                      c.status === 'RESOLVED'
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                        : c.status === 'DISMISSED'
                        ? 'bg-slate-800 text-slate-400'
                        : 'bg-amber-950/40 text-amber-300 border border-amber-800/60'
                    }`}
                  >
                    {c.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
