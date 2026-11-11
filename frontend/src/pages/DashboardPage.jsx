import React, { useState, useRef } from 'react';
import { apiRequest } from '../api/client';
import { RiskBadge } from '../components/RiskBadge';
import { ExpiryCountdown } from '../components/ExpiryCountdown';
import {
  FileTextIcon,
  UploadCloudIcon,
  AlertTriangleIcon,
  DownloadIcon,
  ShieldCheckIcon,
  SearchIcon,
  ClockIcon,
  BarChartIcon,
} from '../components/Icons';

export function DashboardPage({ onRequireAuth }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [scanResult, setScanResult] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (selectedFile) => {
    setError('');
    if (!selectedFile) return;

    const ext = selectedFile.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'doc'].includes(ext)) {
      setError('Поддерживаются только документы форматов PDF и DOCX.');
      return;
    }

    if (selectedFile.size > 20 * 1024 * 1024) {
      setError(`Размер файла (${(selectedFile.size / (1024 * 1024)).toFixed(1)} МБ) превышает ограничение 20 МБ.`);
      return;
    }

    setFile(selectedFile);
  };

  const handleUploadAndScan = async () => {
    if (!file) return;
    setError('');
    setUploading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await apiRequest('/documents/upload/', {
        method: 'POST',
        body: formData,
      });

      if (res.status === 401) {
        onRequireAuth();
        return;
      }

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.file?.[0] || errData.error || 'Ошибка при загрузке документа');
      }

      const data = await res.json();
      setScanResult(data);
      setFile(null);
    } catch (err) {
      setError(err.message || 'Ошибка обработки документа');
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadPdf = async (docId, filename) => {
    try {
      const res = await apiRequest(`/documents/${docId}/pdf/`);
      if (!res.ok) throw new Error('Не удалось скачать отчёт');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_report_${filename}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert(err.message || 'Ошибка скачивания отчёта');
    }
  };

  const featureBadgeStyle = (accent = false) => ({
    width: 40,
    height: 40,
    borderRadius: 10,
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 14,
    backgroundColor: accent ? 'rgba(226, 74, 141, 0.12)' : 'rgba(109, 102, 238, 0.12)',
    color: accent ? 'var(--color-accent)' : 'var(--color-secondary)',
  });

  return (
    <div style={{ maxWidth: 1100, margin: '30px auto', padding: '0 20px', display: 'flex', flexDirection: 'column', gap: 30 }}>
      {/* Intro Header */}
      <div style={{ textAlign: 'center', maxWidth: 700, margin: '0 auto' }}>
        <h1 style={{ fontSize: '2.2rem', marginBottom: 12 }}>
          Аудит документов на персональные данные
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem' }}>
          Загрузите документ в формате PDF или DOCX объёмом до 20 МБ для автоматизированного поиска ПДн, расчёта уровня риска и безопасного удаления исходного файла через 1 час.
        </p>
      </div>

      {/* Upload Box */}
      <div
        className="card"
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          if (e.dataTransfer.files?.[0]) handleFileSelect(e.dataTransfer.files[0]);
        }}
        style={{
          border: `2px dashed ${dragOver ? 'var(--color-accent)' : 'var(--border-color)'}`,
          backgroundColor: dragOver ? 'rgba(226, 74, 141, 0.04)' : 'var(--card-bg)',
          textAlign: 'center',
          padding: '40px 24px',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
        }}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.doc"
          style={{ display: 'none' }}
          onChange={(e) => handleFileSelect(e.target.files?.[0])}
        />

        <div style={{
          width: 60,
          height: 60,
          borderRadius: 14,
          margin: '0 auto 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: file ? 'rgba(226, 74, 141, 0.12)' : 'rgba(109, 102, 238, 0.1)',
          color: file ? 'var(--color-accent)' : 'var(--color-secondary)',
        }}>
          {file ? <FileTextIcon size={30} /> : <UploadCloudIcon size={32} />}
        </div>

        {file ? (
          <div>
            <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: 4 }}>
              {file.name}
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 20 }}>
              Размер: {(file.size / (1024 * 1024)).toFixed(2)} МБ • Формат готов к проверке
            </div>
            <div style={{ display: 'flex', justifyContent: 'center', gap: 12 }} onClick={(e) => e.stopPropagation()}>
              <button
                type="button"
                className="btn btn-accent"
                disabled={uploading}
                onClick={handleUploadAndScan}
              >
                {uploading ? 'Сканирование документа...' : 'Запустить аудит документа'}
              </button>
              <button
                type="button"
                className="btn btn-outline"
                disabled={uploading}
                onClick={() => setFile(null)}
              >
                Отмена
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', fontWeight: 600, marginBottom: 6 }}>
              Перетащите PDF или DOCX файл сюда
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 18 }}>
              или нажмите для выбора файла на вашем компьютере (до 20 МБ)
            </div>
            <span className="btn btn-secondary btn-sm" style={{ pointerEvents: 'none' }}>
              Выбрать документ
            </span>
          </div>
        )}

        {error && (
          <div style={{
            marginTop: 18,
            padding: '10px 16px',
            backgroundColor: 'rgba(239, 68, 68, 0.12)',
            color: '#EF4444',
            borderRadius: 8,
            fontSize: '0.9rem',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
          }}>
            <AlertTriangleIcon size={16} />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Audit Result Display */}
      {scanResult && (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* Card Header with Meta and Risk */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            flexWrap: 'wrap',
            gap: 16,
            borderBottom: '1px solid var(--border-color)',
            paddingBottom: 20
          }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8, flexWrap: 'wrap' }}>
                <h2 style={{ fontSize: '1.4rem' }}>{scanResult.original_filename}</h2>
                <RiskBadge riskLevel={scanResult.risk_level} label={scanResult.risk_display} />
              </div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                Размер: {(scanResult.file_size / 1024).toFixed(1)} КБ • Проверено: {new Date(scanResult.uploaded_at).toLocaleString('ru-RU')}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
              <ExpiryCountdown expiresAt={scanResult.expires_at} fileDeleted={scanResult.file_deleted} />
              <button
                className="btn btn-accent btn-sm"
                onClick={() => handleDownloadPdf(scanResult.id, scanResult.original_filename)}
              >
                <DownloadIcon size={15} />
                <span>Скачать PDF-отчёт</span>
              </button>
            </div>
          </div>

          {/* Risk Summary Notice */}
          <div style={{
            padding: '16px 20px',
            borderRadius: 10,
            backgroundColor: 'rgba(109, 102, 238, 0.08)',
            border: '1px solid rgba(109, 102, 238, 0.25)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: 14,
          }}>
            <div style={{ color: 'var(--color-secondary)', marginTop: 2 }}>
              <ShieldCheckIcon size={22} />
            </div>
            <div>
              <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 600, marginBottom: 4, color: 'var(--text-main)' }}>
                Заключение экспертной системы аудита:
              </div>
              <div style={{ color: 'var(--text-main)', fontSize: '0.95rem' }}>
                {scanResult.risk_summary || 'Персональные данные обработаны в соответствии с шаблонами.'}
              </div>
            </div>
          </div>

          {/* Findings Table */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
              <h3 style={{ fontSize: '1.15rem' }}>
                Обнаруженные записи ({scanResult.findings?.length || 0})
              </h3>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Все конфиденциальные фрагменты маскированы
              </span>
            </div>

            {scanResult.findings && scanResult.findings.length > 0 ? (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th style={{ width: 40 }}>№</th>
                      <th>Категория ПДн</th>
                      <th style={{ width: 80 }}>Стр.</th>
                      <th>Маскированное значение</th>
                      <th>Контекст в документе</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scanResult.findings.map((item, idx) => (
                      <tr key={item.id || idx}>
                        <td style={{ color: 'var(--text-muted)' }}>{idx + 1}</td>
                        <td style={{ fontWeight: 600 }}>{item.type_name}</td>
                        <td>
                          <span className="badge" style={{ background: 'rgba(125, 125, 125, 0.15)', whiteSpace: 'nowrap' }}>
                            стр. {item.page_number}
                          </span>
                        </td>
                        <td>
                          <code style={{
                            backgroundColor: 'rgba(226, 74, 141, 0.12)',
                            color: 'var(--color-accent)',
                            padding: '3px 8px',
                            borderRadius: 6,
                            fontFamily: 'monospace',
                            fontWeight: 700,
                            whiteSpace: 'nowrap',
                          }}>
                            {item.masked_value}
                          </code>
                        </td>
                        <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                          «{item.context}»
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '30px 0', color: 'var(--text-muted)' }}>
                В документе не обнаружено совпадений по шаблонам персональных данных.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Info Features */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20 }}>
        <div className="card">
          <div style={featureBadgeStyle(true)}>
            <SearchIcon size={20} />
          </div>
          <h3 style={{ fontSize: '1.1rem', marginBottom: 6 }}>6 категорий ПДн</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Поиск паспортов РФ, ИНН с проверкой контрольных цифр, СНИЛС, телефонов, e-mail и банковских карт с алгоритмом Луна.
          </p>
        </div>

        <div className="card">
          <div style={featureBadgeStyle(false)}>
            <ClockIcon size={20} />
          </div>
          <h3 style={{ fontSize: '1.1rem', marginBottom: 6 }}>Политика 1 часа</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Исходные файлы автоматически и безвозвратно удаляются с сервера через 60 минут после проверки.
          </p>
        </div>

        <div className="card">
          <div style={featureBadgeStyle(true)}>
            <BarChartIcon size={20} />
          </div>
          <h3 style={{ fontSize: '1.1rem', marginBottom: 6 }}>PDF-отчёт по ГОСТ</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Формирование официального протокола аудита безопасности с разбивкой по страницам и оценкой уровня риска.
          </p>
        </div>
      </div>
    </div>
  );
}
