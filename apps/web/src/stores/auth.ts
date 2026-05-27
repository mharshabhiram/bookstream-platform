import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import Cookies from 'js-cookie';

interface User {
  id: string;
  email: string;
  username: string;
  display_name: string | null;
  avatar_url: string | null;
  role: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  login: (user: User, tokens: { access_token: string; refresh_token: string }) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setLoading: (loading) => set({ isLoading: loading }),
      login: (user, tokens) => {
        Cookies.set('access_token', tokens.access_token, {
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'strict',
          expires: 1 / 48, // 30 minutes
        });
        Cookies.set('refresh_token', tokens.refresh_token, {
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'strict',
          expires: 7,
        });
        set({ user, isAuthenticated: true, isLoading: false });
      },
      logout: () => {
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        set({ user: null, isAuthenticated: false, isLoading: false });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);
