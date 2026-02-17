import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { CurrentUser, AuthPayload, AuthResponse } from '../types/user';
import { post } from '../utils/api';
import { storage } from '../utils/storage';

interface AuthContextType {
  user: CurrentUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: AuthPayload) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async (): Promise<void> => {
      try {
        const token = storage.getAccessToken();
        const storedUser = storage.getUser() as CurrentUser | null;

        if (token && storedUser) {
          if (!storage.isTokenExpired(token)) {
            setUser(storedUser);
          } else {
            storage.clear();
          }
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error);
        storage.clear();
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = useCallback(async (credentials: AuthPayload): Promise<void> => {
    try {
      const response = await post<AuthResponse>('/auth/login', credentials);
      if (response.data) {
        const { user: authUser, accessToken, refreshToken } = response.data;
        storage.setAccessToken(accessToken);
        storage.setRefreshToken(refreshToken);
        storage.setUser(authUser);
        setUser(authUser as CurrentUser);
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }, []);

  const logout = useCallback((): void => {
    storage.clear();
    setUser(null);
  }, []);

  const refreshUser = useCallback(async (): Promise<void> => {
    try {
      const storedUser = storage.getUser() as CurrentUser | null;
      if (storedUser) {
        setUser(storedUser);
      }
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
    refreshUser,
  };

  return React.createElement(AuthContext.Provider, { value }, children);
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
