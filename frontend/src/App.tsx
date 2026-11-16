import React, { useState, useEffect } from 'react';
import { Navigation, PageId } from './components/Navigation';
import { WorkspaceDashboard } from './pages/WorkspaceDashboard';
import { DocumentLibrary } from './pages/DocumentLibrary';
import { DocumentUpload } from './pages/DocumentUpload';
import { DocumentVersionManagement } from './pages/DocumentVersionManagement';
import { ConflictInvestigation } from './pages/ConflictInvestigation';
import { SplitScreenEvidenceViewer } from './pages/SplitScreenEvidenceViewer';
import { RuleRelationshipGraph } from './pages/RuleRelationshipGraph';
import { ReviewQueue } from './pages/ReviewQueue';
import { AuditReports } from './pages/AuditReports';
import { Workspace, Document, ConflictFinding } from './types';
import {
  fetchWorkspaces,
  createWorkspace,
  fetchDocuments,
  deleteDocument,
  fetchConflicts,
  triggerConflictDetection,
} from './api/client';
import { AlertCircle, X, Plus } from 'lucide-react';

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<PageId>('dashboard');
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string>('');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [conflicts, setConflicts] = useState<ConflictFinding[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [selectedConflictId, setSelectedConflictId] = useState<string | undefined>(undefined);

  const [loading, setLoading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // New Workspace Modal
  const [showWorkspaceModal, setShowWorkspaceModal] = useState(false);
  const [newWsName, setNewWsName] = useState('');
  const [newWsSlug, setNewWsSlug] = useState('');
  const [newWsDesc, setNewWsDesc] = useState('');

  useEffect(() => {
    loadWorkspaces();
  }, []);

  useEffect(() => {
    if (activeWorkspaceId) {
      loadWorkspaceData(activeWorkspaceId);
    }
  }, [activeWorkspaceId]);

  const loadWorkspaces = async () => {
    try {
      setLoading(true);
      const ws = await fetchWorkspaces();
      setWorkspaces(ws);
      if (ws.length > 0) {
        setActiveWorkspaceId(ws[0].id);
      } else {
        // Create initial default workspace if none exist
        const initial = await createWorkspace({
          name: 'Enterprise IT & Security Governance',
          slug: 'infosec-governance',
          description: 'Global IT security and compliance specifications',
        });
        setWorkspaces([initial]);
        setActiveWorkspaceId(initial.id);
      }
      setLoading(false);
    } catch (e: any) {
      setLoading(false);
      setErrorMessage(e.message || 'Failed to initialize workspaces.');
    }
  };

  const loadWorkspaceData = async (wsId: string) => {
    try {
      setErrorMessage(null);
      const [docs, confs] = await Promise.all([
        fetchDocuments(wsId),
        fetchConflicts(wsId),
      ]);
      setDocuments(docs);
      setConflicts(confs);
      if (docs.length > 0 && !selectedDocument) {
        setSelectedDocument(docs[0]);
      }
    } catch (e: any) {
      setErrorMessage(e.message || 'Error loading workspace documents.');
    }
  };

  const handleRunAnalysis = async () => {
    if (!activeWorkspaceId) return;
    try {
      setIsAnalyzing(true);
      setErrorMessage(null);
      const findings = await triggerConflictDetection(activeWorkspaceId);
      setConflicts(findings);
      setIsAnalyzing(false);
    } catch (e: any) {
      setIsAnalyzing(false);
      setErrorMessage(e.message || 'Analysis run failed.');
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    try {
      await deleteDocument(docId);
      loadWorkspaceData(activeWorkspaceId);
    } catch (e: any) {
      setErrorMessage(e.message || 'Failed to delete document.');
    }
  };

  const handleCreateWorkspace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newWsName.trim() || !newWsSlug.trim()) return;
    try {
      const created = await createWorkspace({
        name: newWsName.trim(),
        slug: newWsSlug.trim(),
        description: newWsDesc.trim() || undefined,
      });
      setWorkspaces((prev) => [...prev, created]);
      setActiveWorkspaceId(created.id);
      setShowWorkspaceModal(false);
      setNewWsName('');
      setNewWsSlug('');
      setNewWsDesc('');
    } catch (e: any) {
      setErrorMessage(e.message || 'Failed to create workspace.');
    }
  };

  const activeWorkspace = workspaces.find((w) => w.id === activeWorkspaceId);
  const pendingCount = conflicts.filter((c) => c.status === 'PENDING').length;

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans antialiased">
      {/* Sidebar Navigation */}
      <Navigation
        currentPage={currentPage}
        onSelectPage={setCurrentPage}
        workspaces={workspaces}
        activeWorkspaceId={activeWorkspaceId}
        onSelectWorkspace={setActiveWorkspaceId}
        onOpenCreateWorkspace={() => setShowWorkspaceModal(true)}
        pendingCount={pendingCount}
      />

      {/* Main App Body */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Notification / Error Alert */}
        {errorMessage && (
          <div className="bg-red-950/80 border-b border-red-800 p-3 text-xs text-red-200 flex items-center justify-between px-6">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button onClick={() => setErrorMessage(null)} className="text-red-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
          {currentPage === 'dashboard' && (
            <WorkspaceDashboard
              workspaceName={activeWorkspace?.name || 'PolicyDiff'}
              documents={documents}
              conflicts={conflicts}
              isAnalyzing={isAnalyzing}
              onRunAnalysis={handleRunAnalysis}
              onNavigate={setCurrentPage}
              onSelectConflict={(c) => {
                setSelectedConflictId(c.id);
                setCurrentPage('conflicts');
              }}
            />
          )}

          {currentPage === 'documents' && (
            <DocumentLibrary
              documents={documents}
              onUploadClick={() => setCurrentPage('upload')}
              onInspectDocument={(doc) => {
                setSelectedDocument(doc);
                setCurrentPage('versions');
              }}
              onDeleteDocument={handleDeleteDocument}
            />
          )}

          {currentPage === 'upload' && (
            <DocumentUpload
              workspaceId={activeWorkspaceId}
              onUploadSuccess={() => {
                loadWorkspaceData(activeWorkspaceId);
                setCurrentPage('documents');
              }}
              onCancel={() => setCurrentPage('documents')}
            />
          )}

          {currentPage === 'versions' && (
            <DocumentVersionManagement
              document={selectedDocument}
              documents={documents}
              onSelectDocument={setSelectedDocument}
              onNavigateToDiff={() => setCurrentPage('diff_viewer')}
            />
          )}

          {currentPage === 'conflicts' && (
            <ConflictInvestigation
              conflicts={conflicts}
              selectedConflictId={selectedConflictId}
              onReviewCompleted={() => loadWorkspaceData(activeWorkspaceId)}
            />
          )}

          {currentPage === 'diff_viewer' && (
            <SplitScreenEvidenceViewer documents={documents} />
          )}

          {currentPage === 'graph' && (
            <RuleRelationshipGraph workspaceId={activeWorkspaceId} />
          )}

          {currentPage === 'review_queue' && (
            <ReviewQueue
              conflicts={conflicts}
              onReviewSubmitted={() => loadWorkspaceData(activeWorkspaceId)}
            />
          )}

          {currentPage === 'audit' && (
            <AuditReports workspaceId={activeWorkspaceId} />
          )}
        </main>
      </div>

      {/* Create Workspace Modal */}
      {showWorkspaceModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded p-5 max-w-md w-full space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-semibold text-slate-100">Create Compliance Workspace</h3>
              <button onClick={() => setShowWorkspaceModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateWorkspace} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-300 block mb-1 font-medium">Workspace Name *</label>
                <input
                  type="text"
                  required
                  value={newWsName}
                  onChange={(e) => {
                    setNewWsName(e.target.value);
                    if (!newWsSlug) {
                      setNewWsSlug(e.target.value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''));
                    }
                  }}
                  placeholder="e.g. Vendor Sourcing & Procurement"
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-slate-200 focus:outline-none focus:border-slate-600"
                />
              </div>

              <div>
                <label className="text-slate-300 block mb-1 font-medium">Slug (URL safe) *</label>
                <input
                  type="text"
                  required
                  value={newWsSlug}
                  onChange={(e) => setNewWsSlug(e.target.value)}
                  placeholder="e.g. vendor-procurement"
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-slate-200 focus:outline-none focus:border-slate-600 font-mono"
                />
              </div>

              <div>
                <label className="text-slate-300 block mb-1 font-medium">Description (Optional)</label>
                <textarea
                  rows={2}
                  value={newWsDesc}
                  onChange={(e) => setNewWsDesc(e.target.value)}
                  placeholder="Departmental scope and compliance domain..."
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200 focus:outline-none focus:border-slate-600 resize-none"
                />
              </div>

              <div className="pt-2 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowWorkspaceModal(false)}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-3.5 py-1.5 bg-slate-100 hover:bg-white text-slate-900 rounded font-semibold"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
