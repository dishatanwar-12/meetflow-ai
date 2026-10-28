import React from 'react';
import { AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';
import { clsx } from 'clsx';

interface AlertProps {
  type?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  type = 'info',
  title,
  children,
  className,
}) => {
  const styles = {
    info: {
      bg: 'bg-sky-50 border-sky-200 text-sky-900',
      icon: <Info className="h-5 w-5 text-sky-600 flex-shrink-0" />,
    },
    success: {
      bg: 'bg-emerald-50 border-emerald-200 text-emerald-900',
      icon: <CheckCircle className="h-5 w-5 text-emerald-600 flex-shrink-0" />,
    },
    warning: {
      bg: 'bg-amber-50 border-amber-200 text-amber-900',
      icon: <AlertTriangle className="h-5 w-5 text-amber-600 flex-shrink-0" />,
    },
    error: {
      bg: 'bg-rose-50 border-rose-200 text-rose-900',
      icon: <AlertCircle className="h-5 w-5 text-rose-600 flex-shrink-0" />,
    },
  }[type];

  return (
    <div className={clsx('flex items-start gap-3 p-4 rounded-xl border text-sm', styles.bg, className)}>
      {styles.icon}
      <div className="flex-1">
        {title && <h4 className="font-semibold mb-0.5">{title}</h4>}
        <div className="text-xs leading-relaxed opacity-90">{children}</div>
      </div>
    </div>
  );
};

