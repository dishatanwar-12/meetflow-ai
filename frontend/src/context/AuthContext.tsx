import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (data: { email: string; password: string; full_name: string; organization_name: string }) => Promise<void>;
  logout: () => void;
  isAdmin: boolean;
  isPM: boolean;
  canEdit: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('meetflow_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('meetflow_token');
      if (storedToken) {
        try {
          const profile = await api.getCurrentUser();
          setUser(profile);
        } catch {
          localStorage.removeItem('meetflow_token');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email: string, pass: string) => {
    const res = await api.login(email, pass);
    localStorage.setItem('meetflow_token', res.access_token);
    setToken(res.access_token);
    setUser(res.user);
  };

  const register = async (data: { email: string; password: string; full_name: string; organization_name: string }) => {
    const res = await api.register(data);
    localStorage.setItem('meetflow_token', res.access_token);
    setToken(res.access_token);
    setUser(res.user);
  };

  const logout = () => {
    localStorage.removeItem('meetflow_token');
    setToken(null);
    setUser(null);
    window.location.href = '/login';
  };

  const isAdmin = user?.role === 'admin';
  const isPM = isAdmin || user?.role === 'project_manager';
  const canEdit = isPM || user?.role === 'member';

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout, isAdmin, isPM, canEdit }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

