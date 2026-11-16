import React, { useState, useEffect } from 'react';
import { History, FileText, ChevronRight, Layers, FileCode, CheckCircle, RefreshCw } from 'lucide-react';
import { Document, DocumentVersion, ExtractedSection } from '../types';
import { fetchDocumentVersions, fetchVersionSections } from '../api/client';

interface DocumentVersionManagementProps {
  document: Document | null;
  documents: Document[];
  onSelectDocument: (doc: Document) => void;
  onNavigateToDiff: () => void;
}

export const DocumentVersionManagement: React.FC<DocumentVersionManagementProps> = ({
  document,
  documents,
  onSelectDocument,
  onNavigateToDiff,
}) => {
  const [versions, setVersions] = useState<DocumentVersion[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<DocumentVersion | null>(null);
  const [sections, setSections] = useState<ExtractedSection[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (document) {
      loadVersions(document.id);
    }
  }, [document]);

  const loadVersions = async (docId: string) => {
    try {
      setLoading(true);
      const vers = await fetchDocumentVersions(docId);
      setVersions(vers);
      if (vers.length > 0) {
        setSelectedVersion(vers[0]);
        loadSections(vers[0].id);
      } else {
        setSelectedVersion(null);
        setSections([]);
      }
      setLoading(false);
    } catch (e) {
      setLoading(false);
    }
  };

  const loadSections = async (versionId: string) => {
    try {
      const secs = await fetchVersionSections(versionId);
      setSections(secs);
    } catch (e) {}
  };

  if (!document) {
    return (
      <div className="space-y-4">
        <div className="pb-3 border-b border-slate-800">
          <h1 className="text-xl font-semibold text-slate-100 tracking-tight">Version History</h1>
          <p className="text-xs text-slate-400 mt-0.5">Select a policy document to inspect revisions and extracted sections</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded p-4">
          <label className="text-xs font-medium text-slate-300 block mb-2">Select Policy Document:</label>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {documents.map((d) => (
              <button
                key={d.id}
                onClick={() => onSelectDocument(d)}
                className="p-3 bg-slate-950 border border-slate-800 hover:border-slate-700 rounded text-left transition"
              >
                <span className="font-semibold text-xs text-slate-100 block truncate">{d.title}</span>
                <span className="text-[10px] text-slate-400 block mt-0.5">{d.category}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Top Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-semibold text-slate-100 tracking-tight">{document.title}</h1>
            <span className="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-slate-300 font-mono">
              {document.category}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">Version revisions & structure-aware extracted sections</p>
        </div>

        <button
          onClick={onNavigateToDiff}
          className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded text-xs font-medium transition"
        >
          Compare in Split-Screen
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Versions List */}
        <div className="bg-slate-900 border border-slate-800 rounded p-4 space-y-3">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Revisions ({versions.length})
          </h2>

          <div className="space-y-2">
            {versions.map((v) => {
              const isSelected = selectedVersion?.id === v.id;
              return (
                <div
                  key={v.id}
                  onClick={() => {
                    setSelectedVersion(v);
                    loadSections(v.id);
                  }}
                  className={`p-3 rounded border cursor-pointer transition ${
                    isSelected
                      ? 'bg-slate-800/80 border-slate-600 text-slate-100'
                      : 'bg-slate-950 border-slate-800 hover:border-slate-700 text-slate-400'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono text-xs font-bold text-slate-200">v{v.version_tag}</span>
                    <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                      {v.status}
                    </span>
                  </div>
                  <div className="text-[11px] truncate">{v.file_name}</div>
                  <div className="text-[10px] text-slate-400 mt-1 flex items-center justify-between">
                    <span>{(v.file_size_bytes / 1024).toFixed(0)} KB</span>
                    <span>{new Date(v.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Section Hierarchy Details */}
        <div className="md:col-span-2 bg-slate-900 border border-slate-800 rounded p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Extracted Sections ({sections.length})
            </h2>
            {selectedVersion && (
              <span className="text-xs font-mono text-slate-400">
                Format: {selectedVersion.file_format.toUpperCase()}
              </span>
            )}
          </div>

          {sections.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-xs">
              No sections extracted for this version.
            </div>
          ) : (
            <div className="space-y-2.5 max-h-[600px] overflow-y-auto pr-1">
              {sections.map((s) => (
                <div key={s.id} className="bg-slate-950 border border-slate-800 p-3 rounded space-y-1.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {s.section_number && (
                        <span className="font-mono text-xs font-bold text-slate-300 bg-slate-800 px-1.5 py-0.5 rounded">
                          {s.section_number}
                        </span>
                      )}
                      <span className="font-medium text-xs text-slate-100">{s.heading || 'General Section'}</span>
                    </div>
                    <span className="text-[10px] text-slate-400 font-mono">
                      Page {s.page_start} - {s.page_end}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed font-mono bg-slate-900/60 p-2.5 rounded border border-slate-800/80">
                    {s.raw_text}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
