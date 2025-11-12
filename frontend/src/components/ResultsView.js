import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Button } from './ui/button';
import TableViewer from './TableViewer';
import './ResultsView.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ResultsView = ({ jobId, onReset }) => {
  const [jobStatus, setJobStatus] = useState(null);
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);

  useEffect(() => {
    fetchJobStatus();
    fetchTables();
  }, [jobId]);

  const fetchJobStatus = async () => {
    try {
      const response = await axios.get(`${API}/jobs/${jobId}`);
      setJobStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch job status:', error);
    }
  };

  const fetchTables = async () => {
    try {
      const response = await axios.get(`${API}/jobs/${jobId}/tables`);
      setTables(response.data.tables);
    } catch (error) {
      console.error('Failed to fetch tables:', error);
    }
  };

  const downloadArtifact = (filename) => {
    window.open(`${API}/jobs/${jobId}/artifacts/${filename}`, '_blank');
  };

  const totalRows = tables.reduce((sum, t) => sum + t.rowCount, 0);
  const successTables = tables.filter(t => t.copied && !t.error).length;

  return (
    <div className="results-container" data-testid="results-view">
      <div className="results-header">
        <div className="success-banner" data-testid="success-banner">
          <div className="success-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <div>
            <h2>Migrasyon Tamamlandı!</h2>
            <p>Verileriniz başarıyla PostgreSQL'e aktarıldı</p>
          </div>
        </div>
      </div>

      <div className="summary-grid">
        <div className="summary-card" data-testid="summary-tables">
          <div className="summary-icon" style={{ background: '#dbeafe' }}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" strokeWidth="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <line x1="3" y1="9" x2="21" y2="9"/>
              <line x1="9" y1="21" x2="9" y2="9"/>
            </svg>
          </div>
          <div className="summary-content">
            <div className="summary-value">{successTables} / {tables.length}</div>
            <div className="summary-label">Tablo</div>
          </div>
        </div>

        <div className="summary-card" data-testid="summary-rows">
          <div className="summary-icon" style={{ background: '#dcfce7' }}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#16a34a" strokeWidth="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
              <line x1="12" y1="22.08" x2="12" y2="12"/>
            </svg>
          </div>
          <div className="summary-content">
            <div className="summary-value">{totalRows.toLocaleString('tr-TR')}</div>
            <div className="summary-label">Satır</div>
          </div>
        </div>

        <div className="summary-card" data-testid="summary-duration">
          <div className="summary-icon" style={{ background: '#fef3c7' }}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ca8a04" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div className="summary-content">
            <div className="summary-value">{jobStatus?.stats.elapsedSec.toFixed(1)}s</div>
            <div className="summary-label">Süre</div>
          </div>
        </div>
      </div>

      <div className="artifacts-section">
        <h3>Rapor Dosyaları</h3>
        <div className="artifacts-grid">
          <div className="artifact-card" onClick={() => downloadArtifact('schema.sql')} data-testid="download-schema">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            <div>
              <div className="artifact-name">schema.sql</div>
              <div className="artifact-desc">DDL komutları</div>
            </div>
          </div>

          <div className="artifact-card" onClick={() => downloadArtifact('rowcount.csv')} data-testid="download-rowcount">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <path d="M12 18v-6"/>
              <path d="M9 15l3 3 3-3"/>
            </svg>
            <div>
              <div className="artifact-name">rowcount.csv</div>
              <div className="artifact-desc">Satır sayıları</div>
            </div>
          </div>

          <div className="artifact-card" onClick={() => downloadArtifact('errors.log')} data-testid="download-errors">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <circle cx="12" cy="13" r="2"/>
            </svg>
            <div>
              <div className="artifact-name">errors.log</div>
              <div className="artifact-desc">Hata log'ları</div>
            </div>
          </div>
        </div>
      </div>

      <div className="table-viewer-section">
        <h3>Veri Görüntüleme</h3>
        {!selectedTable ? (
          <div className="table-selector">
            <p>Görüntülemek için bir tablo seçin:</p>
            <div className="table-list" data-testid="table-list">
              {tables.map((table) => (
                <div
                  key={table.name}
                  className="table-list-item"
                  onClick={() => setSelectedTable(table)}
                  data-testid={`table-item-${table.name}`}
                >
                  <div className="table-info">
                    <span className="table-name">{table.name}</span>
                    <span className="table-rows">{table.rowCount.toLocaleString('tr-TR')} satır</span>
                  </div>
                  {table.error && (
                    <span className="table-error">⚠ Hata</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <TableViewer
            jobId={jobId}
            table={selectedTable}
            onBack={() => setSelectedTable(null)}
          />
        )}
      </div>

      <div className="actions">
        <Button onClick={onReset} data-testid="new-migration-button" className="reset-button">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="1 4 1 10 7 10"/>
            <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
          </svg>
          Yeni Migrasyon
        </Button>
      </div>
    </div>
  );
};

export default ResultsView;
