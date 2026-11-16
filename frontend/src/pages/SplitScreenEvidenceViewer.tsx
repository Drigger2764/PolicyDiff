import React, { useState } from 'react';
import { Columns, FileText, ArrowRight, ShieldAlert, Sparkles } from 'lucide-react';
import { Document, DocumentVersion, ExtractedSection } from '../types';

interface SplitScreenEvidenceViewerProps {
  documents: Document[];
}

export const SplitScreenEvidenceViewer: React.FC<SplitScreenEvidenceViewerProps> = ({ documents }) => {
  const [docAId, setDocAId] = useState<string>(documents.length > 0 ? documents[0].id : '');
  const [docBId, setDocBId] = useState<string>(documents.length > 1 ? documents[1].id : (documents.length > 0 ? documents[0].id : ''));

  const docA = documents.find((d) => d.id === docAId);
  const docB = documents.find((d) => d.id === docBId);

  const sectionsA: ExtractedSection[] = docA?.versions?.[0]?.sections || [];
  const sectionsB: ExtractedSection[] = docB?.versions?.[0]?.sections || [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-semibold text-slate-100 tracking-tight">Split-Screen Evidence Viewer</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Side-by-side comparative analysis of policy clauses, version revisions, and operative text
          </p>
        </div>
      </div>

      {/* Document Selectors Header */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left Side Selector */}
        <div className="bg-slate-900 border border-slate-800 p-3 rounded space-y-1">
          <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">
            Baseline Document (Left Pane)
          </label>
          <select
            value={docAId}
            onChange={(e) => setDocAId(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600"
          >
            {documents.map((d) => (
              <option key={d.id} value={d.id}>
                {d.title} ({d.category})
              </option>
            ))}
          </select>
        </div>

        {/* Right Side Selector */}
        <div className="bg-slate-900 border border-slate-800 p-3 rounded space-y-1">
          <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">
            Comparison Target (Right Pane)
          </label>
          <select
            value={docBId}
            onChange={(e) => setDocBId(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600"
          >
            {documents.map((d) => (
              <option key={d.id} value={d.id}>
                {d.title} ({d.category})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Dual Pane Evidence Display */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left Pane Document Content */}
        <div className="bg-slate-900 border border-slate-800 rounded p-4 flex flex-col max-h-[640px]">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800 mb-3">
            <div className="flex items-center space-x-2 truncate">
              <FileText className="w-4 h-4 text-slate-400 shrink-0" />
              <span className="font-semibold text-xs text-slate-100 truncate">{docA?.title || 'None'}</span>
            </div>
            <span className="text-[10px] text-slate-400 font-mono">
              {sectionsA.length} {sectionsA.length === 1 ? 'section' : 'sections'}
            </span>
          </div>

          <div className="flex-1 overflow-y-auto space-y-3 pr-1">
            {sectionsA.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">
                No section text available for this document.
              </div>
            ) : (
              sectionsA.map((sec) => (
                <div key={sec.id} className="bg-slate-950 border border-slate-800 rounded p-3 space-y-1">
                  <div className="flex items-center justify-between text-[11px] text-slate-300 font-medium">
                    <span>{sec.heading || `Section ${sec.order_index + 1}`}</span>
                    {sec.page_start && <span className="text-[10px] text-slate-400 font-mono">P. {sec.page_start}</span>}
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed font-mono whitespace-pre-wrap bg-slate-900/60 p-2.5 rounded border border-slate-800/80">
                    {sec.raw_text}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Pane Document Content */}
        <div className="bg-slate-900 border border-slate-800 rounded p-4 flex flex-col max-h-[640px]">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800 mb-3">
            <div className="flex items-center space-x-2 truncate">
              <FileText className="w-4 h-4 text-slate-400 shrink-0" />
              <span className="font-semibold text-xs text-slate-100 truncate">{docB?.title || 'None'}</span>
            </div>
            <span className="text-[10px] text-slate-400 font-mono">
              {sectionsB.length} {sectionsB.length === 1 ? 'section' : 'sections'}
            </span>
          </div>

          <div className="flex-1 overflow-y-auto space-y-3 pr-1">
            {sectionsB.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">
                No section text available for this document.
              </div>
            ) : (
              sectionsB.map((sec) => (
                <div key={sec.id} className="bg-slate-950 border border-slate-800 rounded p-3 space-y-1">
                  <div className="flex items-center justify-between text-[11px] text-slate-300 font-medium">
                    <span>{sec.heading || `Section ${sec.order_index + 1}`}</span>
                    {sec.page_start && <span className="text-[10px] text-slate-400 font-mono">P. {sec.page_start}</span>}
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed font-mono whitespace-pre-wrap bg-slate-900/60 p-2.5 rounded border border-slate-800/80">
                    {sec.raw_text}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
