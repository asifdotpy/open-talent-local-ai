import React from 'react';
import { cn } from '../lib/utils';

export const Card: React.FC<{ className?: string; children: React.ReactNode } & React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => (
  <div className={cn('bg-white rounded-lg shadow p-6', className)} {...props}>
    {children}
  </div>
);
