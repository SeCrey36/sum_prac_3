import React, { useState, useEffect } from 'react';
import { apiRequest } from '../api/client';
import { RiskBadge } from '../components/RiskBadge';
import { ExpiryCountdown } from '../components/ExpiryCountdown';
import {
  FileTextIcon,
  DownloadIcon,
  RefreshIcon,
  TrashIcon,
  InboxIcon,
  SearchIcon,
} from '../components/Icons';

export function HistoryPage({ onSelectDoc }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await apiRequest('/documents/');
      if (!res.ok) throw new Error('Не удалось загрузить историю проверок');
      const data = await res.json();
      setDocuments(data);
    } catch (err) {
      setError(err.message || 'Ошибка загрузки истории');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

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
      alert(err.message || 'Ошибка скачивания');
    }
  };

  const handleDelete = async (docId) => {
    if (!confirm('Вы действительно хотите удалить запись аудита из истории?')) return;
    try {
      const res = await apiRequest(`/documents/${docId}/delete/`, { method: 'DELETE' });
      if (res.ok) {
        setDocuments(prev => prev.filter(d => d.id !== docId));
      }
    } catch (err) {
      alert('Ошибка при удалении');
    }
  };

  const filteredDocs = documents.filter(doc =>
    doc.original_filename.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div style={{ maxWidth: 1100, margin: '30px auto', padding: '0 20px', display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', marginBottom: 4 }}>История проверок документов</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Журнал аудита документов, выполненных под вашей учётной записью
          </p>
        </div>

        <button onClick={fetchHistory} className="btn btn-outline btn-sm">
          <RefreshIcon size={14} />
          <span>Обновить</span>
        </button>
      </div>

      {/* Search Input */}
      <div style={{ maxWidth: 400, position: 'relative' }}>
        <div style={{
          position: 'absolute',
          left: 12,
          top: '50%',
          transform: 'translateY(-50%)',
          color: 'var(--text-muted)',
          pointerEvents: 'none',
          display: 'flex',
        }}>
          <SearchIcon size={16} />
        </div>
        <input
          type="text"
          placeholder="Поиск по названию документа..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ paddingLeft: 38 }}
        />
      </div>

      {error && (
        <div style={{ padding: '12px 16px', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: '#EF4444', borderRadius: 8 }}>
          {error}
        </div>
      )}

      {/* History Table */}
      <div className="card" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
            Загрузка истории проверок...
          </div>
        ) : filteredDocs.length > 0 ? (
          <div className="table-container" style={{ border: 'none' }}>
            <table>
              <thead>
                <tr>
                  <th>Документ</th>
                  <th>Дата проверки</th>
                  <th>Уровень риска</th>
                  <th>Найдено</th>
                  <th>Статус файла</th>
                  <th style={{ textAlign: 'right' }}>Действия</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocs.map((doc) => (
                  <tr key={doc.id}>
                    <td>
                      <div
                        onClick={() => onSelectDoc(doc.id)}
                        style={{
                          fontWeight: 600,
                          cursor: 'pointer',
                          color: 'var(--color-accent)',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 6
                        }}
                      >
                        <FileTextIcon size={15} />
                        <span style={{ textDecoration: 'underline' }}>{doc.original_filename}</span>
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {(doc.file_size / 1024).toFixed(1)} КБ
                      </div>
                    </td>
                    <td style={{ fontSize: '0.9rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                      {new Date(doc.uploaded_at).toLocaleString('ru-RU')}
                    </td>
                    <td>
                      <RiskBadge riskLevel={doc.risk_level} label={doc.risk_display} />
                    </td>
                    <td>
                      <span style={{
                        fontWeight: 700,
                        fontSize: '1rem',
                        color: doc.total_findings > 0 ? 'var(--text-main)' : 'var(--text-muted)'
                      }}>
                        {doc.total_findings}
                      </span>
                    </td>
                    <td>
                      <ExpiryCountdown expiresAt={doc.expires_at} fileDeleted={doc.file_deleted} />
                    </td>
                    <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                      <div style={{ display: 'inline-flex', gap: 8 }}>
                        <button
                          onClick={() => handleDownloadPdf(doc.id, doc.original_filename)}
                          className="btn btn-outline btn-sm"
                          title="Скачать PDF-отчёт"
                        >
                          <DownloadIcon size={14} />
                          <span>PDF</span>
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id)}
                          className="btn btn-outline btn-sm"
                          title="Удалить из журнала"
                          style={{ color: '#EF4444', padding: '6px 9px' }}
                        >
                          <TrashIcon size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '50px 20px', color: 'var(--text-muted)' }}>
            <div style={{ marginBottom: 12, color: 'var(--text-muted)', opacity: 0.7 }}>
              <InboxIcon size={40} />
            </div>
            <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 600, marginBottom: 6, fontSize: '1.1rem', color: 'var(--text-main)' }}>
              История проверок пуста
            </div>
            <div>Загрузите свой первый документ во вкладке «Проверка файла».</div>
          </div>
        )}
      </div>
    </div>
  );
}
