import React, { useState } from 'react';
import axios from 'axios';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { toast } from 'sonner';
import './UploadForm.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UploadForm = ({ onUploadStart }) => {
  const [file, setFile] = useState(null);
  const [pgUri, setPgUri] = useState('postgresql://postgres:postgres@localhost:5432/target_db');
  const [schema, setSchema] = useState('public');
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.bak')) {
        toast.error('Lütfen bir .bak dosyası seçin');
        return;
      }
      setFile(selectedFile);
      toast.success(`Dosya seçildi: ${selectedFile.name}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      toast.error('Lütfen bir .bak dosyası seçin');
      return;
    }

    if (!pgUri) {
      toast.error('Lütfen PostgreSQL bağlantı URI\'sini girin');
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('pgUri', pgUri);
      formData.append('schema', schema);

      const response = await axios.post(`${API}/import`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      toast.success('Migrasyon başlatıldı!');
      onUploadStart(response.data.jobId);
    } catch (error) {
      console.error('Upload error:', error);
      const errorMsg = error.response?.data?.detail || 'Yükleme başarısız oldu';
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleDemo = async () => {
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/import/demo`);
      toast.success('Demo migrasyon başlatıldı!');
      onUploadStart(response.data.jobId);
    } catch (error) {
      console.error('Demo error:', error);
      const errorMsg = error.response?.data?.detail || 'Demo başlatılamadı';
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container" data-testid="upload-form">
      <div className="upload-card">
        <div className="card-header">
          <div className="icon-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          </div>
          <h2>Yedek Dosyasını Yükle</h2>
          <p>SQL Server .bak yedeğinizi seçin ve PostgreSQL'e aktarın</p>
        </div>

        <form onSubmit={handleSubmit} className="upload-form">
          <div className="form-group">
            <Label htmlFor="bak-file">BAK Dosyası</Label>
            <div className="file-input-wrapper">
              <Input
                id="bak-file"
                data-testid="file-input"
                type="file"
                accept=".bak"
                onChange={handleFileChange}
                disabled={loading}
              />
              {file && (
                <div className="file-info" data-testid="file-info">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
                    <polyline points="13 2 13 9 20 9"/>
                  </svg>
                  <span>{file.name}</span>
                  <span className="file-size">({(file.size / (1024 * 1024)).toFixed(2)} MB)</span>
                </div>
              )}
            </div>
          </div>

          <div className="form-group">
            <Label htmlFor="pg-uri">PostgreSQL Bağlantı URI</Label>
            <Input
              id="pg-uri"
              data-testid="pg-uri-input"
              type="text"
              value={pgUri}
              onChange={(e) => setPgUri(e.target.value)}
              placeholder="postgresql://user:pass@host:5432/database"
              disabled={loading}
            />
            <span className="hint">Örnek: postgresql://postgres:postgres@localhost:5432/target_db</span>
          </div>

          <div className="form-group">
            <Label htmlFor="schema">Hedef Şema</Label>
            <Input
              id="schema"
              data-testid="schema-input"
              type="text"
              value={schema}
              onChange={(e) => setSchema(e.target.value)}
              placeholder="public"
              disabled={loading}
            />
          </div>

          <Button
            type="submit"
            data-testid="start-button"
            className="submit-button"
            disabled={loading || !file}
          >
            {loading ? (
              <>
                <div className="spinner"></div>
                Yükleniyor...
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="9 11 12 14 22 4"/>
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                </svg>
                Migrasyonu Başlat
              </>
            )}
          </Button>
        </form>

        <div className="demo-section">
          <div className="divider">
            <span>VEYA</span>
          </div>
          <Button
            type="button"
            data-testid="demo-button"
            className="demo-button"
            onClick={handleDemo}
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="spinner"></div>
                Başlatılıyor...
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polygon points="10 8 16 12 10 16 10 8"/>
                </svg>
                Demo Modu İle Dene
              </>
            )}
          </Button>
          <p className="demo-description">
            Gerçek veritabanı olmadan migration işlemini deneyimleyin
          </p>
        </div>
      </div>

      <div className="info-cards">
        <div className="info-card">
          <h3>Hızlı Aktarım</h3>
          <p>Optimize edilmiş COPY protokolü ile yüksek performans</p>
        </div>
        <div className="info-card">
          <h3>Şema Korunur</h3>
          <p>Tablolar, ilişkiler ve kısıtlamalar bozulmadan aktarılır</p>
        </div>
        <div className="info-card">
          <h3>Canlı İzleme</h3>
          <p>Gerçek zamanlı ilerleme ve log takibi</p>
        </div>
      </div>
    </div>
  );
};

export default UploadForm;
