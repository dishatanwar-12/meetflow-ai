import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import { Alert } from '../components/ui/Alert';
import { Skeleton } from '../components/ui/Skeleton';
import { api } from '../services/api';
import { Client } from '../types';
import { Users2, Plus, Search, Globe, Mail, FolderKanban } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const ClientsPage: React.FC = () => {
  const { isPM } = useAuth();
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);

  // Form states
  const [name, setName] = useState('');
  const [orgName, setOrgName] = useState('');
  const [contactName, setContactName] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [industry, setIndustry] = useState('');
  const [website, setWebsite] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadClients();
  }, [search]);

  const loadClients = async () => {
    setLoading(true);
    try {
      const data = await api.getClients(search || undefined);
      setClients(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setSubmitting(true);
    setError(null);
    try {
      await api.createClient({
        name: name.trim(),
        organization_name: orgName.trim() || undefined,
        contact_name: contactName.trim() || undefined,
        contact_email: contactEmail.trim() || undefined,
        industry: industry.trim() || undefined,
        website: website.trim() || undefined,
        notes: notes.trim() || undefined,
      });
      setModalOpen(false);
      setName('');
      setOrgName('');
      setContactName('');
      setContactEmail('');
      setIndustry('');
      setWebsite('');
      setNotes('');
      loadClients();
    } catch (err: any) {
      setError(err.message || 'Failed to create client.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Clients</h1>
          <p className="text-xs text-slate-500 mt-1">Manage client accounts and their associated projects.</p>
        </div>
        {isPM && (
          <Button variant="primary" size="md" onClick={() => setModalOpen(true)}>
            <Plus className="w-4 h-4 mr-1.5" />
            Add Client
          </Button>
        )}
      </div>

      {/* Search Bar */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
        <input
          type="text"
          placeholder="Search by client name, organization or industry..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-brand-800 bg-white"
        />
      </div>

      {/* Clients Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Skeleton className="h-44 rounded-xl" />
          <Skeleton className="h-44 rounded-xl" />
          <Skeleton className="h-44 rounded-xl" />
        </div>
      ) : clients.length === 0 ? (
        <Card className="p-12 text-center text-slate-500">
          <Users2 className="w-12 h-12 mx-auto text-slate-400 mb-3" />
          <h3 className="text-sm font-semibold text-slate-800">No clients found</h3>
          <p className="text-xs text-slate-500 mt-1">Add your first client to start organizing projects.</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {clients.map((c) => (
            <Card key={c.id} className="p-5 flex flex-col justify-between hover:border-slate-300 transition-colors">
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">{c.name}</h3>
                    {c.organization_name && (
                      <p className="text-xs text-slate-500">{c.organization_name}</p>
                    )}
                  </div>
                  {c.industry && (
                    <span className="px-2 py-0.5 bg-slate-100 text-slate-700 rounded text-[11px] font-medium">
                      {c.industry}
                    </span>
                  )}
                </div>

                <div className="space-y-1.5 text-xs text-slate-600">
                  {c.contact_name && (
                    <p className="flex items-center gap-2">
                      <span className="text-slate-400 font-medium">Contact:</span>
                      <span className="font-semibold text-slate-800">{c.contact_name}</span>
                    </p>
                  )}
                  {c.contact_email && (
                    <p className="flex items-center gap-2">
                      <Mail className="w-3.5 h-3.5 text-slate-400" />
                      <a href={`mailto:${c.contact_email}`} className="text-brand-900 hover:underline">
                        {c.contact_email}
                      </a>
                    </p>
                  )}
                  {c.website && (
                    <p className="flex items-center gap-2">
                      <Globe className="w-3.5 h-3.5 text-slate-400" />
                      <a href={c.website} target="_blank" rel="noreferrer" className="text-brand-900 hover:underline truncate">
                        {c.website}
                      </a>
                    </p>
                  )}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span className="flex items-center gap-1.5 font-medium">
                  <FolderKanban className="w-3.5 h-3.5 text-slate-400" />
                  {c.projects_count || 0} Projects
                </span>
                <span className="text-[11px]">Added {new Date(c.created_at).toLocaleDateString()}</span>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Create New Client"
        description="Add a new client organization."
        maxWidth="md"
      >
        <form onSubmit={handleCreate} className="space-y-4">
          {error && <Alert type="error">{error}</Alert>}
          <Input label="Client Name *" value={name} onChange={(e) => setName(e.target.value)} required />
          <Input label="Organization / Division" value={orgName} onChange={(e) => setOrgName(e.target.value)} />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Contact Name" value={contactName} onChange={(e) => setContactName(e.target.value)} />
            <Input label="Contact Email" type="email" value={contactEmail} onChange={(e) => setContactEmail(e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Industry" value={industry} onChange={(e) => setIndustry(e.target.value)} />
            <Input label="Website" value={website} onChange={(e) => setWebsite(e.target.value)} />
          </div>
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <Button type="button" variant="outline" size="sm" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={submitting}>
              Save Client
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
