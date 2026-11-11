import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { Header } from './components/Header';
import { DashboardPage } from './pages/DashboardPage';
import { HistoryPage } from './pages/HistoryPage';
import { AuthModal } from './pages/AuthModal';
import { apiRequest } from './api/client';
import { FileTextIcon, DownloadIcon, CloseIcon } from './components/Icons';

function MainLayout() {
  const { user } = useAuth();
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [selectedDocDetails, setSelectedDocDetails] = useState(null);

  const handleSelectDoc = async (docId) => {
    try {
      const res = await apiRequest(`/documents/${docId}/`);
      if (res.ok) {
        const data = await res.json();
        setSelectedDocDetails(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header
        currentTab={currentTab}
        setCurrentTab={(tab) => {
          setSelectedDocDetails(null);
          setCurrentTab(tab);
        }}
        onOpenAuth={() => setAuthModalOpen(true)}
      />

      <main style={{ flex: 1, paddingBottom: 60 }}>
        {currentTab === 'dashboard' && (
          <DashboardPage onRequireAuth={() => setAuthModalOpen(true)} />
        )}

        {currentTab === 'history' && (
          <HistoryPage onSelectDoc={handleSelectDoc} />
        )}
      </main>

      <footer style={{
        borderTop: '1px solid var(--border-color)',
        padding: '20px 24px',
        textAlign: 'center',
        color: 'var(--text-muted)',
        fontSize: '0.85rem'
      }}>
        <div>
          DocSec — Автоматизированный сервис проверки документов на персональные данные (152-ФЗ)
        </div>
        <div style={{ marginTop: 4 }}>
          Учебная практика по направлению «Программная инженерия» • СФУ ИКИТ
        </div>
      </footer>

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
      />

      {/* Modal for viewing detailed scan from history */}
      {selectedDocDetails && (
        <div style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.65)',
          backdropFilter: 'blur(5px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: 20
        }}>
          <div className="card" style={{ maxWidth: 850, width: '100%', maxHeight: '85vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h2 style={{ fontSize: '1.3rem', display: 'flex', alignItems: 'center', gap: 8 }}>
                <FileTextIcon size={20} />
                <span>{selectedDocDetails.original_filename}</span>
              </h2>
              <button
                onClick={() => setSelectedDocDetails(null)}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', padding: 4 }}
              >
                <CloseIcon size={18} />
              </button>
            </div>

            <div style={{ marginBottom: 16, display: 'flex', gap: 10, flexWrap: 'wrap' }}>
              <span className="badge badge-medium">
                Находок: {selectedDocDetails.total_findings}
              </span>
              <span className="badge" style={{ background: 'rgba(125, 125, 125, 0.15)' }}>
                Проверено: {new Date(selectedDocDetails.uploaded_at).toLocaleString('ru-RU')}
              </span>
            </div>

            <div style={{ padding: '12px 16px', borderRadius: 8, backgroundColor: 'rgba(109, 102, 238, 0.08)', marginBottom: 16 }}>
              <b>Оценка риска:</b> {selectedDocDetails.risk_summary}
            </div>

            {selectedDocDetails.findings && selectedDocDetails.findings.length > 0 ? (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>№</th>
                      <th>Тип данных</th>
                      <th>Стр.</th>
                      <th>Маскированный фрагмент</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedDocDetails.findings.map((f, i) => (
                      <tr key={f.id || i}>
                        <td>{i + 1}</td>
                        <td style={{ fontWeight: 600 }}>{f.type_name}</td>
                        <td>стр. {f.page_number}</td>
                        <td>
                          <code style={{ color: 'var(--color-accent)', fontWeight: 700 }}>
                            {f.masked_value}
                          </code>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: 20, color: 'var(--text-muted)' }}>
                Персональные данные не найдены.
              </div>
            )}

            <div style={{ marginTop: 20, textAlign: 'right' }}>
              <button
                className="btn btn-accent btn-sm"
                onClick={async () => {
                  const res = await apiRequest(`/documents/${selectedDocDetails.id}/pdf/`);
                  if (res.ok) {
                    const blob = await res.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `audit_report_${selectedDocDetails.original_filename}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url);
                  }
                }}
              >
                <DownloadIcon size={15} />
                <span>Скачать PDF-протокол</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <MainLayout />
      </AuthProvider>
    </ThemeProvider>
  );
}
