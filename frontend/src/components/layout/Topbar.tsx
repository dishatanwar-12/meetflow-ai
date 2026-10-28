import React from 'react';
import { Menu, LogOut, Shield } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';

interface TopbarProps {
  onMenuClick: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({ onMenuClick }) => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-4 md:px-8 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="md:hidden p-2 rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-800"
          aria-label="Toggle mobile menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-600">Workspace</span>
          <span className="text-xs text-slate-300">/</span>
          <span className="text-xs font-medium text-slate-800 font-semibold">{user?.organization_id ? 'Enterprise' : 'Production'}</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {user?.role && (
          <Badge variant="default" className="text-[11px] uppercase tracking-wider font-semibold py-0.5">
            <Shield className="w-3 h-3 mr-1 inline" />
            {user.role.replace('_', ' ')}
          </Badge>
        )}

        <Button
          variant="outline"
          size="sm"
          onClick={logout}
          className="text-xs font-medium text-slate-600 hover:text-rose-600 hover:border-rose-200"
        >
          <LogOut className="w-3.5 h-3.5 mr-1.5" />
          Sign out
        </Button>
      </div>
    </header>
  );
};

