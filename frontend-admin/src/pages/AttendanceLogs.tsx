import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Calendar, Clock, Download, Filter, Search, RefreshCw, X, FileText, Edit2 } from 'lucide-react';

interface AttendanceLog {
    id: string;
    employee_name: string;
    emp_code: string;
    department: string;
    date: string;
    check_in: string | null;
    check_out: string | null;
    status: string;
    confidence: number | null;
    ot_hours: number;
    ot_weekend_hours: number;
    ot_holiday_hours: number;
    total_hours_worked: number;
}

type ViewMode = 'all' | 'by_employee' | 'by_department';

const STATUS_BADGE: Record<string, string> = {
    present: 'badge-success',
    absent: 'badge-danger',
    late: 'badge-warning',
    half_day: 'badge-warning',
    weekly_off: 'badge-gray',
    holiday: 'badge-info',
};

export default function AttendanceLogs() {
    const [logs, setLogs] = useState<AttendanceLog[]>([]);
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(50);
    const [totalRecords, setTotalRecords] = useState(0);
    const [totalPages, setTotalPages] = useState(0);
    const [searchTerm, setSearchTerm] = useState('');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [loading, setLoading] = useState(true);
    const [exporting, setExporting] = useState(false);
    const [syncing, setSyncing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [successMsg, setSuccessMsg] = useState<string | null>(null);
    const [editingLog, setEditingLog] = useState<AttendanceLog | null>(null);
    const [editForm, setEditForm] = useState({
        check_in: '',
        check_out: '',
        status: '',
        ot_hours: 0,
        ot_weekend_hours: 0,
        ot_holiday_hours: 0
    });
    const [savingEdit, setSavingEdit] = useState(false);
    const [viewMode, setViewMode] = useState<ViewMode>('all');
    const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());

    useEffect(() => { fetchLogs(1); }, []);

    const showSuccess = (msg: string) => {
        setSuccessMsg(msg);
        setTimeout(() => setSuccessMsg(null), 3000);
    };

    const fetchLogs = async (pageToFetch = page) => {
        try {
            setLoading(true);
            setError(null);
            const params: Record<string, any> = {
                page: pageToFetch,
                page_size: pageSize
            };
            if (searchTerm) params.search = searchTerm;
            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;
            
            const res = await axios.get('/api/v1/attendance/logs', { params });
            setLogs(res.data.logs || []);
            setTotalRecords(res.data.total || 0);
            setTotalPages(res.data.total_pages || 0);
            setPage(res.data.page || 1);
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Failed to load logs');
        } finally {
            setLoading(false);
        }
    };

    const handlePageChange = (newPage: number) => {
        if (newPage >= 1 && newPage <= totalPages) {
            fetchLogs(newPage);
        }
    };

    const handleClearFilters = () => {
        setSearchTerm('');
        setStartDate('');
        setEndDate('');
        setPage(1);
        setTimeout(() => fetchLogs(1), 0);
    };

    const handleExport = async () => {
        try {
            setExporting(true);
            const params: Record<string, string> = {};
            if (searchTerm) params.search = searchTerm;
            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;
            const response = await axios.get('/api/v1/attendance/export', {
                params,
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `attendance_${new Date().toISOString().split('T')[0]}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            showSuccess('Export downloaded successfully');
        } catch (err: any) {
            alert('Export Error: ' + (err.response?.data?.detail || 'Failed to export'));
        } finally {
            setExporting(false);
        }
    };

    const handleSyncHours = async () => {
        if (!confirm('Recalculate total hours for the last 30 days? This will apply the 30-min break deduction to all existing logs.')) return;
        try {
            setSyncing(true);
            const res = await axios.post('/api/v1/debug/recalculate-hours', {}, { params: { days: 30 } });
            showSuccess(res.data.message || 'Hours synced successfully');
            fetchLogs();
        } catch (err: any) {
            alert('Error: ' + (err.response?.data?.detail || err.message));
        } finally {
            setSyncing(false);
        }
    };

    const handleOpenEdit = (log: AttendanceLog) => {
        setEditingLog(log);
        setEditForm({
            check_in: log.check_in || '',
            check_out: log.check_out || '',
            status: log.status || 'present',
            ot_hours: log.ot_hours || 0,
            ot_weekend_hours: log.ot_weekend_hours || 0,
            ot_holiday_hours: log.ot_holiday_hours || 0
        });
    };

    const handleSaveEdit = async () => {
        if (!editingLog) return;
        try {
            setSavingEdit(true);
            const updateData: any = {};
            if (editForm.check_in !== (editingLog.check_in || '')) {
                updateData.check_in = editForm.check_in || null;
            }
            if (editForm.check_out !== (editingLog.check_out || '')) {
                updateData.check_out = editForm.check_out || null;
            }
            if (editForm.status !== editingLog.status) {
                updateData.status = editForm.status;
            }
            if (editForm.ot_hours !== editingLog.ot_hours) {
                updateData.ot_hours = editForm.ot_hours;
            }
            if (editForm.ot_weekend_hours !== editingLog.ot_weekend_hours) {
                updateData.ot_weekend_hours = editForm.ot_weekend_hours;
            }
            if (editForm.ot_holiday_hours !== editingLog.ot_holiday_hours) {
                updateData.ot_holiday_hours = editForm.ot_holiday_hours;
            }
            
            await axios.put(`/api/v1/attendance/logs/${editingLog.id}`, updateData);
            showSuccess('Attendance log updated successfully');
            setEditingLog(null);
            fetchLogs();
        } catch (err: any) {
            alert('Error: ' + (err.response?.data?.detail || err.message));
        } finally {
            setSavingEdit(false);
        }
    };

    const formatTime = (timeStr: string | null) => timeStr || '—';
    const formatDate = (isoString: string) => {
        if (!isoString) return '';
        return new Date(isoString).toLocaleDateString([], { day: '2-digit', month: 'short', year: 'numeric' });
    };

    const hasFilters = searchTerm || startDate || endDate;

    const toggleGroup = (key: string) => {
        setExpandedGroups(prev => {
            const next = new Set(prev);
            if (next.has(key)) next.delete(key);
            else next.add(key);
            return next;
        });
    };

    const renderLogRow = (log: AttendanceLog) => {
        const totalOT = (log.ot_hours || 0) + (log.ot_weekend_hours || 0) + (log.ot_holiday_hours || 0);
        const confidencePct = log.confidence ? Math.round(log.confidence * 100) : null;
        const badgeClass = STATUS_BADGE[log.status] || 'badge-gray';
        
        // Check if it's a Sunday
        const isSunday = new Date(log.date).getUTCDay() === 0;

        return (
            <tr key={log.id} style={{ backgroundColor: isSunday ? '#fff7f7' : undefined }}>
                <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Calendar size={13} style={{ color: isSunday ? '#ef4444' : 'var(--text-faint)', flexShrink: 0 }} />
                        <span style={{ fontWeight: 600, color: isSunday ? '#ef4444' : 'var(--text-main)' }}>
                            {formatDate(log.date)}
                        </span>
                    </div>
                </td>
                <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                        <div style={{
                            width: '28px', height: '28px', borderRadius: '50%',
                            background: `hsl(${log.employee_name.charCodeAt(0) * 5 % 360}, 65%, 90%)`,
                            color: `hsl(${log.employee_name.charCodeAt(0) * 5 % 360}, 65%, 35%)`,
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontWeight: 700, fontSize: '0.7rem', flexShrink: 0,
                        }}>
                            {log.employee_name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                            <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{log.employee_name}</div>
                            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                                {log.emp_code}
                            </div>
                        </div>
                    </div>
                </td>
                <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Clock size={13} style={{ color: '#10b981' }} />
                        <span style={{ fontVariantNumeric: 'tabular-nums', color: log.check_in ? 'var(--text-secondary)' : 'var(--text-faint)' }}>
                            {formatTime(log.check_in)}
                        </span>
                    </div>
                </td>
                <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Clock size={13} style={{ color: '#ef4444' }} />
                        <span style={{ fontVariantNumeric: 'tabular-nums', color: log.check_out ? 'var(--text-secondary)' : 'var(--text-faint)' }}>
                            {formatTime(log.check_out)}
                        </span>
                    </div>
                </td>
                <td>
                    <span className={`badge ${badgeClass}`} style={{ display: 'inline-flex', gap: '0.3rem', alignItems: 'center' }}>
                        <span style={{
                            width: '5px', height: '5px', borderRadius: '50%',
                            background: 'currentColor', opacity: 0.7,
                            display: 'inline-block',
                        }} />
                        {log.status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                    </span>
                </td>
                <td>
                    {log.total_hours_worked > 0 ? (
                        <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                            {log.total_hours_worked} <span style={{ fontWeight: 400, color: 'var(--text-muted)', fontSize: '0.75rem' }}>hrs</span>
                        </span>
                    ) : (
                        <span style={{ color: 'var(--text-faint)' }}>—</span>
                    )}
                </td>
                <td>
                    {totalOT > 0 ? (
                        <div style={{ fontSize: '0.78rem', display: 'flex', flexDirection: 'column', gap: '2px' }}>
                            {log.ot_hours > 0 && (
                                <span className="badge badge-purple" style={{ width: 'fit-content' }}>
                                    {log.ot_hours}h Reg
                                </span>
                            )}
                            {log.ot_weekend_hours > 0 && (
                                <span className="badge badge-info" style={{ width: 'fit-content' }}>
                                    {log.ot_weekend_hours}h Wknd
                                </span>
                            )}
                            {log.ot_holiday_hours > 0 && (
                                <span className="badge badge-warning" style={{ width: 'fit-content' }}>
                                    {log.ot_holiday_hours}h Hol
                                </span>
                            )}
                        </div>
                    ) : (
                        <span style={{ color: 'var(--text-faint)' }}>—</span>
                    )}
                </td>
                <td>
                    {confidencePct !== null ? (
                        <div style={{ minWidth: '70px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                                <span style={{
                                    fontSize: '0.72rem', fontWeight: 600,
                                    color: confidencePct >= 80 ? '#059669' : '#d97706',
                                }}>
                                    {confidencePct}%
                                </span>
                            </div>
                            <div style={{ height: '4px', background: '#f1f5f9', borderRadius: '9999px', overflow: 'hidden' }}>
                                <div style={{
                                    height: '100%',
                                    width: `${confidencePct}%`,
                                    background: confidencePct >= 80 ? '#10b981' : '#f59e0b',
                                    borderRadius: '9999px',
                                }} />
                            </div>
                        </div>
                    ) : (
                        <span style={{ color: 'var(--text-faint)' }}>—</span>
                    )}
                </td>
                <td>
                    <button
                        className="btn btn-ghost"
                        style={{ padding: '0.375rem' }}
                        onClick={() => handleOpenEdit(log)}
                        title="Edit"
                    >
                        <Edit2 size={14} />
                    </button>
                </td>
            </tr>
        );
    };

    const getGroupedLogs = () => {
        if (viewMode === 'all') return null;
        const groups: Record<string, AttendanceLog[]> = {};
        for (const log of logs) {
            const key = viewMode === 'by_employee' ? log.emp_code : log.department;
            if (!groups[key]) groups[key] = [];
            groups[key].push(log);
        }
        return groups;
    };

    const groupedLogs = getGroupedLogs();

    return (
        <div className="animate-fade-in">
            {/* Page Header */}
            <div className="page-header">
                <div>
                    <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                        <FileText size={22} style={{ color: 'var(--primary)' }} />
                        Attendance Logs
                    </h2>
                    <div className="page-header-subtitle">View, filter and export attendance records</div>
                </div>
                <div style={{ display: 'flex', gap: '0.625rem' }}>
                    <button
                        className="btn btn-ghost btn-sm"
                        onClick={handleSyncHours}
                        disabled={syncing}
                        style={{ gap: '0.375rem' }}
                    >
                        <RefreshCw size={14} style={{ animation: syncing ? 'spin 0.7s linear infinite' : 'none' }} />
                        {syncing ? 'Syncing…' : 'Sync Hours'}
                    </button>
                    <button
                        className="btn btn-success btn-sm"
                        onClick={handleExport}
                        disabled={exporting}
                    >
                        <Download size={14} />
                        {exporting ? 'Exporting…' : 'Export CSV'}
                    </button>
                </div>
            </div>

            {/* Alerts */}
            {successMsg && (
                <div className="alert alert-success" style={{ marginBottom: '1rem' }}>
                    ✓ {successMsg}
                </div>
            )}
            {error && (
                <div className="alert alert-error" style={{ marginBottom: '1rem' }}>
                    {error}
                </div>
            )}

            {/* Filter Bar */}
            <div className="card" style={{ marginBottom: '1.25rem', padding: '1.25rem' }}>
                <div style={{ display: 'flex', gap: '0.875rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                    {/* Search */}
                    <div style={{ flex: '1 1 220px' }}>
                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>
                            Search Employee
                        </label>
                        <div style={{ position: 'relative' }}>
                            <Search size={15} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-faint)' }} />
                            <input
                                type="search"
                                placeholder="Name or code…"
                                value={searchTerm}
                                onChange={(e) => { 
                                    setSearchTerm(e.target.value);
                                    setPage(1); // Reset page on type
                                }}
                                onKeyDown={(e) => e.key === 'Enter' && fetchLogs(1)}
                                style={{ paddingLeft: '2.25rem' }}
                            />
                        </div>
                    </div>

                    {/* Start Date */}
                    <div style={{ flex: '0 0 160px' }}>
                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>
                            From Date
                        </label>
                        <div style={{ position: 'relative' }}>
                            <Calendar size={15} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-faint)' }} />
                            <input
                                type="date"
                                value={startDate}
                                onChange={(e) => {
                                    setStartDate(e.target.value);
                                    setPage(1);
                                }}
                                style={{ paddingLeft: '2.25rem' }}
                            />
                        </div>
                    </div>

                    {/* End Date */}
                    <div style={{ flex: '0 0 160px' }}>
                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>
                            To Date
                        </label>
                        <div style={{ position: 'relative' }}>
                            <Calendar size={15} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-faint)' }} />
                            <input
                                type="date"
                                value={endDate}
                                onChange={(e) => {
                                    setEndDate(e.target.value);
                                    setPage(1);
                                }}
                                style={{ paddingLeft: '2.25rem' }}
                            />
                        </div>
                    </div>

                    {/* Actions */}
                    <div style={{ display: 'flex', gap: '0.5rem', paddingBottom: '1px' }}>
                        <button className="btn btn-primary" onClick={() => { setPage(1); fetchLogs(1); }}>
                            <Filter size={15} />
                            Filter
                        </button>
                        {hasFilters && (
                            <button className="btn btn-ghost" onClick={handleClearFilters} title="Clear filters">
                                <X size={15} />
                                Clear
                            </button>
                        )}
                    </div>
                </div>

                {/* Results count */}
                {!loading && (
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.875rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                        <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                            Showing <strong style={{ color: 'var(--text-main)' }}>
                                {logs.length > 0 ? (page - 1) * pageSize + 1 : 0} - {logs.length > 0 ? (page - 1) * pageSize + logs.length : 0}
                            </strong> of <strong style={{ color: 'var(--text-main)' }}>{totalRecords}</strong> records
                            {hasFilters && ' (filtered)'}
                        </div>
                        <div style={{ display: 'flex', gap: '0.25rem' }}>
                            {([
                                { key: 'all' as ViewMode, label: 'All Records' },
                                { key: 'by_employee' as ViewMode, label: 'Group by Employee' },
                                { key: 'by_department' as ViewMode, label: 'Group by Department' },
                            ]).map(opt => (
                                <button
                                    key={opt.key}
                                    className={`btn btn-sm ${viewMode === opt.key ? 'btn-primary' : 'btn-ghost'}`}
                                    onClick={() => { setViewMode(opt.key); setExpandedGroups(new Set()); }}
                                >
                                    {opt.label}
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Table */}
            {loading ? (
                <div className="loading-spinner">
                    <div className="spinner" />
                    <span>Loading attendance logs…</span>
                </div>
            ) : (
                <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                    <div className="table-container">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Employee</th>
                                    <th>Check In</th>
                                    <th>Check Out</th>
                                    <th>Status</th>
                                    <th>Hours</th>
                                    <th>OT</th>
                                    <th>Face Match</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {logs.length === 0 ? (
                                    <tr>
                                        <td colSpan={9}>
                                            <div className="empty-state">
                                                <div className="empty-state-icon">
                                                    <FileText size={24} />
                                                </div>
                                                <div className="empty-state-title">No records found</div>
                                                <div className="empty-state-desc">
                                                    {hasFilters ? 'Try adjusting your filters' : 'No attendance logs available'}
                                                </div>
                                            </div>
                                        </td>
                                    </tr>
                                ) : viewMode === 'all' ? (
                                    logs.map((log) => renderLogRow(log))
                                ) : (
                                    Object.entries(groupedLogs || {}).map(([groupKey, groupLogs]) => (
                                        <React.Fragment key={groupKey}>
                                            <tr 
                                                className="group-header" 
                                                onClick={() => toggleGroup(groupKey)}
                                                style={{ cursor: 'pointer', backgroundColor: 'var(--bg-hover)', fontWeight: 600 }}
                                            >
                                                <td colSpan={9} style={{ padding: '0.875rem 1rem', borderBottom: '2px solid var(--border-light)' }}>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
                                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', minWidth: '280px' }}>
                                                            <span style={{ 
                                                                transform: expandedGroups.has(groupKey) ? 'rotate(90deg)' : 'rotate(0deg)',
                                                                transition: 'transform 0.2s',
                                                                color: 'var(--text-faint)', fontSize: '0.7rem'
                                                            }}>
                                                                ▶
                                                            </span>
                                                            {viewMode === 'by_employee' ? (
                                                                <div>
                                                                    <div style={{ color: 'var(--text-main)', fontSize: '0.9rem' }}>{groupLogs[0].employee_name}</div>
                                                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Code: {groupKey}</div>
                                                                </div>
                                                            ) : (
                                                                <div style={{ color: 'var(--text-main)', fontSize: '1rem' }}>{groupKey}</div>
                                                            )}
                                                        </div>

                                                        {/* Summary Stats for the current results */}
                                                        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                                                            <div className="badge badge-gray" style={{ background: '#f0fdf4', color: '#166534', border: '1px solid #bbf7d0' }}>
                                                                Present: <strong style={{ marginLeft: '4px' }}>{groupLogs.filter(l => l.status === 'present').length}</strong>
                                                            </div>
                                                            <div className="badge badge-gray" style={{ background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca' }}>
                                                                Absent: <strong style={{ marginLeft: '4px' }}>{groupLogs.filter(l => l.status === 'absent').length}</strong>
                                                            </div>
                                                            <div className="badge badge-gray" style={{ background: '#faf5ff', color: '#6b21a8', border: '1px solid #e9d5ff' }}>
                                                                Total OT: <strong style={{ marginLeft: '4px' }}>
                                                                    {groupLogs.reduce((sum, l) => sum + (l.ot_hours || 0) + (l.ot_weekend_hours || 0) + (l.ot_holiday_hours || 0), 0).toFixed(1)}h
                                                                </strong>
                                                            </div>
                                                        </div>

                                                        <span className="badge badge-gray" style={{ marginLeft: 'auto', fontWeight: 500, opacity: 0.7 }}>
                                                            {groupLogs.length} Records
                                                        </span>
                                                    </div>
                                                </td>
                                            </tr>
                                            {expandedGroups.has(groupKey) && groupLogs.map(log => renderLogRow(log))}
                                        </React.Fragment>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                    {/* Pagination Footer */}
                    {!loading && totalPages > 1 && (
                        <div style={{ padding: '0.875rem 1.25rem', borderTop: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: 'var(--bg-card)' }}>
                            <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                                Page <strong style={{ color: 'var(--text-main)' }}>{page}</strong> of <strong style={{ color: 'var(--text-main)' }}>{totalPages}</strong>
                            </div>
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                <button 
                                    className="btn btn-ghost btn-sm" 
                                    onClick={() => handlePageChange(page - 1)}
                                    disabled={page === 1}
                                    style={{ padding: '0.4rem 0.8rem' }}
                                >
                                    Previous
                                </button>
                                
                                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                    let p: number;
                                    if (totalPages <= 5) p = i + 1;
                                    else if (page <= 3) p = i + 1;
                                    else if (page >= totalPages - 2) p = totalPages - 4 + i;
                                    else p = page - 2 + i;
                                    
                                    return (
                                        <button
                                            key={p}
                                            className={`btn btn-sm ${page === p ? 'btn-primary' : 'btn-ghost'}`}
                                            onClick={() => handlePageChange(p)}
                                            style={{ minWidth: '32px', padding: 0 }}
                                        >
                                            {p}
                                        </button>
                                    );
                                })}

                                <button 
                                    className="btn btn-ghost btn-sm" 
                                    onClick={() => handlePageChange(page + 1)}
                                    disabled={page === totalPages}
                                    style={{ padding: '0.4rem 0.8rem' }}
                                >
                                    Next
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Edit Modal */}
            {editingLog && (
                <div className="modal-overlay" onClick={() => setEditingLog(null)}>
                    <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '450px' }}>
                        <div className="modal-header">
                            <h3>Edit Attendance</h3>
                            <button className="btn btn-ghost" onClick={() => setEditingLog(null)}>
                                <X size={18} />
                            </button>
                        </div>
                        <div className="modal-body">
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>
                                    Employee
                                </label>
                                <div style={{ fontWeight: 500 }}>{editingLog.employee_name}</div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{editingLog.date}</div>
                            </div>
                            
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>
                                        Check In (HH:MM AM/PM)
                                    </label>
                                    <input
                                        type="text"
                                        className="input"
                                        value={editForm.check_in}
                                        onChange={(e) => setEditForm({ ...editForm, check_in: e.target.value })}
                                        placeholder="e.g., 09:00 AM"
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>
                                        Check Out (HH:MM AM/PM)
                                    </label>
                                    <input
                                        type="text"
                                        className="input"
                                        value={editForm.check_out}
                                        onChange={(e) => setEditForm({ ...editForm, check_out: e.target.value })}
                                        placeholder="e.g., 06:00 PM"
                                    />
                                </div>
                            </div>
                            
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>
                                    Status
                                </label>
                                <select
                                    className="input"
                                    value={editForm.status}
                                    onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                                >
                                    <option value="present">Present</option>
                                    <option value="absent">Absent</option>
                                    <option value="late">Late</option>
                                    <option value="half_day">Half Day</option>
                                </select>
                            </div>
                            
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem' }}>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>
                                        OT Hours
                                    </label>
                                    <input
                                        type="number"
                                        className="input"
                                        value={editForm.ot_hours}
                                        onChange={(e) => setEditForm({ ...editForm, ot_hours: Number(e.target.value) })}
                                        min="0"
                                        step="0.5"
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>
                                        OT Weekend
                                    </label>
                                    <input
                                        type="number"
                                        className="input"
                                        value={editForm.ot_weekend_hours}
                                        onChange={(e) => setEditForm({ ...editForm, ot_weekend_hours: Number(e.target.value) })}
                                        min="0"
                                        step="0.5"
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>
                                        OT Holiday
                                    </label>
                                    <input
                                        type="number"
                                        className="input"
                                        value={editForm.ot_holiday_hours}
                                        onChange={(e) => setEditForm({ ...editForm, ot_holiday_hours: Number(e.target.value) })}
                                        min="0"
                                        step="0.5"
                                    />
                                </div>
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-ghost" onClick={() => setEditingLog(null)}>
                                Cancel
                            </button>
                            <button className="btn btn-primary" onClick={handleSaveEdit} disabled={savingEdit}>
                                {savingEdit ? 'Saving...' : 'Save Changes'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
