import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { Sparkles } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [organizationName, setOrganizationName] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName || !email || !organizationName || !password) return;

    setLoading(true);
    setError(null);
    try {
      await register({
        full_name: fullName.trim(),
        email: email.trim().toLowerCase(),
        organization_name: organizationName.trim(),
        password,
      });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="w-12 h-12 rounded-2xl bg-brand-950 mx-auto flex items-center justify-center text-white shadow-lg mb-3">
          <Sparkles className="w-6 h-6 text-accent-100" />
        </div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">Create your MeetFlow account</h2>
        <p className="mt-1 text-xs text-slate-500">First user in organization is automatically assigned Admin role.</p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 sm:px-10 shadow-sm rounded-2xl border border-slate-200 space-y-6">
          {error && <Alert type="error">{error}</Alert>}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Full Name *"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Sarah Connor"
              required
            />

            <Input
              label="Company / Organization Name *"
              value={organizationName}
              onChange={(e) => setOrganizationName(e.target.value)}
              placeholder="Initech Global"
              required
            />

            <Input
              label="Work Email *"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="sarah@initech.com"
              required
            />

            <Input
              label="Password *"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              helperText="Minimum 8 characters."
              required
            />

            <Button type="submit" variant="primary" size="md" className="w-full" isLoading={loading}>
              Create Account
            </Button>
          </form>

          <div className="pt-4 border-t border-slate-100 text-center">
            <p className="text-xs text-slate-500">
              Already registered?{' '}
              <Link to="/login" className="font-semibold text-brand-900 hover:underline">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
