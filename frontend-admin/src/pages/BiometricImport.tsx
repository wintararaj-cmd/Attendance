import { useState } from 'react';
import { Upload, FileSpreadsheet, CheckCircle2, AlertCircle, Loader2, FileCode, X } from 'lucide-react';
import axios from 'axios';

export default function BiometricImport() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [useLocalPath, setUseLocalPath] = useState(false);
  const [filePath, setFilePath] = useState('E:\\Project\\AttendanceSys\\rpt_attn_dtls_emp.xls');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setError(null);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
  };

  const handleImport = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      if (useLocalPath) {
        formData.append('file_path', filePath);
      } else if (selectedFile) {
        formData.append('file', selectedFile);
      } else {
        throw new Error('Please select a file to upload or specify a local path.');
      }

      const response = await axios.post('/api/v1/attendance/import-biometric', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
      if (!useLocalPath) setSelectedFile(null); // Clear after success
    } catch (err: any) {
      console.error('Import error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to import biometric attendance data.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <FileSpreadsheet size={22} style={{ color: 'var(--primary)' }} />
            Biometric Attendance Import
          </h2>
          <div className="page-header-subtitle">Import attendance records from biometric device Excel files</div>
        </div>
      </div>

      <div className="card" style={{ maxWidth: '600px', margin: '2rem auto', padding: '2rem' }}>
        <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'center' }}>
          <div className="flex gap-1 p-1 bg-gray-100 rounded-lg" style={{ width: 'fit-content' }}>
            <button 
              className={`btn btn-sm ${!useLocalPath ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setUseLocalPath(false)}
            >
              Upload File
            </button>
            <button 
              className={`btn btn-sm ${useLocalPath ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setUseLocalPath(true)}
            >
              Server Path
            </button>
          </div>
        </div>

        {!useLocalPath ? (
          <div 
            style={{ 
              border: `2px dashed ${selectedFile ? 'var(--success)' : 'var(--border)'}`,
              borderRadius: 'var(--border-radius)',
              padding: '2.5rem 1.5rem',
              textAlign: 'center',
              backgroundColor: selectedFile ? 'var(--success-light)' : 'var(--bg-app)',
              cursor: 'pointer',
              transition: 'var(--transition)',
              position: 'relative'
            }}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                setSelectedFile(e.dataTransfer.files[0]);
              }
            }}
            onClick={() => !selectedFile && document.getElementById('file-upload')?.click()}
          >
            <input 
              type="file" 
              id="file-upload" 
              hidden 
              accept=".xls,.xlsx" 
              onChange={handleFileChange} 
            />
            
            {selectedFile ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle2 size={40} className="text-success" />
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{selectedFile.name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{(selectedFile.size / 1024).toFixed(1)} KB</div>
                </div>
                <button 
                  className="btn btn-ghost btn-sm" 
                  onClick={(e) => { e.stopPropagation(); clearFile(); }}
                  style={{ marginTop: '0.5rem', color: 'var(--danger)' }}
                >
                  <X size={14} /> Remove
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
                <div style={{ padding: '1rem', backgroundColor: 'white', borderRadius: '50%', boxShadow: 'var(--shadow-sm)' }}>
                  <Upload size={32} style={{ color: 'var(--primary)' }} />
                </div>
                <div>
                  <p style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.25rem' }}>Click to upload or drag and drop</p>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Excel files (.xls, .xlsx) exported from biometric device</p>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="form-group">
            <label>Full Path on Server</label>
            <div style={{ position: 'relative' }}>
              <FileCode className="input-icon" size={16} />
              <input
                type="text"
                className="input input-with-icon"
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
                placeholder="e.g. E:\Reports\attendance.xls"
              />
            </div>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
              Useful if the file is already on the server's local storage.
            </p>
          </div>
        )}

        <button
          onClick={handleImport}
          disabled={loading || (!selectedFile && !useLocalPath) || (useLocalPath && !filePath)}
          className="btn btn-primary lg"
          style={{ width: '100%', marginTop: '2rem', height: '3.5rem', fontSize: '1rem' }}
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin" size={20} />
              Smart Analyzing & Importing...
            </>
          ) : (
            <>
              <Upload size={20} />
              Start Smart Import
            </>
          )}
        </button>

        {error && (
          <div className="alert alert-error" style={{ marginTop: '1.5rem' }}>
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        {result && (
          <div className="alert alert-success" style={{ marginTop: '1.5rem', display: 'block' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', fontWeight: 700 }}>
              <CheckCircle2 size={20} />
              Import Successful
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div style={{ backgroundColor: 'white', padding: '0.75rem', borderRadius: '8px', border: '1px solid #a7f3d0' }}>
                <span style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#059669', fontWeight: 600 }}>Logs Created</span>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#064e3b' }}>{result.logs_imported}</div>
              </div>
              <div style={{ backgroundColor: 'white', padding: '0.75rem', borderRadius: '8px', border: '1px solid #a7f3d0' }}>
                <span style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#059669', fontWeight: 600 }}>Employees Created</span>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#064e3b' }}>{result.new_employees}</div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="card" style={{ maxWidth: '600px', margin: '0 auto', border: 'none', boxShadow: 'none', background: 'transparent' }}>
        <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertCircle size={16} style={{ color: 'var(--warning)' }} />
          Supported Format Information
        </h3>
        <ul style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.5rem', paddingLeft: '1.25rem' }}>
          <li>Supports <strong>.xls</strong> and <strong>.xlsx</strong> files.</li>
          <li>Automatically detects <strong>Month, Year</strong> and <strong>Day 1</strong> start columns using AI.</li>
          <li><strong>Smart Mapping:</strong> Syncs unknown status codes (WW, PP, HD, etc.) automatically.</li>
          <li>Adds new employees to the system automatically if not found.</li>
        </ul>
      </div>
    </div>
  );
}
