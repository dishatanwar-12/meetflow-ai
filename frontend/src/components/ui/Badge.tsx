import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'neutral' | 'success' | 'warning' | 'danger' | 'info' | 'teal' | 'amber' | 'purple';
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
  const baseStyles = 'inline-flex items-center font-medium rounded-full border transition-colors';

  const variants = {
    default: 'bg-[#F0EBFE] text-[#6C52EE] border-purple-100',
    purple: 'bg-[#F0EBFE] text-[#6C52EE] border-purple-100',
    neutral: 'bg-slate-100 text-slate-700 border-slate-200/80',
    success: 'bg-[#ECFDF5] text-[#059669] border-emerald-100/60',
    warning: 'bg-[#FFFBEB] text-[#D97706] border-amber-200/60',
    amber: 'bg-[#FFFBEB] text-[#D97706] border-amber-200/60',
    danger: 'bg-[#FFF1F2] text-[#E11D48] border-rose-200/60',
    info: 'bg-[#EFF6FF] text-[#2563EB] border-blue-200/60',
    teal: 'bg-[#ECFDF5] text-[#059669] border-teal-200/60',
  };

  const sizes = {
    sm: 'text-[11px] px-2 py-0.5 leading-4 font-semibold',
    md: 'text-xs px-2.5 py-1 leading-4 font-semibold',
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
