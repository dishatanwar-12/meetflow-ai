import React, { useState, useRef, useEffect } from 'react';
import { Search, Bell, ChevronDown, Menu, LogOut, Shield, User as UserIcon } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

interface TopbarProps {
  onMenuClick: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({ onMenuClick }) => {
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  // Listen for ⌘K or Ctrl+K shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && searchQuery.trim()) {
      navigate(`/tasks?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const getInitials = (name?: string) => {
    if (!name) return 'AA';
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return parts[0].slice(0, 2).toUpperCase();
  };

  const displayName = user?.full_name || 'Alice Admin';
  const initials = getInitials(user?.full_name);

  return (
    <header className="h-20 bg-transparent px-4 sm:px-6 md:px-8 flex items-center justify-between sticky top-0 z-30 select-none">
      {/* Left / Search section */}
      <div className="flex items-center gap-3 flex-1 max-w-xl">
        <button
          onClick={onMenuClick}
          className="md:hidden p-2 rounded-xl text-slate-500 hover:bg-white hover:text-slate-800 transition-colors"
          aria-label="Toggle mobile menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="relative w-full max-w-md">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
            <Search className="w-4 h-4 text-slate-400" />
          </div>
          <input
            ref={inputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleSearchKeyDown}
            placeholder="Search meetings, tasks, or keywords..."
            className="w-full pl-10 pr-14 py-2 text-xs sm:text-sm text-slate-800 bg-white placeholder-slate-400 rounded-full border border-slate-100 shadow-[0_2px_10px_-2px_rgba(0,0,0,0.03)] focus:outline-none focus:ring-2 focus:ring-[#6C52EE]/20 focus:border-[#6C52EE] transition-all"
          />
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <kbd className="inline-flex items-center px-1.5 py-0.5 text-[10px] font-mono font-medium text-slate-400 bg-slate-50 border border-slate-200/80 rounded-md">
              ⌘ K
            </kbd>
          </div>
        </div>
      </div>

      {/* Right Actions section */}
      <div className="flex items-center gap-3.5 sm:gap-4">
        {/* Notification Bell in White Circle */}
        <button
          type="button"
          aria-label="Notifications"
          className="relative w-9 h-9 rounded-full bg-white border border-slate-100 shadow-[0_2px_8px_-2px_rgba(0,0,0,0.03)] flex items-center justify-center text-slate-500 hover:text-slate-800 transition-all"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full ring-2 ring-white" />
        </button>

        {/* User Profile dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2.5 pl-1 pr-2 py-1 rounded-full hover:bg-white transition-all"
          >
            <div className="w-9 h-9 rounded-full bg-[#181A2A] text-white flex items-center justify-center text-xs font-semibold shadow-sm">
              {initials}
            </div>
            <span className="hidden sm:inline-block text-xs font-semibold text-slate-800">
              {displayName}
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {/* Dropdown Menu */}
          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-xl border border-slate-100 py-2 z-50 animate-in fade-in slide-in-from-top-1 duration-150">
              <div className="px-4 py-2 border-b border-slate-100">
                <div className="text-xs font-bold text-slate-900">{displayName}</div>
                <div className="text-[11px] text-slate-500 truncate">{user?.email}</div>
                {user?.role && (
                  <div className="mt-1">
                    <span className="inline-flex items-center text-[10px] font-semibold text-[#6C52EE] bg-[#F0EBFE] px-2 py-0.5 rounded-full uppercase tracking-wider">
                      <Shield className="w-2.5 h-2.5 mr-1" />
                      {user.role.replace('_', ' ')}
                    </span>
                  </div>
                )}
              </div>

              <div className="py-1">
                <button
                  onClick={() => {
                    setDropdownOpen(false);
                    navigate('/settings');
                  }}
                  className="w-full text-left px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 flex items-center gap-2"
                >
                  <UserIcon className="w-3.5 h-3.5 text-slate-400" />
                  Account Settings
                </button>
              </div>

              <div className="border-t border-slate-100 pt-1">
                <button
                  onClick={() => {
                    setDropdownOpen(false);
                    logout();
                  }}
                  className="w-full text-left px-4 py-2 text-xs font-medium text-rose-600 hover:bg-rose-50 flex items-center gap-2"
                >
                  <LogOut className="w-3.5 h-3.5 text-rose-500" />
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
