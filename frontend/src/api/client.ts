import {
  Workspace,
  Document,
  DocumentVersion,
  ExtractedSection,
  ConflictFinding,
  ReviewDecision,
  ReviewDecisionType,
} from '../types';

const API_BASE = '/api/v1';

export async function fetchHealth(): Promise<{ status: string; service: string }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchWorkspaces(): Promise<Workspace[]> {
  const res = await fetch(`${API_BASE}/workspaces/`);
  if (!res.ok) throw new Error('Failed to fetch workspaces');
  return res.json();
}

export async function createWorkspace(data: { name: string; slug: string; description?: string }): Promise<Workspace> {
  const res = await fetch(`${API_BASE}/workspaces/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to create workspace');
  }
  return res.json();
}

export async function fetchDocuments(workspaceId?: string): Promise<Document[]> {
  const url = workspaceId ? `${API_BASE}/documents/?workspace_id=${workspaceId}` : `${API_BASE}/documents/`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
}

export async function uploadDocument(formData: FormData): Promise<Document> {
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to upload document');
  }
  return res.json();
}

export async function deleteDocument(documentId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete document');
}

export async function fetchDocumentVersions(documentId: string): Promise<DocumentVersion[]> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/versions`);
  if (!res.ok) throw new Error('Failed to fetch document versions');
  return res.json();
}

export async function fetchVersionSections(versionId: string): Promise<ExtractedSection[]> {
  const res = await fetch(`${API_BASE}/documents/versions/${versionId}/sections`);
  if (!res.ok) throw new Error('Failed to fetch document sections');
  return res.json();
}

export async function fetchConflicts(
  workspaceId?: string,
  category?: string,
  status?: string
): Promise<ConflictFinding[]> {
  const params = new URLSearchParams();
  if (workspaceId) params.append('workspace_id', workspaceId);
  if (category && category !== 'ALL') params.append('category', category);
  if (status && status !== 'ALL') params.append('status_filter', status);

  const res = await fetch(`${API_BASE}/conflicts/?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch conflicts');
  return res.json();
}

export async function triggerConflictDetection(workspaceId: string): Promise<ConflictFinding[]> {
  const res = await fetch(`${API_BASE}/conflicts/detect?workspace_id=${workspaceId}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to run conflict detection');
  return res.json();
}

export async function fetchConflictGraph(workspaceId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/conflicts/graph?workspace_id=${workspaceId}`);
  if (!res.ok) throw new Error('Failed to fetch conflict graph');
  return res.json();
}

export async function submitReview(
  conflictId: string,
  decision: ReviewDecisionType,
  notes?: string,
  actionTaken?: string
): Promise<ReviewDecision> {
  const res = await fetch(`${API_BASE}/conflicts/${conflictId}/review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      conflict_id: conflictId,
      decision,
      notes,
      action_taken: actionTaken,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to submit review');
  }
  return res.json();
}

export async function fetchAuditReport(workspaceId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/audit/report?workspace_id=${workspaceId}`);
  if (!res.ok) throw new Error('Failed to fetch audit report');
  return res.json();
}

export async function fetchEvaluationBenchmark(): Promise<any> {
  const res = await fetch(`${API_BASE}/audit/benchmark`);
  if (!res.ok) throw new Error('Failed to fetch benchmark');
  return res.json();
}
