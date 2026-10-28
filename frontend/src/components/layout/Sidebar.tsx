import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users2,
  FolderKanban,
  Video,
  CheckSquare,
  Scale,
  AlertOctagon,
  Boxes,
  Settings,
  Sparkles
} from 'lucide-react';
import { clsx } from 'clsx';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onClose }) => {
  const { user } = useAuth();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Clients', href: '/clients', icon: Users2 },
    { name: 'Projects', href: '/projects', icon: FolderKanban },
    { name: 'Meetings', href: '/meetings', icon: Video },
    { name: 'Tasks Board', href: '/tasks', icon: CheckSquare },
    { name: 'Decisions', href: '/decisions', icon: Scale },
    { name: 'Risks & Questions', href: '/risks-questions', icon: AlertOctagon },
    { name: 'Integrations', href: '/integrations', icon: Boxes },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-brand-950 text-slate-300 flex flex-col h-full border-r border-slate-800">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 gap-3 border-b border-brand-900 bg-brand-950/90">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-700 to-accent-500 flex items-center justify-center text-white shadow-md">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="font-bold text-base tracking-tight text-white block">MeetFlow AI</span>
          <span className="text-[10px] text-accent-100/70 tracking-widest uppercase font-semibold">Action Tracker</span>
        </div>
      </div>

      {/* Workspace Indicator */}
      <div className="px-5 py-3.5 border-b border-slate-800/80 bg-brand-900/30">
        <div className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">Workspace</div>
        <div className="text-xs font-medium text-white truncate mt-0.5">
          {user?.organization_id ? 'Enterprise Workspace' : 'My Team'}
        </div>
      </div>

      {/* Nav items */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.href}
              onClick={onClose}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-colors',
                  isActive
                    ? 'bg-brand-800 text-white shadow-sm font-semibold'
                    : 'text-slate-400 hover:text-white hover:bg-brand-900/60'
                )
              }
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {item.name}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer User Info */}
      <div className="p-4 border-t border-slate-800/80 bg-brand-950/60">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-brand-800 border border-brand-700 flex items-center justify-center text-xs font-bold text-accent-100">
            {user?.full_name?.charAt(0) || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-semibold text-white truncate">{user?.full_name || 'User'}</div>
            <div className="text-[10px] text-slate-400 truncate capitalize">{user?.role?.replace('_', ' ') || 'Member'}</div>
          </div>
        </div>
      </div>
    </aside>
  );
};

