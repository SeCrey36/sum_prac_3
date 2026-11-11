import React, { useState, useEffect } from 'react';
import { LockIcon, ClockIcon } from './Icons';

export function ExpiryCountdown({ expiresAt, fileDeleted }) {
  const [timeLeft, setTimeLeft] = useState('');
  const [isExpired, setIsExpired] = useState(fileDeleted);

  useEffect(() => {
    if (fileDeleted) {
      setIsExpired(true);
      return;
    }

    if (!expiresAt) return;

    const targetTime = new Date(expiresAt).getTime();

    const updateTimer = () => {
      const now = new Date().getTime();
      const diff = targetTime - now;

      if (diff <= 0) {
        setIsExpired(true);
        setTimeLeft('00:00');
      } else {
        const minutes = Math.floor(diff / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        setTimeLeft(`${minutes} мин ${seconds < 10 ? '0' : ''}${seconds} сек`);
      }
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    return () => clearInterval(interval);
  }, [expiresAt, fileDeleted]);

  if (isExpired) {
    return (
      <div
        title="Исходный файл удалён с сервера (политика 1-часового хранения)"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          padding: '5px 10px',
          borderRadius: 8,
          backgroundColor: 'rgba(107, 114, 128, 0.1)',
          border: '1px solid var(--border-color)',
          color: 'var(--text-muted)',
          fontSize: '0.8rem',
          whiteSpace: 'nowrap',
        }}
      >
        <LockIcon size={13} />
        <span>Файл удалён</span>
      </div>
    );
  }

  return (
    <div
      title="Исходный файл будет автоматически удалён с сервера через 1 час после загрузки"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        padding: '5px 10px',
        borderRadius: 8,
        backgroundColor: 'rgba(226, 74, 141, 0.08)',
        border: '1px solid rgba(226, 74, 141, 0.25)',
        color: 'var(--color-accent)',
        fontSize: '0.8rem',
        fontWeight: 600,
        whiteSpace: 'nowrap',
      }}
    >
      <ClockIcon size={13} />
      <span>Удалится через {timeLeft}</span>
    </div>
  );
}
