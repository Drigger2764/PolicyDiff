import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import { uploadDocument } from '../api/client';

interface DocumentUploadProps {
  workspaceId: string;
  onUploadSuccess: () => void;
  onCancel: () => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  workspaceId,
  onUploadSuccess,
  onCancel,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Information Security');
  const [description, setDescription] = useState('');
  const [versionTag, setVersionTag] = useState('1.0.0');
  const [effectiveDate, setEffectiveDate] = useState(new Date().toISOString().split('T')[0]);

  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      const ext = selected.name.toLowerCase().split('.').pop();
      if (!['pdf', 'docx', 'doc'].includes(ext || '')) {
        setErrorMsg('Invalid format. Please upload a PDF or DOCX file.');
        return;
      }
      if (selected.size > 50 * 1024 * 1024) {
        setErrorMsg('File exceeds 50MB maximum limit.');
        return;
      }
      setFile(selected);
      setErrorMsg(null);
      if (!title) {
        // Auto-fill title from filename
        const cleanName = selected.name.replace(/\.[^/.]+$/, '').replace(/[_-]/g, ' ');
        setTitle(cleanName);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setErrorMsg('Please select a PDF or DOCX document.');
      return;
    }
    if (!title.trim()) {
      setErrorMsg('Please provide a policy title.');
      return;
    }

    try {
      setIsUploading(true);
      setErrorMsg(null);

      const formData = new FormData();
      formData.append('workspace_id', workspaceId);
      formData.append('title', title.trim());
      formData.append('category', category);
      formData.append('version_tag', versionTag.trim());
      if (description.trim()) formData.append('description', description.trim());
      if (effectiveDate) formData.append('effective_date', effectiveDate);
      formData.append('file', file);

      await uploadDocument(formData);
      setIsUploading(false);
      onUploadSuccess();
    } catch (err: any) {
      setIsUploading(false);
      setErrorMsg(err.message || 'Upload and parsing failed.');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="pb-3 border-b border-slate-800">
        <h1 className="text-xl font-semibold text-slate-100 tracking-tight">Upload Policy Document</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Upload PDF or Word specifications to extract structured rules and section hierarchy.
        </p>
      </div>

      {errorMsg && (
        <div className="p-3 bg-red-950/50 border border-red-800/80 rounded text-xs text-red-200 flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <span>{errorMsg}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4 bg-slate-900 p-6 rounded border border-slate-800">
        {/* Drag & Drop File Target */}
        <div>
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-1.5">
            File (PDF or DOCX) *
          </label>
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-slate-700 hover:border-slate-500 rounded p-6 text-center cursor-pointer transition bg-slate-950/40"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf,.docx,.doc"
              className="hidden"
            />
            {file ? (
              <div className="flex items-center justify-center space-x-2 text-slate-200">
                <FileText className="w-5 h-5 text-slate-400" />
                <span className="font-medium text-xs truncate max-w-sm">{file.name}</span>
                <span className="text-[10px] text-slate-400 font-mono">
                  ({(file.size / 1024 / 1024).toFixed(2)} MB)
                </span>
              </div>
            ) : (
              <div className="space-y-1">
                <UploadCloud className="w-7 h-7 text-slate-400 mx-auto" />
                <div className="text-xs text-slate-300 font-medium">Click to select document</div>
                <div className="text-[10px] text-slate-400">PDF, DOCX up to 50MB</div>
              </div>
            )}
          </div>
        </div>

        {/* Form Fields Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1">Policy Title *</label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Identity and Key Management Standard"
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600"
            />
          </div>

          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600"
            >
              <option value="Information Security">Information Security</option>
              <option value="Data Privacy">Data Privacy</option>
              <option value="Travel and Expense">Travel and Expense</option>
              <option value="Remote Work">Remote Work</option>
              <option value="Procurement">Procurement</option>
              <option value="Software Development">Software Development</option>
              <option value="Incident Response">Incident Response</option>
              <option value="Legal & Governance">Legal & Governance</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1">Version Tag</label>
            <input
              type="text"
              value={versionTag}
              onChange={(e) => setVersionTag(e.target.value)}
              placeholder="e.g. 1.0.0 or 2024-Q1"
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600 font-mono"
            />
          </div>

          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1">Effective Date</label>
            <input
              type="date"
              value={effectiveDate}
              onChange={(e) => setEffectiveDate(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600"
            />
          </div>
        </div>

        <div>
          <label className="text-xs font-medium text-slate-300 block mb-1">Description / Summary (Optional)</label>
          <textarea
            rows={2}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="High-level description of requirements governed by this policy..."
            className="w-full bg-slate-950 border border-slate-800 rounded p-2.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600 resize-none"
          />
        </div>

        {/* Action Buttons */}
        <div className="pt-2 flex items-center justify-end space-x-3 border-t border-slate-800">
          <button
            type="button"
            onClick={onCancel}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-medium transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isUploading}
            className="flex items-center space-x-1.5 px-4 py-1.5 bg-slate-100 hover:bg-white text-slate-900 rounded text-xs font-semibold transition disabled:opacity-50"
          >
            {isUploading ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Parsing Sections...</span>
              </>
            ) : (
              <span>Upload and Ingest</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
