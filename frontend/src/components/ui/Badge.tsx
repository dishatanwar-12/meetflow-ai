import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'neutral' | 'success' | 'warning' | 'danger' | 'info' | 'teal' | 'amber';
  size?: 'sm' | 'md';
  className?: string;
  title?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  className,
  title,
}) => {
  const baseStyles = 'inline-flex items-center font-medium rounded-md border';

  const variants = {
    default: 'bg-brand-50 text-brand-900 border-brand-200',
    neutral: 'bg-slate-50 text-slate-700 border-slate-200',
    success: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    warning: 'bg-amber-50 text-amber-900 border-amber-300',
    amber: 'bg-amber-50 text-amber-900 border-amber-300',
    danger: 'bg-rose-50 text-rose-800 border-rose-200',
    info: 'bg-sky-50 text-sky-800 border-sky-200',
    teal: 'bg-teal-50 text-teal-800 border-teal-200',
  };

  const sizes = {
    sm: 'text-xs px-2 py-0.5 leading-4',
    md: 'text-xs px-2.5 py-1 leading-4',
  };

  return (
    <span
      title={title}
      className={twMerge(clsx(baseStyles, variants[variant], sizes[size], className))}
    >
      {children}
    </span>
  );
};

