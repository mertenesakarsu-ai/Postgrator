import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { Progress } from './ui/progress';
import './ProgressView.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const WS_URL = BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://');

const STAGES = [
  { key: 'verify', label: 'Doğrulama', icon: '🔍' },
  { key: 'restore', label: 'Restore', icon: '📦' },
  { key: 'schema_discovery', label: 'Şema Analizi', icon: '🔎' },
  { key: 'ddl_apply', label: 'Tablo Oluşturma', icon: '🏗️' },
  { key: 'data_copy', label: 'Veri Kopyalama', icon: '📊' },
  { key: 'constraints_apply', label: 'Kısıtlamalar', icon: '🔗' },
  { key: 'validate', label: 'Doğrulama', icon: '✅' },
  { key: 'done', label: 'Tamamlandı', icon: '🎉' },
];

const ProgressView = ({ jobId, onComplete }) => {
  const [jobStatus, setJobStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const wsRef = useRef(null);
  const logsEndRef = useRef(null);

  useEffect(() => {
    // Fetch initial job status
    fetchJobStatus();

    // Connect WebSocket
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [jobId]);

  useEffect(() => {
    // Auto scroll logs
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const fetchJobStatus = async () => {
    try {
      const response = await axios.get(`${API}/jobs/${jobId}`);
      setJobStatus(response.data);
      
      const stageIdx = STAGES.findIndex(s => s.key === response.data.stage);
      if (stageIdx >= 0) {
        setCurrentStageIndex(stageIdx);
      }
    } catch (error) {
      console.error('Failed to fetch job status:', error);
    }
  };

  const connectWebSocket = () => {
    const ws = new WebSocket(`${WS_URL}/api/jobs/${jobId}/stream`);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.t === 'stage') {
        const stageIdx = STAGES.findIndex(s => s.key === message.v);
        if (stageIdx >= 0) {
          setCurrentStageIndex(stageIdx);
        }
      } else if (message.t === 'log') {
        setLogs(prev => [...prev, message]);
      } else if (message.t === 'table_progress') {
        setLogs(prev => [...prev, {
          level: 'info',
          msg: `${message.table}: ${message.rows}/${message.total} satır (${message.percent}%)`
        }]);
      } else if (message.t === 'done') {
        if (message.success) {
          setTimeout(() => onComplete(), 1500);
        }
      } else if (message.t === 'error') {
        setLogs(prev => [...prev, { level: 'error', msg: message.msg }]);
      }
      
      // Update job status
      fetchJobStatus();
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    wsRef.current = ws;
  };

  const getLogClass = (level) => {
    switch (level) {
      case 'error': return 'log-error';
      case 'warning': return 'log-warning';
      case 'info': return 'log-info';
      default: return 'log-info';
    }
  };

  return (
    <div className="progress-container" data-testid="progress-view">
      <div className="progress-card">
        <div className="progress-header">
          <h2>Migrasyon İlerliyor</h2>
          {jobStatus && (
            <div className="progress-stats">
              <span data-testid="tables-progress">{jobStatus.stats.tablesDone} / {jobStatus.stats.tablesTotal} tablo</span>
              <span data-testid="elapsed-time">{jobStatus.stats.elapsedSec.toFixed(1)}s</span>
            </div>
          )}
        </div>

        <div className="overall-progress">
          <div className="progress-label">
            <span data-testid="progress-percent">{jobStatus?.percent || 0}%</span>
            <span className="current-stage">{STAGES[currentStageIndex]?.label}</span>
          </div>
          <Progress value={jobStatus?.percent || 0} className="progress-bar" data-testid="progress-bar" />
        </div>

        <div className="stages-timeline">
          {STAGES.map((stage, index) => (
            <div
              key={stage.key}
              className={`stage-item ${
                index < currentStageIndex ? 'completed' :
                index === currentStageIndex ? 'active' : 'pending'
              }`}
              data-testid={`stage-${stage.key}`}
            >
              <div className="stage-icon">{stage.icon}</div>
              <div className="stage-label">{stage.label}</div>
            </div>
          ))}
        </div>

        <div className="logs-section">
          <h3>Log Kayıtları</h3>
          <div className="logs-container" data-testid="logs-container">
            {logs.map((log, idx) => (
              <div key={idx} className={`log-entry ${getLogClass(log.level)}`}>
                <span className="log-time">{new Date().toLocaleTimeString('tr-TR')}</span>
                <span className="log-message">{log.msg}</span>
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>

        {jobStatus?.error && (
          <div className="error-banner" data-testid="error-banner">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <span>{jobStatus.error}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressView;
