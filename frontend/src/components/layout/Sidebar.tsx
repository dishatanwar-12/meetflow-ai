import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Home,
  PlusSquare,
  CalendarDays,
  CheckSquare,
  Download,
  Settings,
  Folder,
  Users2,
  Lightbulb,
  ArrowRight
} from 'lucide-react';
import { clsx } from 'clsx';
import { MeetingFlowLogo } from '../common/MeetingFlowLogo';
import { GlowingWavesGraphic } from '../common/BotanicalLeaves';

interface SidebarProps {
  onClose?: () => void;
  onNewMeetingClick?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onClose, onNewMeetingClick }) => {
  const primaryNavigation = [
    { name: 'Home', href: '/dashboard', icon: Home },
    { name: 'New Meeting', href: '#new-meeting', icon: PlusSquare, isAction: true },
    { name: 'Meetings', href: '/meetings', icon: CalendarDays },
    { name: 'Action Tracker', href: '/tasks', icon: CheckSquare },
    { name: 'Export', href: '/integrations', icon: Download },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const secondaryNavigation = [
    { name: 'Projects', href: '/projects', icon: Folder },
    { name: 'Clients', href: '/clients', icon: Users2 },
    { name: 'Decisions', href: '/decisions', icon: Lightbulb },
  ];

  return (
    <aside className="w-64 bg-[#0A0C18] text-slate-400 flex flex-col h-full border-r border-slate-900 select-none">
      {/* Brand Header */}
      <div className="h-20 flex items-center px-5 gap-3">
        <MeetingFlowLogo className="w-8 h-8 flex-shrink-0" />
        <div className="min-w-0">
          <span className="font-bold text-base tracking-tight text-white block leading-tight">MeetingFlow</span>
          <span className="text-[11px] text-slate-500 font-normal truncate block mt-0.5">From Conversations to Action</span>
        </div>
      </div>

      {/* Main Nav items */}
      <nav className="flex-1 px-3.5 py-2 space-y-1 overflow-y-auto">
        {primaryNavigation.map((item) => {
          const Icon = item.icon;
          if (item.isAction) {
            return (
              <button
                key={item.name}
                type="button"
                onClick={() => {
                  if (onClose) onClose();
                  if (onNewMeetingClick) onNewMeetingClick();
                  else {
                    window.dispatchEvent(new CustomEvent('open-new-meeting-wizard'));
                  }
                }}
                className="w-full flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-sm font-medium text-slate-400 hover:text-white hover:bg-white/5 transition-all text-left group"
              >
                <Icon className="w-4 h-4 text-slate-400 group-hover:text-white transition-colors" />
                <span>{item.name}</span>
              </button>
            );
          }

          return (
            <NavLink
              key={item.name}
              to={item.href}
              onClick={onClose}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all group',
                  isActive
                    ? 'bg-gradient-to-r from-[#6366F1] to-[#4F46E5] text-white shadow-[0_4px_16px_rgba(99,102,241,0.3)]'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    className={clsx(
                      'w-4 h-4 transition-colors',
                      isActive ? 'text-white' : 'text-slate-400 group-hover:text-white'
                    )}
                  />
                  <span>{item.name}</span>
                </>
              )}
            </NavLink>
          );
        })}

        {/* Divider */}
        <div className="pt-3 pb-2 px-3">
          <div className="h-px bg-slate-800/80" />
        </div>

        {secondaryNavigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.href}
              onClick={onClose}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3.5 px-3.5 py-2 rounded-xl text-xs font-medium transition-all group',
                  isActive
                    ? 'bg-gradient-to-r from-[#6366F1] to-[#4F46E5] text-white shadow-[0_4px_16px_rgba(99,102,241,0.3)]'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    className={clsx(
                      'w-4 h-4 transition-colors',
                      isActive ? 'text-white' : 'text-slate-500 group-hover:text-white'
                    )}
                  />
                  <span>{item.name}</span>
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Promotion Card */}
      <div className="p-3.5">
        <div className="bg-[#131528] border border-slate-800/80 rounded-2xl p-4 relative overflow-hidden shadow-lg group cursor-pointer">
          {/* Glowing Wavy Graphic in the Background */}
          <GlowingWavesGraphic className="absolute -bottom-2 -left-4 -right-4 h-24 w-[120%] pointer-events-none opacity-70" />

          <div className="relative z-10 pr-6">
            <div className="font-bold text-white text-xs sm:text-[13px] leading-snug">
              Better meetings. <br />
              More action.
            </div>
            <div className="text-[11px] text-slate-400 mt-1 leading-relaxed font-normal">
              Turn your conversations <br className="hidden sm:inline" /> into clear next steps.
            </div>
          </div>

          <button
            type="button"
            onClick={() => {
              if (onNewMeetingClick) onNewMeetingClick();
              else {
                window.dispatchEvent(new CustomEvent('open-new-meeting-wizard'));
              }
            }}
            className="w-7 h-7 rounded-lg bg-slate-800/90 group-hover:bg-[#6366F1] text-white flex items-center justify-center transition-all absolute bottom-3.5 right-3.5 z-10 shadow-sm"
            aria-label="Create meeting action"
          >
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
};
