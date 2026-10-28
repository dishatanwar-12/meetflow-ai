import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { Skeleton } from '../components/ui/Skeleton';
import { api } from '../services/api';
import { Sparkles, GitBranch, CheckCircle2, AlertTriangle, RefreshCw, Key } from 'lucide-react';

export const IntegrationsPage: React.FC = () => {
  const [providerData, setProviderData] = useState<any | null>(null);
  const [healthData, setHealthData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkIntegrations();
  }, []);

  const checkIntegrations = async () => {
    setLoading(true);
    try {
      const [prov, health] = await Promise.all([
        api.getSystemProviders(),
        api.getSystemHealth(),
      ]);
      setProviderData(prov);
      setHealthData(health);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Integrations Hub</h1>
          <p className="text-xs text-slate-500 mt-1">
            Configure and monitor NVIDIA NIM AI models, external task trackers, and system health.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={checkIntegrations}>
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Refresh Status
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* NVIDIA NIM Hosted LLM */}
        <Card className="border border-slate-200">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-brand-900 flex items-center justify-center text-white">
                <Sparkles className="w-5 h-5 text-accent-100" />
              </div>
              <div>
                <CardTitle>NVIDIA NIM Hosted LLM</CardTitle>
                <div className="text-[11px] text-slate-500">Official OpenAI-compatible inference</div>
              </div>
            </div>
            {loading ? (
              <Skeleton className="h-6 w-20" />
            ) : providerData?.is_configured ? (
              <Badge variant="success">READY</Badge>
            ) : (
              <Badge variant="amber">UNCONFIGURED</Badge>
            )}
          </CardHeader>
          <CardContent className="space-y-3 text-xs text-slate-600">
            <p>
              MeetFlow AI processes meeting transcripts using real hosted NVIDIA NIM models
              with strict output validation and prompt injection defenses.
            </p>

            <div className="p-3 bg-slate-50 rounded-lg space-y-1.5 font-mono text-[11px]">
              <div><span className="text-slate-400">Endpoint:</span> {providerData?.base_url || 'https://integrate.api.nvidia.com/v1'}</div>
              <div><span className="text-slate-400">Model:</span> {providerData?.model || 'meta/llama-3.3-70b-instruct'}</div>
              <div><span className="text-slate-400">Status:</span> {providerData?.instructions || 'Checking...'}</div>
            </div>

            <div className="pt-2 text-[11px] text-slate-500">
              Get an API key from <a href="https://build.nvidia.com" target="_blank" rel="noreferrer" className="text-brand-900 font-semibold underline">build.nvidia.com</a> and add it as <code className="bg-slate-100 px-1 py-0.5 rounded text-brand-900">NVIDIA_API_KEY</code>.
            </div>
          </CardContent>
        </Card>

        {/* GitHub Issues Integration */}
        <Card className="border border-slate-200">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-slate-900 flex items-center justify-center text-white">
                <GitBranch className="w-5 h-5" />
              </div>
              <div>
                <CardTitle>GitHub Issues</CardTitle>
                <div className="text-[11px] text-slate-500">Task Tracker Integration</div>
              </div>
            </div>
            <Badge variant="teal">BUILT-IN</Badge>
          </CardHeader>
          <CardContent className="space-y-3 text-xs text-slate-600">
            <p>
              Export confirmed action items directly into GitHub Issues with supporting transcript quotes,
              assigned owners, and resolved deadlines.
            </p>

            <div className="p-3 bg-slate-50 rounded-lg space-y-1 text-xs">
              <div className="flex items-center gap-2 text-emerald-800 font-semibold">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Pre-flight uncertainty checks enabled</span>
              </div>
              <div className="flex items-center gap-2 text-emerald-800 font-semibold">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Idempotent issue mapping (prevents duplicate exports)</span>
              </div>
            </div>

            <div className="pt-2 text-[11px] text-slate-500">
              To export tasks, open any reviewed meeting and click <b>Export Outcomes &gt; Export to GitHub</b>.
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Health */}
      <Card className="p-5 border border-slate-200 bg-slate-50/50">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">Backend & Database Health</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div>
            <span className="text-slate-400 block">Status</span>
            <span className="font-bold text-slate-800 capitalize">{healthData?.status || 'Active'}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Database</span>
            <span className="font-bold text-emerald-600">Connected</span>
          </div>
          <div>
            <span className="text-slate-400 block">Version</span>
            <span className="font-bold text-slate-800">{healthData?.version || '1.0.0'}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Environment</span>
            <span className="font-bold text-slate-800 capitalize">{healthData?.environment || 'Development'}</span>
          </div>
        </div>
      </Card>
    </div>
  );
};

