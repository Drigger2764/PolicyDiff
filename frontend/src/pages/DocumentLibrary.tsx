import React, { useState } from 'react';
import { FileText, Search, Trash2, Eye, Plus, FileCode, CheckCircle, Clock } from 'lucide-react';
import { Document } from '../types';

interface DocumentLibraryProps {
  documents: Document[];
  onUploadClick: () => void;
  onInspectDocument: (doc: Document) => void;
  onDeleteDocument: (docId: string) => void;
}

export const DocumentLibrary: React.FC<DocumentLibraryProps> = ({
  documents,
  onUploadClick,
  onInspectDocument,
  onDeleteDocument,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');

  const categories = ['ALL', ...Array.from(new Set(documents.map((d) => d.category)))];

  const filtered = documents.filter((doc) => {
    const matchesSearch =
      doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (doc.description && doc.description.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCat = selectedCategory === 'ALL' || doc.category === selectedCategory;
    return matchesSearch && matchesCat;
  });

  return (
    <div className="space-y-4">
      {/* Top Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-semibold text-slate-100 tracking-tight">Document Library</h1>
          <p className="text-xs text-slate-400 mt-0.5">Ingested policy standards, guidelines, and departmental handbooks</p>
        </div>

        <button
          onClick={onUploadClick}
          className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-100 hover:bg-white text-slate-900 rounded text-xs font-semibold transition"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Upload Document</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-900 p-3 rounded border border-slate-800">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-2.5 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search by title, keyword, or scope..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-slate-600"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <span className="text-[11px] font-medium text-slate-400">Category:</span>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600"
          >
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Documents Table */}
      <div className="bg-slate-900 border border-slate-800 rounded overflow-hidden">
        {filtered.length === 0 ? (
          <div className="p-8 text-center">
            <FileText className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <h3 className="text-sm font-medium text-slate-300">No documents found</h3>
            <p className="text-xs text-slate-400 mt-1">Upload a PDF or DOCX file to begin policy rule extraction.</p>
          </div>
        ) : (
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px] font-semibold border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Title & Scope</th>
                <th className="py-2.5 px-4">Category</th>
                <th className="py-2.5 px-4">Revisions</th>
                <th className="py-2.5 px-4">Uploaded</th>
                <th className="py-2.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {filtered.map((doc) => {
                const verCount = doc.versions?.length || 1;
                const latestVersion = doc.versions && doc.versions.length > 0 ? doc.versions[0] : null;
                const dateStr = new Date(doc.created_at).toLocaleDateString();

                return (
                  <tr key={doc.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 font-medium text-slate-100">
                      <div className="flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-slate-400 shrink-0" />
                        <div>
                          <span className="block font-semibold">{doc.title}</span>
                          {doc.description && (
                            <span className="text-[11px] text-slate-400 block truncate max-w-md">
                              {doc.description}
                            </span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-slate-300 font-mono border border-slate-700">
                        {doc.category}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-slate-300 font-mono">{verCount} {verCount === 1 ? 'version' : 'versions'}</span>
                      {latestVersion && (
                        <span className="text-[10px] text-slate-400 block font-mono">v{latestVersion.version_tag}</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono">{dateStr}</td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => onInspectDocument(doc)}
                          title="Inspect Sections & Rules"
                          className="p-1.5 hover:bg-slate-700 rounded text-slate-300 hover:text-white transition"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => {
                            if (window.confirm(`Delete policy "${doc.title}" and all its extracted sections?`)) {
                              onDeleteDocument(doc.id);
                            }
                          }}
                          title="Delete Document"
                          className="p-1.5 hover:bg-red-950/60 rounded text-slate-400 hover:text-red-400 transition"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
