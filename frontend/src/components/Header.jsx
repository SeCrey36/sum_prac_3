import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { ShieldCheckIcon, FileTextIcon, HistoryIcon, SunIcon, MoonIcon } from './Icons';

export function Header({ currentTab, setCurrentTab, onOpenAuth }) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <header style={{
      borderBottom: '1px solid var(--border-color)',
      padding: '16px 24px',
      backgroundColor: 'var(--card-bg)',
      backdropFilter: 'blur(8px)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{
        maxWidth: 1200,
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 16,
      }}>
        {/* Logo */}
        <div 
          onClick={() => setCurrentTab('dashboard')}
          style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}
        >
          <div style={{
            width: 38,
            height: 38,
            borderRadius: 10,
            background: 'linear-gradient(135deg, var(--color-accent), var(--color-secondary))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: '0 2px 8px rgba(226, 74, 141, 0.4)'
          }}>
            <ShieldCheckIcon size={20} />
          </div>
          <div>
            <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1.15rem', color: 'var(--text-main)' }}>
              DocSec <span style={{ fontSize: '0.75rem', color: 'var(--color-accent)', fontWeight: 600 }}>152-ФЗ</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1 }}>
              Аудит персональных данных
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        {user && (
          <nav style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={() => setCurrentTab('dashboard')}
              className={`btn btn-sm ${currentTab === 'dashboard' ? 'btn-accent' : 'btn-outline'}`}
            >
              <FileTextIcon size={15} />
              <span>Проверка файла</span>
            </button>
            <button
              onClick={() => setCurrentTab('history')}
              className={`btn btn-sm ${currentTab === 'history' ? 'btn-accent' : 'btn-outline'}`}
            >
              <HistoryIcon size={15} />
              <span>История проверок</span>
            </button>
          </nav>
        )}

        {/* Actions & User */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button
            onClick={toggleTheme}
            className="btn btn-outline btn-sm"
            title="Переключить тему"
            style={{ padding: '7px 10px' }}
          >
            {theme === 'dark' ? <SunIcon size={16} /> : <MoonIcon size={16} />}
          </button>

          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{user.username}</span>
              </div>
              <button onClick={logout} className="btn btn-outline btn-sm">
                Выйти
              </button>
            </div>
          ) : (
            <button onClick={onOpenAuth} className="btn btn-accent btn-sm">
              Войти / Регистрация
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
