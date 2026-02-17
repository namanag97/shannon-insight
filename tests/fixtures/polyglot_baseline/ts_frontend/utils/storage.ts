const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_KEY = 'current_user';

export const storage = {
  setAccessToken: (token: string): void => {
    try {
      localStorage.setItem(TOKEN_KEY, token);
    } catch (error) {
      console.error('Failed to set access token:', error);
    }
  },

  getAccessToken: (): string | null => {
    try {
      return localStorage.getItem(TOKEN_KEY);
    } catch (error) {
      console.error('Failed to get access token:', error);
      return null;
    }
  },

  setRefreshToken: (token: string): void => {
    try {
      localStorage.setItem(REFRESH_TOKEN_KEY, token);
    } catch (error) {
      console.error('Failed to set refresh token:', error);
    }
  },

  getRefreshToken: (): string | null => {
    try {
      return localStorage.getItem(REFRESH_TOKEN_KEY);
    } catch (error) {
      console.error('Failed to get refresh token:', error);
      return null;
    }
  },

  setUser: (user: unknown): void => {
    try {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    } catch (error) {
      console.error('Failed to set user:', error);
    }
  },

  getUser: (): unknown | null => {
    try {
      const user = localStorage.getItem(USER_KEY);
      return user ? JSON.parse(user) : null;
    } catch (error) {
      console.error('Failed to get user:', error);
      return null;
    }
  },

  clear: (): void => {
    try {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    } catch (error) {
      console.error('Failed to clear storage:', error);
    }
  },

  isTokenExpired: (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expiryTime = payload.exp * 1000;
      return Date.now() >= expiryTime;
    } catch {
      return true;
    }
  },
};
