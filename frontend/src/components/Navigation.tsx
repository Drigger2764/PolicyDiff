import React from 'react';
import {
  LayoutDashboard,
  FileText,
  UploadCloud,
  History,
  AlertTriangle,
  Columns,
  Share2,
  CheckSquare,
  FileBarChart2,
  FolderGit2,
} from 'lucide-react';
import { Workspace } from '../types';

export type PageId =
  | 'dashboard'
  | 'documents'
  | 'upload'
  | 'versions'
  | 'conflicts'
  | 'diff_viewer'
  | 'graph'
  | 'review_queue'
  | 'audit';

interface NavigationProps {
  currentPage: PageId;
  onSelectPage: (page: PageId) => void;
  workspaces: Workspace[];
  activeWorkspaceId?: string;
  onSelectWorkspace: (id: string) => void;
  onOpenCreateWorkspace: () => void;
  pendingCount?: number;
}

export const Navigation: React.FC<NavigationProps> = ({
  currentPage,
  onSelectPage,
  workspaces,
  activeWorkspaceId,
  onSelectWorkspace,
  onOpenCreateWorkspace,
  pendingCount = 0,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'documents', label: 'Document Library', icon: FileText },
    { id: 'upload', label: 'Upload Policy', icon: UploadCloud },
    { id: 'versions', label: 'Version History', icon: History },
    { id: 'conflicts', label: 'Conflict Investigation', icon: AlertTriangle },
    { id: 'diff_viewer', label: 'Split-Screen Evidence', icon: Columns },
    { id: 'graph', label: 'Rule Relationship Graph', icon: Share2 },
    {
      id: 'review_queue',
      label: 'Review Queue',
      icon: CheckSquare,
      badge: pendingCount > 0 ? pendingCount : undefined,
    },
    { id: 'audit', label: 'Audit & Evaluation', icon: FileBarChart2 },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0 h-screen sticky top-0">
      {/* Brand & Workspace Selector */}
      <div className="p-4 border-b border-slate-800">
        <div className="flex items-center space-x-2.5 mb-3">
          <div className="w-7 h-7 bg-slate-800 border border-slate-700 rounded flex items-center justify-center text-slate-100 font-bold text-sm tracking-wider">
            PD
          </div>
          <div>
            <span className="font-semibold text-slate-100 text-sm tracking-tight block">PolicyDiff</span>
            <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 block">Enterprise Intelligence</span>
          </div>
        </div>

        {/* Workspace select */}
        <div className="space-y-1">
          <label className="text-[11px] font-medium text-slate-400 block">Workspace</label>
          <div className="flex items-center space-x-1.5">
            <select
              value={activeWorkspaceId || ''}
              onChange={(e) => onSelectWorkspace(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600"
            >
              {workspaces.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.name}
                </option>
              ))}
            </select>
            <button
              onClick={onOpenCreateWorkspace}
              title="Add Workspace"
              className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 shrink-0 text-xs"
            >
              +
            </button>
          </div>
        </div>
      </div>

      {/* Nav Menu Items */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 px-3 py-1">
          Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectPage(item.id as PageId)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded text-xs font-medium transition ${
                isActive
                  ? 'bg-slate-800 text-white font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <div className="flex items-center space-x-2.5 truncate">
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-slate-100' : 'text-slate-400'}`} />
                <span className="truncate">{item.label}</span>
              </div>
              {item.badge !== undefined && (
                <span className="ml-2 px-1.5 py-0.5 rounded-full text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer System Status */}
      <div className="p-3 border-t border-slate-800 text-xs text-slate-400 bg-slate-950/50">
        <div className="flex items-center justify-between">
          <span className="text-[11px]">Engine Status</span>
          <span className="flex items-center space-x-1 text-[11px] text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            <span>Online</span>
          </span>
        </div>
        <div className="text-[10px] text-slate-400 mt-1 font-mono">v0.1.0 • Enterprise Core</div>
      </div>
    </aside>
  );
};
