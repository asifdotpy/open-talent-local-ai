import React, { createContext, useContext, useMemo, ReactNode } from 'react';
import '../app';
import { container } from '../app';

type ContainerType = typeof container;

const AppContext = createContext<ContainerType | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const value = useMemo(() => container, []);
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContainer(): ContainerType {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useAppContainer must be used within AppProvider');
  return ctx;
}
