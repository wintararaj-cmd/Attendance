import { useEffect, useState } from 'react';
import axios from 'axios';
import { Calendar, Clock } from 'lucide-react';

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
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchLogs();
    }, []);

    const fetchLogs = async () => {
        try {
            setError(null);
            const res = await axios.get('/api/v1/attendance/logs');
            // Backend returns { logs: [...] }
            setLogs(res.data.logs || []);
        } catch (err: any) {
            console.error("Failed to fetch logs", err);
            setError(err.response?.data?.detail || err.message || "Failed to load logs");
        } finally {
            setLoading(false);
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

    if (loading) return <div className="p-4">Loading logs...</div>;
    if (error) return <div className="p-4 text-red-600">Error: {error}</div>;

    return (
        <div>
            <div className="page-header">
                <h2>Attendance Logs</h2>
                <div className="text-muted" style={{ fontSize: '0.875rem' }}>
                    Showing last 50 entries
                </div>
            </div>

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
                                        <div style={{ color: 'var(--text-muted)' }}>No attendance logs found</div>
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
        </div>
    );
}
