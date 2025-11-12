import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Button } from './ui/button';
import './TableViewer.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TableViewer = ({ jobId, table, onBack }) => {
  const [data, setData] = useState(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(100);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTableData();
  }, [page]);

  const fetchTableData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `${API}/jobs/${jobId}/tables/${table.name}/rows?page=${page}&pageSize=${pageSize}`
      );
      setData(response.data);
    } catch (error) {
      console.error('Failed to fetch table data:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalPages = data ? Math.ceil(data.total / pageSize) : 0;

  return (
    <div className="table-viewer" data-testid="table-viewer">
      <div className="viewer-header">
        <Button onClick={onBack} className="back-button" data-testid="back-button">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="19" y1="12" x2="5" y2="12"/>
            <polyline points="12 19 5 12 12 5"/>
          </svg>
          Geri
        </Button>
        <div className="table-header-info">
          <h4 data-testid="table-name">{table.name}</h4>
          <span className="table-total" data-testid="table-total">{data?.total.toLocaleString('tr-TR')} satır</span>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner-large"></div>
          <p>Yükleniyor...</p>
        </div>
      ) : data && data.rows.length > 0 ? (
        <>
          <div className="table-wrapper">
            <table className="data-table" data-testid="data-table">
              <thead>
                <tr>
                  {data.columns.map((col) => (
                    <th key={col} data-testid={`column-${col}`}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.rows.map((row, rowIdx) => (
                  <tr key={rowIdx} data-testid={`row-${rowIdx}`}>
                    {row.map((cell, cellIdx) => (
                      <td key={cellIdx} data-testid={`cell-${rowIdx}-${cellIdx}`}>
                        {cell === null ? <span className="null-value">NULL</span> : String(cell)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination" data-testid="pagination">
            <Button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              data-testid="prev-button"
              className="pagination-button"
            >
              Önceki
            </Button>
            <span className="page-info" data-testid="page-info">
              Sayfa {page} / {totalPages}
            </span>
            <Button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              data-testid="next-button"
              className="pagination-button"
            >
              Sonraki
            </Button>
          </div>
        </>
      ) : (
        <div className="empty-state">
          <p>Veri bulunamadı</p>
        </div>
      )}
    </div>
  );
};

export default TableViewer;
