import { useEffect, useState } from 'react';
import axios from 'axios';
import {
    Users, UserCheck, UserX, Building2, Briefcase,
    Clock, RefreshCw, Activity, BarChart2
} from 'lucide-react';

interface DashboardStats {
    total_employees: number;
    present_today: number;
    absent_today: number;
    late_count: number;
    recent_activity: Array<{
        id: string;
        employee_name: string;
        emp_code: string;
        department?: string;
        time: string;
        status: string;
    }>;
    department_breakdown: Array<{
        department: string;
        count: number;
    }>;
    employee_type_breakdown: Array<{
        type: string;
        count: number;
    }>;
}

function LiveClock() {
    const [now, setNow] = useState(new Date());

    useEffect(() => {
        const t = setInterval(() => setNow(new Date()), 1000);
        return () => clearInterval(t);
    }, []);

    return (
        <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', fontVariantNumeric: 'tabular-nums' }}>
                {now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {now.toLocaleDateString([], { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
            </div>
        </div>
    );
}

const STAT_CONFIG = [
    {
        key: 'total_employees',
        label: 'Total Employees',
        icon: Users,
        color: '#6366f1',
        bg: 'rgba(99, 102, 241, 0.1)',
        sublabel: (s: DashboardStats) => `${s.department_breakdown?.length || 0} departments`,
    },
    {
        key: 'present_today',
        label: 'Present Today',
        icon: UserCheck,
        color: '#10b981',
        bg: 'rgba(16, 185, 129, 0.1)',
        sublabel: (s: DashboardStats) => {
            const pct = s.total_employees > 0
                ? Math.round((s.present_today / s.total_employees) * 100)
                : 0;
            return `${pct}% attendance rate`;
        },
    },
    {
        key: 'absent_today',
        label: 'Absent Today',
        icon: UserX,
        color: '#ef4444',
        bg: 'rgba(239, 68, 68, 0.1)',
        sublabel: (_s: DashboardStats) => 'Yet to check in',
    },
    {
        key: 'late_count',
        label: 'Late Arrivals',
        icon: Clock,
        color: '#f59e0b',
        bg: 'rgba(245, 158, 11, 0.1)',
        sublabel: (_s: DashboardStats) => 'Arrived after shift',
    },
];

const DEPT_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#0ea5e9', '#8b5cf6', '#ec4899'];
const TYPE_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#0ea5e9'];

export default function DashboardHome() {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    useEffect(() => {
        fetchStats();
        const interval = setInterval(fetchStats, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchStats = async (isManual = false) => {
        try {
            if (isManual) setRefreshing(true);
            const res = await axios.get('/api/v1/dashboard/stats');
            setStats(res.data);
        } catch (err) {
            console.error('Failed to fetch dashboard stats', err);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    if (loading) {
        return (
            <div className="loading-spinner">
                <div className="spinner" />
                <span>Loading dashboard…</span>
            </div>
        );
    }

    const s: DashboardStats = stats || {
        total_employees: 0,
        present_today: 0,
        absent_today: 0,
        late_count: 0,
        recent_activity: [],
        department_breakdown: [],
        employee_type_breakdown: [],
    };

    const attendancePct = s.total_employees > 0
        ? Math.round((s.present_today / s.total_employees) * 100)
        : 0;

    return (
        <div className="animate-fade-in">
            {/* Page Header */}
            <div className="page-header">
                <div>
                    <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                        <Activity size={22} style={{ color: 'var(--primary)' }} />
                        Dashboard
                    </h2>
                    <div className="page-header-subtitle">Real-time workforce overview</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
                    <LiveClock />
                    <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => fetchStats(true)}
                        disabled={refreshing}
                        style={{ gap: '0.375rem' }}
                    >
                        <RefreshCw size={14} style={{ animation: refreshing ? 'spin 0.7s linear infinite' : 'none' }} />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Attendance Progress Banner */}
            <div className="card" style={{
                marginBottom: '1.5rem',
                background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
                border: 'none',
                color: 'white',
                overflow: 'hidden',
                position: 'relative',
            }}>
                <div style={{
                    position: 'absolute', top: '-30px', right: '-30px',
                    width: '180px', height: '180px',
                    background: 'rgba(99, 102, 241, 0.12)',
                    borderRadius: '50%',
                    pointerEvents: 'none',
                }} />
                <div style={{
                    position: 'absolute', bottom: '-50px', left: '30%',
                    width: '200px', height: '200px',
                    background: 'rgba(16, 185, 129, 0.07)',
                    borderRadius: '50%',
                    pointerEvents: 'none',
                }} />

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative', zIndex: 1, flexWrap: 'wrap', gap: '1rem' }}>
                    <div>
                        <div style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.25rem' }}>
                            Today's Attendance Rate
                        </div>
                        <div style={{ fontSize: '2.5rem', fontWeight: 800, letterSpacing: '-1px', lineHeight: 1 }}>
                            {attendancePct}<span style={{ fontSize: '1.5rem', opacity: 0.7 }}>%</span>
                        </div>
                        <div style={{ color: '#94a3b8', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                            {s.present_today} out of {s.total_employees} employees checked in
                        </div>
                    </div>

                    <div style={{ flex: '0 0 280px', maxWidth: '280px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.75rem', color: '#94a3b8' }}>
                            <span>Present</span>
                            <span>Absent</span>
                        </div>
                        <div style={{ height: '10px', background: 'rgba(255,255,255,0.1)', borderRadius: '9999px', overflow: 'hidden' }}>
                            <div style={{
                                height: '100%',
                                width: `${attendancePct}%`,
                                background: 'linear-gradient(90deg, #6366f1, #10b981)',
                                borderRadius: '9999px',
                                transition: 'width 1s cubic-bezier(0.4, 0, 0.2, 1)',
                            }} />
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.75rem' }}>
                            <span style={{ color: '#6ee7b7', fontWeight: 600 }}>{s.present_today} Present</span>
                            <span style={{ color: '#fca5a5', fontWeight: 600 }}>{s.absent_today} Absent</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Stat Cards */}
            <div className="grid-4" style={{ marginBottom: '1.5rem' }}>
                {STAT_CONFIG.map(({ key, label, icon: Icon, color, bg, sublabel }) => {
                    const val = (s as any)[key] as number;
                    return (
                        <div key={key} className="card stat-card" style={{ marginBottom: 0 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div>
                                    <h3 style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', fontWeight: 500 }}>{label}</h3>
                                    <div className="value animate-count" style={{ color, marginTop: '0.375rem' }}>
                                        {val}
                                    </div>
                                    <div className="trend" style={{ color: 'var(--text-muted)', marginTop: '0.375rem' }}>
                                        {sublabel(s)}
                                    </div>
                                </div>
                                <div className="stat-card-icon" style={{ background: bg }}>
                                    <Icon size={20} style={{ color }} />
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Breakdown Section */}
            <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
                {/* Department Breakdown */}
                <div className="card" style={{ marginBottom: 0 }}>
                    <div className="card-header">
                        <div className="card-title">
                            <Building2 size={17} style={{ color: 'var(--primary)' }} />
                            Department Distribution
                        </div>
                        <span className="badge badge-info">
                            {s.department_breakdown?.length || 0} depts
                        </span>
                    </div>

                    {(s.department_breakdown?.length || 0) === 0 ? (
                        <div className="empty-state" style={{ padding: '1.5rem' }}>
                            <BarChart2 size={28} style={{ color: 'var(--text-faint)' }} />
                            <span>No department data yet</span>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                            {(s.department_breakdown || []).map((dept, idx) => {
                                const pct = s.total_employees > 0
                                    ? Math.round((dept.count / s.total_employees) * 100)
                                    : 0;
                                const color = DEPT_COLORS[idx % DEPT_COLORS.length];
                                return (
                                    <div key={dept.department}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.375rem' }}>
                                            <span style={{ fontWeight: 500, fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                                {dept.department}
                                            </span>
                                            <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                                                {dept.count} <span style={{ opacity: 0.6 }}>({pct}%)</span>
                                            </span>
                                        </div>
                                        <div className="progress-bar">
                                            <div
                                                className="progress-fill"
                                                style={{ width: `${pct}%`, background: color }}
                                            />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* Employee Type Breakdown */}
                <div className="card" style={{ marginBottom: 0 }}>
                    <div className="card-header">
                        <div className="card-title">
                            <Briefcase size={17} style={{ color: 'var(--primary)' }} />
                            Employment Types
                        </div>
                        <span className="badge badge-purple">
                            {s.employee_type_breakdown?.length || 0} types
                        </span>
                    </div>

                    {(s.employee_type_breakdown?.length || 0) === 0 ? (
                        <div className="empty-state" style={{ padding: '1.5rem' }}>
                            <BarChart2 size={28} style={{ color: 'var(--text-faint)' }} />
                            <span>No type data yet</span>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                            {(s.employee_type_breakdown || []).map((item, idx) => {
                                const pct = s.total_employees > 0
                                    ? Math.round((item.count / s.total_employees) * 100)
                                    : 0;
                                const color = TYPE_COLORS[idx % TYPE_COLORS.length];
                                const label = item.type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                                return (
                                    <div key={item.type}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.375rem' }}>
                                            <span style={{ fontWeight: 500, fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                                {label}
                                            </span>
                                            <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                                                {item.count} <span style={{ opacity: 0.6 }}>({pct}%)</span>
                                            </span>
                                        </div>
                                        <div className="progress-bar">
                                            <div
                                                className="progress-fill"
                                                style={{ width: `${pct}%`, background: color }}
                                            />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            </div>

            {/* Recent Activity */}
            <div className="card">
                <div className="card-header">
                    <div className="card-title">
                        <Clock size={17} style={{ color: 'var(--primary)' }} />
                        Recent Attendance Activity
                    </div>
                    <span className="badge badge-gray">{s.recent_activity?.length || 0} records</span>
                </div>

                {(s.recent_activity?.length || 0) === 0 ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">
                            <Clock size={24} />
                        </div>
                        <div className="empty-state-title">No activity yet</div>
                        <div className="empty-state-desc">Attendance logs for today will appear here</div>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Employee</th>
                                    <th>Code</th>
                                    <th>Department</th>
                                    <th>Time</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {(Array.isArray(s.recent_activity) ? s.recent_activity : []).map((log) => (
                                    <tr key={log.id}>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                                                <div style={{
                                                    width: '30px', height: '30px',
                                                    borderRadius: '50%',
                                                    background: `hsl(${log.employee_name.charCodeAt(0) * 5 % 360}, 65%, 90%)`,
                                                    color: `hsl(${log.employee_name.charCodeAt(0) * 5 % 360}, 65%, 35%)`,
                                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                    fontWeight: 700, fontSize: '0.75rem', flexShrink: 0,
                                                }}>
                                                    {log.employee_name.charAt(0).toUpperCase()}
                                                </div>
                                                <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{log.employee_name}</span>
                                            </div>
                                        </td>
                                        <td>
                                            <span style={{ fontFamily: 'monospace', fontSize: '0.8125rem', background: '#f1f5f9', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                                                {log.emp_code}
                                            </span>
                                        </td>
                                        <td>
                                            {log.department ? (
                                                <span className="badge badge-info">{log.department}</span>
                                            ) : (
                                                <span style={{ color: 'var(--text-faint)' }}>—</span>
                                            )}
                                        </td>
                                        <td style={{ color: 'var(--text-secondary)', fontVariantNumeric: 'tabular-nums' }}>
                                            {log.time}
                                        </td>
                                        <td>
                                            <span className={`badge ${log.status === 'present' ? 'badge-success' : 'badge-warning'}`}>
                                                <span style={{
                                                    width: '6px', height: '6px', borderRadius: '50%',
                                                    background: log.status === 'present' ? '#10b981' : '#f59e0b',
                                                    display: 'inline-block',
                                                }} />
                                                {log.status.charAt(0).toUpperCase() + log.status.slice(1)}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
