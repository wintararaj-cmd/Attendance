import { useEffect, useState } from 'react';
import axios from 'axios';
import { Calendar, Clock, Download, Filter } from 'lucide-react';

interface AttendanceLog {
    id: string;
    employee_name: string;
    emp_code: string;
    date: string;
    check_in: string | null;
    check_out: string | null;
    status: string;
    confidence: number | null;
}



export default function AttendanceLogs() {
    const [logs, setLogs] = useState<AttendanceLog[]>([]);
    // Filters
    const [searchTerm, setSearchTerm] = useState('');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');

    const [loading, setLoading] = useState(true);
    const [exporting, setExporting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchLogs();
    }, []);

    const fetchLogs = async () => {
        try {
            setLoading(true);
            setError(null);

            const params: any = {};
            if (searchTerm) params.search = searchTerm;
            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;

            const res = await axios.get('/api/v1/attendance/logs', { params });
            // Backend returns { logs: [...] }
            setLogs(res.data.logs || []);
        } catch (err: any) {
            console.error("Failed to fetch logs", err);
            setError(err.response?.data?.detail || err.message || "Failed to load logs");
        } finally {
            setLoading(false);
        }
    };

    const handleExport = async () => {
        try {
            setExporting(true);
            const params: any = {};
            if (searchTerm) params.search = searchTerm;
            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;

            const response = await axios.get('/api/v1/attendance/export', {
                params,
                responseType: 'blob', // Important for file download
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `attendance_logs_${new Date().toISOString().split('T')[0]}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err: any) {
            console.error("Export failed", err);
            const msg = err.response?.data?.detail || "Failed to export logs";
            alert(`Export Error: ${msg}`);
        } finally {
            setExporting(false);
        }
    };

    const formatTime = (timeStr: string | null) => {
        // Backend now returns formatted string "HH:MM AM/PM"
        if (!timeStr) return '--:--';
        return timeStr;
    };

    const formatDate = (isoString: string) => {
        if (!isoString) return '';
        return new Date(isoString).toLocaleDateString([], { day: '2-digit', month: 'short', year: 'numeric' });
    };

    return (
        <div>
            <div className="page-header">
                <div>
                    <h2>Attendance Logs</h2>
                    <div className="text-muted" style={{ fontSize: '0.875rem' }}>
                        View and export attendance records
                    </div>
                </div>
            </div>

            <div className="card" style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                    <div style={{ flex: 1, minWidth: '200px' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500, fontSize: '0.875rem' }}>
                            Search Employee
                        </label>
                        <input
                            type="text"
                            placeholder="Search by Name or Code..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                    fetchLogs();
                                }
                            }}
                            style={{
                                width: '100%',
                                padding: '0.6rem',
                                borderRadius: '8px',
                                border: '1px solid #d1d5db',
                                fontSize: '0.875rem'
                            }}
                        />
                    </div>

                    <div style={{ width: '150px' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500, fontSize: '0.875rem' }}>
                            Start Date
                        </label>
                        <input
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '0.6rem',
                                borderRadius: '8px',
                                border: '1px solid #d1d5db',
                                fontSize: '0.875rem'
                            }}
                        />
                    </div>

                    <div style={{ width: '150px' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500, fontSize: '0.875rem' }}>
                            End Date
                        </label>
                        <input
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '0.6rem',
                                borderRadius: '8px',
                                border: '1px solid #d1d5db',
                                fontSize: '0.875rem'
                            }}
                        />
                    </div>

                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                            className="btn btn-primary"
                            onClick={fetchLogs}
                            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                        >
                            <Filter size={16} /> Filter
                        </button>

                        <button
                            className="btn"
                            onClick={handleExport}
                            disabled={exporting}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                backgroundColor: '#10b981',
                                color: 'white'
                            }}
                        >
                            <Download size={16} /> {exporting ? 'Exporting...' : 'Export CSV'}
                        </button>
                    </div>
                </div>
            </div>

            {loading ? (
                <div className="p-4 text-center">Loading logs...</div>
            ) : error ? (
                <div className="p-4 text-red-600">Error: {error}</div>
            ) : (
                <div className="card">
                    <div className="table-container">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Employee</th>
                                    <th>Code</th>
                                    <th>Check In</th>
                                    <th>Check Out</th>
                                    <th>Status</th>
                                    <th>FACE MATCH PERCENTAGE</th>
                                </tr>
                            </thead>
                            <tbody>
                                {logs.length === 0 ? (
                                    <tr>
                                        <td colSpan={7} style={{ textAlign: 'center', padding: '3rem' }}>
                                            <div style={{ color: 'var(--text-muted)' }}>No attendance logs found matching filters</div>
                                        </td>
                                    </tr>
                                ) : (
                                    logs.map(log => (
                                        <tr key={log.id}>
                                            <td>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                    <Calendar size={14} className="text-muted" />
                                                    {formatDate(log.date)}
                                                </div>
                                            </td>
                                            <td>
                                                <div style={{ fontWeight: 500 }}>{log.employee_name}</div>
                                            </td>
                                            <td><span style={{ fontFamily: 'monospace' }}>{log.emp_code}</span></td>
                                            <td>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                    <Clock size={14} style={{ color: '#059669' }} />
                                                    {formatTime(log.check_in)}
                                                </div>
                                            </td>
                                            <td>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                    <Clock size={14} style={{ color: '#dc2626' }} />
                                                    {formatTime(log.check_out)}
                                                </div>
                                            </td>
                                            <td>
                                                <span className={`badge ${log.status === 'present' ? 'badge-success' : 'badge-warning'}`}>
                                                    {log.status.toUpperCase()}
                                                </span>
                                            </td>
                                            <td>
                                                {log.confidence ? (
                                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                                                        <div style={{ height: '4px', width: '100%', background: '#eee', borderRadius: '2px', overflow: 'hidden' }}>
                                                            <div style={{ height: '100%', width: `${log.confidence * 100}%`, background: log.confidence > 0.8 ? '#059669' : '#f59e0b' }}></div>
                                                        </div>
                                                        <span style={{ fontSize: '0.7rem' }}>{(log.confidence * 100).toFixed(1)}%</span>
                                                    </div>
                                                ) : '--'}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
