import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useAuth } from '../context/AuthContext';
import { Shield, Key, Lock, User, Building } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Workspace Settings</h1>
        <p className="text-xs text-slate-500 mt-1">
          Review profile, organization configuration, and security & privacy controls.
        </p>
      </div>

      {/* User Profile */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="w-4 h-4 text-brand-900" /> User Profile
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <span className="text-slate-400 block font-medium">Full Name</span>
              <span className="font-semibold text-slate-900 text-sm">{user?.full_name}</span>
            </div>
            <div>
              <span className="text-slate-400 block font-medium">Email Address</span>
              <span className="font-semibold text-slate-900 text-sm">{user?.email}</span>
            </div>
            <div>
              <span className="text-slate-400 block font-medium">Assigned Role</span>
              <Badge variant="default" className="mt-1">{user?.role?.toUpperCase()}</Badge>
            </div>
            <div>
              <span className="text-slate-400 block font-medium">Account Status</span>
              <span className="font-semibold text-emerald-600">Active</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security & Privacy */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-brand-900" /> Security & Privacy Policies
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-xs text-slate-600 leading-relaxed">
          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
            <h4 className="font-bold text-slate-800">Transcript Confidentiality & AI Processing</h4>
            <p>
              When an AI analysis run is initiated, transcript notes are transmitted exclusively via encrypted
              HTTPS to the configured NVIDIA NIM hosted inference endpoint (<code>https://integrate.api.nvidia.com/v1</code>).
            </p>
            <p>
              Transcripts are treated as untrusted user content and isolated within system boundary delimiters.
              NVIDIA NIM endpoints process requests in real-time server-side.
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
            <h4 className="font-bold text-slate-800">Credential Rotation</h4>
            <p>
              API keys and JWT secrets are stored server-side only in environment variables and never bundled
              into client code. To rotate credentials, update <code>NVIDIA_API_KEY</code> or <code>JWT_SECRET_KEY</code> in
              your deployment environment and restart the backend service.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

