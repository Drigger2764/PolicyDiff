import React from 'react';
import { BookOpen, Layers } from 'lucide-react';

interface HeaderProps {
  activeWorkspace?: string;
}

export const Header: React.FC<HeaderProps> = ({ activeWorkspace }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur px-6 py-4 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-indigo-600/20 text-indigo-400 rounded-lg border border-indigo-500/30">
          <Layers className="w-6 h-6" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold tracking-tight text-white">PolicyDiff</h1>
            <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800 font-medium">
              v0.1.0 Foundation
            </span>
          </div>
          <p className="text-xs text-slate-400">Policy Document Intelligence & Deontic Contradiction Engine</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {activeWorkspace && (
          <div className="flex items-center space-x-2 text-sm bg-slate-900 border border-slate-800 rounded-md px-3 py-1.5 text-slate-300">
            <BookOpen className="w-4 h-4 text-slate-400" />
            <span className="text-slate-400">Workspace:</span>
            <span className="font-semibold text-white">{activeWorkspace}</span>
          </div>
        )}
        <div className="flex items-center space-x-1.5 text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800/60 px-3 py-1 rounded-full">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Engine Online</span>
        </div>
      </div>
    </header>
  );
};
