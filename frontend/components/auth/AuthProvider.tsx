'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import { ApiError, apiRequest } from '@/lib/api';

export type CurrentUser = {
  id: string;
  email: string;
  username: string;
  is_active?: boolean;
  phone?: {
    phone_number: string;
    is_verified: boolean;
    verified_at: string | null;
  } | null;
};

type CurrentUserResponse = {
  user: CurrentUser;
};

type AuthContextValue = {
  user: CurrentUser | null;
  isAuthenticated: boolean | null;
  isLoading: boolean;
  refreshAuth: () => Promise<void>;
};

const AuthContext =
  createContext<AuthContextValue | undefined>(
    undefined,
  );

type AuthProviderProps = {
  children: React.ReactNode;
};

export default function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] =
    useState<CurrentUser | null>(null);

  const [isAuthenticated, setIsAuthenticated] =
    useState<boolean | null>(null);

  const [isLoading, setIsLoading] =
    useState(true);

  const refreshAuth = useCallback(async () => {
    setIsLoading(true);

    try {
      const data =
        await apiRequest<CurrentUserResponse>(
          '/api/accounts/me/',
        );

      setUser(data.user);
      setIsAuthenticated(true);
    } catch (error) {
      if (
        error instanceof ApiError &&
        error.status === 401
      ) {
        setUser(null);
        setIsAuthenticated(false);
      } else {
        /*
         * Keep the existing authentication state
         * when the request fails for another reason.
         *
         * This prevents a temporary network/server
         * problem from being treated as a logout.
         */
        setIsAuthenticated((current) =>
          current === null ? null : current,
        );
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshAuth();
  }, [refreshAuth]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated,
      isLoading,
      refreshAuth,
    }),
    [
      user,
      isAuthenticated,
      isLoading,
      refreshAuth,
    ],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      'useAuth must be used within an AuthProvider.',
    );
  }

  return context;
}