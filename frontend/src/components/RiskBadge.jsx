import React from 'react';
import { CheckCircleIcon, AlertTriangleIcon, ShieldAlertIcon } from './Icons';

export function RiskBadge({ riskLevel, label }) {
  const displayLabel = label || {
    LOW: 'Низкий риск',
    MEDIUM: 'Средний риск',
    CRITICAL: 'Критический риск'
  }[riskLevel] || riskLevel;

  const badgeClass = {
    LOW: 'badge-low',
    MEDIUM: 'badge-medium',
    CRITICAL: 'badge-critical'
  }[riskLevel] || 'badge-low';

  const icons = {
    LOW: <CheckCircleIcon size={14} />,
    MEDIUM: <AlertTriangleIcon size={14} />,
    CRITICAL: <ShieldAlertIcon size={14} />,
  };

  return (
    <span
      className={`badge ${badgeClass}`}
      style={{ fontSize: '0.82rem', padding: '5px 10px', gap: 6, whiteSpace: 'nowrap' }}
    >
      {icons[riskLevel] || <CheckCircleIcon size={14} />}
      <span>{displayLabel}</span>
    </span>
  );
}
