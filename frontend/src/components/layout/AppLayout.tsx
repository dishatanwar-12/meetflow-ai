import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { MeetingWizardModal } from '../meetings/MeetingWizardModal';

export const AppLayout: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [wizardOpen, setWizardOpen] = useState(false);

  useEffect(() => {
    const handleOpenWizard = () => setWizardOpen(true);
    window.addEventListener('open-new-meeting-wizard', handleOpenWizard);
    return () => window.removeEventListener('open-new-meeting-wizard', handleOpenWizard);
  }, []);

  return (
    <div className="flex h-screen bg-[#F8F9FD] text-slate-800 overflow-hidden font-sans">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex flex-shrink-0">
        <Sidebar onNewMeetingClick={() => setWizardOpen(true)} />
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          <div
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="relative flex-1 flex flex-col max-w-xs w-full bg-white z-10 shadow-2xl">
            <Sidebar
              onClose={() => setMobileMenuOpen(false)}
              onNewMeetingClick={() => {
                setMobileMenuOpen(false);
                setWizardOpen(true);
              }}
            />
          </div>
        </div>
      )}

      {/* Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Topbar onMenuClick={() => setMobileMenuOpen(true)} />
        <main className="flex-1 overflow-y-auto px-4 sm:px-6 md:px-8 pb-10 w-full max-w-[1400px] mx-auto">
          <Outlet />
        </main>
      </div>

      {/* Global Meeting Wizard Modal */}
      <MeetingWizardModal
        isOpen={wizardOpen}
        onClose={() => setWizardOpen(false)}
        onSuccess={(id) => {
          window.location.href = `/meetings/${id}`;
        }}
      />
    </div>
  );
};
