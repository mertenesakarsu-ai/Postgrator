import React, { useState } from 'react';
import UploadForm from '../components/UploadForm';
import ProgressView from '../components/ProgressView';
import ResultsView from '../components/ResultsView';

const Home = () => {
  const [view, setView] = useState('upload'); // upload, progress, results
  const [jobId, setJobId] = useState(null);

  const handleUploadStart = (newJobId) => {
    setJobId(newJobId);
    setView('progress');
  };

  const handleMigrationComplete = () => {
    setView('results');
  };

  const handleReset = () => {
    setView('upload');
    setJobId(null);
  };

  return (
    <div className="home-container">
      <header className="header">
        <div className="header-content">
          <h1 data-testid="app-title">Postgrator</h1>
          <p className="subtitle">SQL Server → PostgreSQL Migrasyonu</p>
        </div>
      </header>

      <main className="main-content">
        {view === 'upload' && (
          <UploadForm onUploadStart={handleUploadStart} />
        )}
        
        {view === 'progress' && jobId && (
          <ProgressView 
            jobId={jobId} 
            onComplete={handleMigrationComplete}
          />
        )}
        
        {view === 'results' && jobId && (
          <ResultsView 
            jobId={jobId}
            onReset={handleReset}
          />
        )}
      </main>
    </div>
  );
};

export default Home;
