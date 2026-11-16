import React, { useState, useEffect } from 'react';
import { Share2, RefreshCw, Layers, AlertTriangle, ShieldCheck } from 'lucide-react';
import { fetchConflictGraph } from '../api/client';

interface RuleRelationshipGraphProps {
  workspaceId: string;
}

export const RuleRelationshipGraph: React.FC<RuleRelationshipGraphProps> = ({ workspaceId }) => {
  const [graphData, setGraphData] = useState<any>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadGraph();
  }, [workspaceId]);

  const loadGraph = async () => {
    try {
      setLoading(true);
      const data = await fetchConflictGraph(workspaceId);
      setGraphData(data);
      if (data?.nodes?.length > 0) {
        setSelectedNode(data.nodes[0]);
      }
      setLoading(false);
    } catch (e) {
      setLoading(false);
    }
  };

  const nodes = graphData?.nodes || [];
  const links = graphData?.links || [];
  const metrics = graphData?.metrics || {
    total_nodes: 0,
    total_edges: 0,
    connected_clusters: 0,
    circular_dependencies: 0,
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-semibold text-slate-100 tracking-tight">Rule Relationship Graph</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            NetworkX graph topology of policy dependency nodes and contradiction edges
          </p>
        </div>

        <button
          onClick={loadGraph}
          disabled={loading}
          className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded text-xs font-medium transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Topology</span>
        </button>
      </div>

      {/* Graph Metrics Summary Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-slate-900 border border-slate-800 p-3 rounded">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">Total Nodes</span>
          <span className="text-xl font-bold text-slate-100 block mt-0.5">{metrics.total_nodes}</span>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-3 rounded">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">Contradiction Edges</span>
          <span className="text-xl font-bold text-amber-400 block mt-0.5">{metrics.total_edges}</span>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-3 rounded">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">Connected Clusters</span>
          <span className="text-xl font-bold text-slate-100 block mt-0.5">{metrics.connected_clusters}</span>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-3 rounded">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">Circular Loops</span>
          <span className="text-xl font-bold text-emerald-400 block mt-0.5">{metrics.circular_dependencies}</span>
        </div>
      </div>

      {/* Main Graph Visualization Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Visual Graph View Area */}
        <div className="lg:col-span-8 bg-slate-900 border border-slate-800 rounded p-4 min-h-[500px] flex flex-col justify-between">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-xs text-slate-400">
            <span className="font-semibold uppercase tracking-wider text-[11px]">Visual Topology Plane</span>
            <div className="flex items-center space-x-3 text-[10px]">
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span>
                <span>Direct Contradiction</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                <span>Conditional / Exception</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-full bg-slate-500"></span>
                <span>Isolated Rule</span>
              </span>
            </div>
          </div>

          {nodes.length === 0 ? (
            <div className="my-auto text-center p-12 text-slate-400 text-xs">
              <Share2 className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <span>No policy rules currently indexed in graph topology.</span>
            </div>
          ) : (
            <div className="my-auto py-8">
              {/* Responsive SVG/HTML interactive node grid with connecting vectors */}
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                {nodes.map((node: any) => {
                  const isSelected = selectedNode?.id === node.id;
                  const hasConflict = links.some((l: any) => l.source === node.id || l.target === node.id);

                  return (
                    <button
                      key={node.id}
                      onClick={() => setSelectedNode(node)}
                      className={`p-3 rounded border text-left transition relative ${
                        isSelected
                          ? 'bg-slate-800 border-slate-400 shadow-md ring-1 ring-slate-400'
                          : hasConflict
                          ? 'bg-slate-950 border-amber-800/80 hover:border-amber-600'
                          : 'bg-slate-950 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-mono text-xs font-bold text-slate-200">{node.id}</span>
                        <span
                          className={`w-2 h-2 rounded-full ${
                            hasConflict ? 'bg-amber-400 animate-pulse' : 'bg-slate-600'
                          }`}
                        />
                      </div>
                      <div className="text-[11px] text-slate-300 font-medium truncate">{node.action}</div>
                      <div className="text-[10px] text-slate-400 truncate mt-0.5">{node.subject}</div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          <div className="text-[10px] text-slate-400 pt-2 border-t border-slate-800 flex items-center justify-between">
            <span>Directed Multigraph Model • NetworkX Analysis</span>
            <span>Click any node to inspect extracted properties</span>
          </div>
        </div>

        {/* Selected Node Properties Inspector */}
        <div className="lg:col-span-4 bg-slate-900 border border-slate-800 rounded p-4 space-y-3">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 border-b border-slate-800 pb-2">
            Node Inspector
          </h2>

          {selectedNode ? (
            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 block">Rule Identifier</span>
                <span className="font-mono font-bold text-slate-100 text-sm">{selectedNode.id}</span>
              </div>

              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 block">Governed Subject</span>
                <span className="text-slate-200 font-medium">{selectedNode.subject}</span>
              </div>

              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 block">Deontic Modality</span>
                <span className="font-mono text-slate-100 bg-slate-800 px-2 py-0.5 rounded inline-block mt-0.5 font-bold">
                  {selectedNode.obligation}
                </span>
              </div>

              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 block">Operative Action</span>
                <span className="text-slate-300 font-mono bg-slate-950 px-2 py-0.5 rounded inline-block mt-0.5">
                  {selectedNode.action}
                </span>
              </div>

              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 block">Source Document</span>
                <span className="text-slate-300">{selectedNode.document || 'Policy Document'}</span>
              </div>

              {/* Edge Connections for this node */}
              <div className="pt-2 border-t border-slate-800">
                <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">
                  Connected Conflicts (
                  {links.filter((l: any) => l.source === selectedNode.id || l.target === selectedNode.id).length}
                  )
                </span>
                <div className="space-y-1.5">
                  {links
                    .filter((l: any) => l.source === selectedNode.id || l.target === selectedNode.id)
                    .map((l: any, i: number) => (
                      <div key={i} className="p-2 bg-slate-950 rounded border border-slate-800 text-[11px] space-y-0.5">
                        <div className="text-amber-400 font-semibold">{l.category}</div>
                        <div className="text-slate-400 font-mono text-[10px]">
                          Target: {l.source === selectedNode.id ? l.target : l.source}
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center p-8 text-slate-400 text-xs">
              Select a node in the graph to view properties.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
