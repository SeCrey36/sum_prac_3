import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiRequest, setTokens, clearTokens, getTokens } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = async () => {
    try {
      const res = await apiRequest('/auth/me/');
      if (res.ok) {
        const data = await res.json();
        setUser(data);
        localStorage.setItem('current_user', JSON.stringify(data));
      } else {
        setUser(null);
        clearTokens();
      }
    } catch (err) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const { access } = getTokens();
    if (access) {
      fetchProfile();
    } else {
      setLoading(false);
    }

    const handleUnauthorized = () => setUser(null);
    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, []);

  const login = async (username, password) => {
    const res = await fetch('/api/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Неверный логин или пароль');
    }
    const data = await res.json();
    setTokens(data.access, data.refresh);
    await fetchProfile();
  };

  const register = async (username, email, password) => {
    const res = await fetch('/api/auth/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const msg = err.username?.[0] || err.email?.[0] || err.password?.[0] || 'Ошибка при регистрации';
      throw new Error(msg);
    }
    const data = await res.json();
    setTokens(data.tokens.access, data.tokens.refresh);
    setUser(data.user);
    localStorage.setItem('current_user', JSON.stringify(data.user));
  };

  const logout = () => {
    clearTokens();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser: fetchProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
