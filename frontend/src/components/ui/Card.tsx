import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export const Card: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, className, ...props }) => (
  <div
    className={twMerge(clsx('bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden', className))}
    {...props}
  >
    {children}
  </div>
);

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, className, ...props }) => (
  <div className={twMerge(clsx('px-6 py-4 border-b border-slate-100 flex items-center justify-between', className))} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ children, className, ...props }) => (
  <h3 className={twMerge(clsx('text-base font-semibold text-slate-900', className))} {...props}>
    {children}
  </h3>
);

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, className, ...props }) => (
  <div className={twMerge(clsx('p-6', className))} {...props}>
    {children}
  </div>
);

