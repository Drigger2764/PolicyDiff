import React, { useState, useEffect } from 'react';
import { FileBarChart2, Download, Printer, RefreshCw, CheckCircle2, ShieldCheck, Cpu } from 'lucide-react';
import { fetchAuditReport, fetchEvaluationBenchmark } from '../api/client';

interface AuditReportsProps {
  workspaceId: string;
}

export const AuditReports: React.FC<AuditReportsProps> = ({ workspaceId }) => {
  const [report, setReport] = useState<any>(null);
  const [benchmark, setBenchmark] = useState<any>(null);
  const [loadingReport, setLoadingReport] = useState(false);
  const [runningBenchmark, setRunningBenchmark] = useState(false);

  useEffect(() => {
    loadReport();
  }, [workspaceId]);

  const loadReport = async () => {
    try {
      setLoadingReport(true);
      const data = await fetchAuditReport(workspaceId);
      setReport(data);
      setLoadingReport(false);
    } catch (e) {
      setLoadingReport(false);
    }
  };

  const runBenchmark = async () => {
    try {
      setRunningBenchmark(true);
      const data = await fetchEvaluationBenchmark();
      setBenchmark(data);
      setRunningBenchmark(false);
    } catch (e) {
      setRunningBenchmark(false);
    }
  };

  const handleExportJSON = () => {
    const exportData = {
      report,
      benchmark,
      exported_at: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `PolicyDiff_Audit_Report_${workspaceId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-semibold text-slate-100 tracking-tight">Audit & Evaluation Reports</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Executive compliance reporting, conflict statistics, and empirical NLP benchmark evaluation
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          <button
            onClick={() => window.print()}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-medium transition"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print View</span>
          </button>
          <button
            onClick={handleExportJSON}
            disabled={!report}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-slate-100 hover:bg-white text-slate-900 rounded text-xs font-semibold transition disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Report JSON</span>
          </button>
        </div>
      </div>

      {/* Compliance Overview Card */}
      {report && (
        <div className="bg-slate-900 border border-slate-800 rounded p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
                Workspace Compliance Audit Summary
              </h2>
              <span className="text-xs text-slate-400 font-mono mt-0.5 block">
                Target: {report.workspace?.name} ({report.workspace?.slug})
              </span>
            </div>
            <div className="text-right">
              <span className="text-xs text-slate-400 block font-medium">Compliance Resolution Rate</span>
              <span className="text-xl font-bold text-emerald-400">{report.statistics?.resolution_rate_percent}%</span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-950 p-3 rounded border border-slate-800">
              <span className="text-[10px] uppercase font-mono text-slate-400 block">Total Policies</span>
              <span className="text-lg font-bold text-slate-100">{report.statistics?.total_documents}</span>
            </div>
            <div className="bg-slate-950 p-3 rounded border border-slate-800">
              <span className="text-[10px] uppercase font-mono text-slate-400 block">Extracted Rules</span>
              <span className="text-lg font-bold text-slate-100">{report.statistics?.total_extracted_rules}</span>
            </div>
            <div className="bg-slate-950 p-3 rounded border border-slate-800">
              <span className="text-[10px] uppercase font-mono text-slate-400 block">Identified Conflicts</span>
              <span className="text-lg font-bold text-amber-400">{report.statistics?.total_conflicts_detected}</span>
            </div>
            <div className="bg-slate-950 p-3 rounded border border-slate-800">
              <span className="text-[10px] uppercase font-mono text-slate-400 block">Determinations Applied</span>
              <span className="text-lg font-bold text-emerald-400">
                {report.statistics?.resolved_conflicts + report.statistics?.dismissed_conflicts}
              </span>
            </div>
          </div>

          {/* Breakdown Tables */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-2">
                Conflicts by Category
              </span>
              <div className="bg-slate-950 rounded border border-slate-800 divide-y divide-slate-800/80 text-xs">
                {Object.entries(report.conflict_categories || {}).length === 0 ? (
                  <div className="p-3 text-slate-400">No conflicts categorized.</div>
                ) : (
                  Object.entries(report.conflict_categories || {}).map(([cat, count]: any) => (
                    <div key={cat} className="p-2.5 flex items-center justify-between">
                      <span className="text-slate-300 font-medium">{cat}</span>
                      <span className="font-mono text-slate-100 bg-slate-800 px-2 py-0.5 rounded">{count}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-2">
                Severity Distribution
              </span>
              <div className="bg-slate-950 rounded border border-slate-800 divide-y divide-slate-800/80 text-xs">
                {Object.entries(report.severity_distribution || {}).length === 0 ? (
                  <div className="p-3 text-slate-400">No severity metrics recorded.</div>
                ) : (
                  Object.entries(report.severity_distribution || {}).map(([sev, count]: any) => (
                    <div key={sev} className="p-2.5 flex items-center justify-between">
                      <span className="text-slate-300 font-medium">{sev}</span>
                      <span className="font-mono text-slate-100 bg-slate-800 px-2 py-0.5 rounded">{count}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empirical NLP Benchmark Section */}
      <div className="bg-slate-900 border border-slate-800 rounded p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <div>
              <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
                Empirical Engine Evaluation Benchmark
              </h2>
              <span className="text-xs text-slate-400 mt-0.5 block">
                Evaluates rule extraction and contradiction detection against 516 reproducible synthetic policy rules
              </span>
            </div>
          </div>

          <button
            onClick={runBenchmark}
            disabled={runningBenchmark}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded text-xs font-medium transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${runningBenchmark ? 'animate-spin' : ''}`} />
            <span>{runningBenchmark ? 'Executing Benchmark...' : 'Run Live Benchmark'}</span>
          </button>
        </div>

        {benchmark ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="bg-slate-950 p-3 rounded border border-slate-800">
                <span className="text-slate-400 block font-mono text-[10px]">CORPUS SIZE</span>
                <span className="text-base font-bold text-slate-100">
                  {benchmark.dataset_summary?.total_synthetic_rules} Rules
                </span>
              </div>
              <div className="bg-slate-950 p-3 rounded border border-slate-800">
                <span className="text-slate-400 block font-mono text-[10px]">DOMAINS COVERED</span>
                <span className="text-base font-bold text-slate-100">
                  {benchmark.dataset_summary?.domains} Enterprise Domains
                </span>
              </div>
              <div className="bg-slate-950 p-3 rounded border border-slate-800">
                <span className="text-slate-400 block font-mono text-[10px]">PLANTED CONFLICTS</span>
                <span className="text-base font-bold text-amber-400">
                  {benchmark.dataset_summary?.planted_ground_truth_conflicts} Pairs
                </span>
              </div>
              <div className="bg-slate-950 p-3 rounded border border-slate-800">
                <span className="text-slate-400 block font-mono text-[10px]">EXECUTION TIME</span>
                <span className="text-base font-bold text-emerald-400 font-mono">
                  {benchmark.dataset_summary?.execution_time_seconds}s
                </span>
              </div>
            </div>

            {/* Metrics Comparison Table */}
            <div className="bg-slate-950 rounded border border-slate-800 overflow-hidden text-xs">
              <table className="w-full text-left">
                <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] font-semibold border-b border-slate-800">
                  <tr>
                    <th className="py-2.5 px-4">Evaluation Track</th>
                    <th className="py-2.5 px-4">Precision</th>
                    <th className="py-2.5 px-4">Recall</th>
                    <th className="py-2.5 px-4">F1 Score</th>
                    <th className="py-2.5 px-4">False Positives</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/80 font-mono">
                  <tr>
                    <td className="py-2.5 px-4 font-sans font-semibold text-slate-200">
                      Rule Extraction Engine (Deontic Parser)
                    </td>
                    <td className="py-2.5 px-4 text-emerald-400">
                      {(benchmark.rule_extraction_metrics?.precision * 100).toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-4 text-emerald-400">
                      {(benchmark.rule_extraction_metrics?.recall * 100).toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-4 text-emerald-400 font-bold">
                      {(benchmark.rule_extraction_metrics?.f1_score * 100).toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">
                      {benchmark.rule_extraction_metrics?.false_positives}
                    </td>
                  </tr>
                  <tr className="bg-slate-900/40">
                    <td className="py-2.5 px-4 font-sans font-semibold text-indigo-300">
                      PolicyDiff Contradiction Detection (Deontic Matrix)
                    </td>
                    <td className="py-2.5 px-4 text-indigo-300 font-bold">
                      {(benchmark.conflict_detection_metrics?.precision * 100).toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-4 text-emerald-400 font-bold">
                      {(benchmark.conflict_detection_metrics?.recall * 100).toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-4 text-emerald-400 font-bold">
                      {(benchmark.conflict_detection_metrics?.f1_score * 100).toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">
                      {benchmark.conflict_detection_metrics?.false_positives}
                    </td>
                  </tr>
                  <tr className="opacity-75">
                    <td className="py-2.5 px-4 font-sans text-slate-400">
                      Naive Similarity Overlap Baseline
                    </td>
                    <td className="py-2.5 px-4 text-red-400">
                      {(benchmark.baseline_comparison?.precision * 100).toFixed(2)}%
                    </td>
                    <td className="py-2.5 px-4 text-amber-400">
                      {(benchmark.baseline_comparison?.recall * 100).toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-4 text-red-400">
                      {(benchmark.baseline_comparison?.f1_score * 100).toFixed(2)}%
                    </td>
                    <td className="py-2.5 px-4 text-red-400">
                      {benchmark.baseline_comparison?.false_positives}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="p-8 text-center text-slate-400 text-xs">
            Click "Run Live Benchmark" to execute the synthetic 516-rule evaluation pipeline.
          </div>
        )}
      </div>
    </div>
  );
};
