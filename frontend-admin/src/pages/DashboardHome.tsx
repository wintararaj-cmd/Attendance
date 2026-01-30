import { useEffect, useState } from 'react';
import axios from 'axios';
import { Users, UserCheck, UserX, Clock, Building2, Briefcase, TrendingUp } from 'lucide-react';

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

export default function DashboardHome() {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
        // Refresh stats every 30 seconds
        const interval = setInterval(fetchStats, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchStats = async () => {
        try {
            const res = await axios.get('/api/v1/dashboard/stats');
            setStats(res.data);
        } catch (err) {
            console.error("Failed to fetch dashboard stats", err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-4">Loading dashboard...</div>;

    const s = stats || {
        total_employees: 0,
        present_today: 0,
        absent_today: 0,
        late_count: 0,
        recent_activity: [],
        department_breakdown: [],
        employee_type_breakdown: []
    };

    // Calculate attendance percentage
    const attendancePercentage = s.total_employees > 0
        ? Math.round((s.present_today / s.total_employees) * 100)
        : 0;

    return (
        <div>
            <div className="page-header">
                <div>
                    <h2>Dashboard Overview</h2>
                    <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                        Welcome back! Here's what's happening today.
                    </p>
                </div>
            </div>

            {/* Main Stats */}
            <div className="grid-4" style={{ marginBottom: '2rem' }}>
                <div className="card stat-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                            <h3 style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontWeight: 500 }}>Total Employees</h3>
                            <div className="value" style={{ fontSize: '2rem', fontWeight: 700, marginTop: '0.5rem' }}>
                                {s.total_employees}
                            </div>
                        </div>
                        <div style={{ padding: '0.75rem', background: '#e0f2fe', borderRadius: '12px', color: '#0284c7' }}>
                            <Users size={24} />
                        </div>
                    </div>
                </div>

                <div className="card stat-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                            <h3 style={{ color: '#059669', fontSize: '0.875rem', fontWeight: 500 }}>Present Today</h3>
                            <div className="value" style={{ fontSize: '2rem', fontWeight: 700, marginTop: '0.5rem', color: '#059669' }}>
                                {s.present_today}
                            </div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                                {attendancePercentage}% attendance
                            </div>
                        </div>
                        <div style={{ padding: '0.75rem', background: '#d1fae5', borderRadius: '12px', color: '#059669' }}>
                            <UserCheck size={24} />
                        </div>
                    </div>
                </div>

                <div className="card stat-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                            <h3 style={{ color: '#dc2626', fontSize: '0.875rem', fontWeight: 500 }}>Absent Today</h3>
                            <div className="value" style={{ fontSize: '2rem', fontWeight: 700, marginTop: '0.5rem', color: '#dc2626' }}>
                                {s.absent_today}
                            </div>
                        </div>
                        <div style={{ padding: '0.75rem', background: '#fee2e2', borderRadius: '12px', color: '#dc2626' }}>
                            <UserX size={24} />
                        </div>
                    </div>
                </div>

                <div className="card stat-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                            <h3 style={{ color: '#7c3aed', fontSize: '0.875rem', fontWeight: 500 }}>Attendance Rate</h3>
                            <div className="value" style={{ fontSize: '2rem', fontWeight: 700, marginTop: '0.5rem', color: '#7c3aed' }}>
                                {attendancePercentage}%
                            </div>
                        </div>
                        <div style={{ padding: '0.75rem', background: '#ede9fe', borderRadius: '12px', color: '#7c3aed' }}>
                            <TrendingUp size={24} />
                        </div>
                    </div>
                </div>
            </div>

            {/* Department & Employee Type Breakdown */}
            <div className="grid-2" style={{ marginBottom: '2rem' }}>
                {/* Department Breakdown */}
                <div className="card">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                        <Building2 size={20} style={{ color: 'var(--primary)' }} />
                        <h3 style={{ margin: 0 }}>Department Distribution</h3>
                    </div>

                    {s.department_breakdown.length === 0 ? (
                        <div style={{ color: 'var(--text-muted)', padding: '2rem', textAlign: 'center', background: '#f9fafb', borderRadius: '8px' }}>
                            No department data available
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {s.department_breakdown.map((dept, idx) => {
                                const percentage = s.total_employees > 0
                                    ? Math.round((dept.count / s.total_employees) * 100)
                                    : 0;
                                const colors = ['#0284c7', '#059669', '#7c3aed', '#dc2626', '#ea580c', '#0891b2'];
                                const color = colors[idx % colors.length];

                                return (
                                    <div key={dept.department}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                            <span style={{ fontWeight: 500 }}>{dept.department}</span>
                                            <span style={{ color: 'var(--text-muted)' }}>{dept.count} ({percentage}%)</span>
                                        </div>
                                        <div style={{
                                            height: '8px',
                                            background: '#f3f4f6',
                                            borderRadius: '4px',
                                            overflow: 'hidden'
                                        }}>
                                            <div style={{
                                                height: '100%',
                                                width: `${percentage}%`,
                                                background: color,
                                                transition: 'width 0.3s ease'
                                            }} />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* Employee Type Breakdown */}
                <div className="card">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                        <Briefcase size={20} style={{ color: 'var(--primary)' }} />
                        <h3 style={{ margin: 0 }}>Employee Type Distribution</h3>
                    </div>

                    {s.employee_type_breakdown.length === 0 ? (
                        <div style={{ color: 'var(--text-muted)', padding: '2rem', textAlign: 'center', background: '#f9fafb', borderRadius: '8px' }}>
                            No employee type data available
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {s.employee_type_breakdown.map((type, idx) => {
                                const percentage = s.total_employees > 0
                                    ? Math.round((type.count / s.total_employees) * 100)
                                    : 0;
                                const colors = ['#0284c7', '#059669', '#ea580c', '#7c3aed'];
                                const color = colors[idx % colors.length];

                                return (
                                    <div key={type.type}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                            <span style={{ fontWeight: 500 }}>
                                                {type.type.replace('_', ' ').toUpperCase()}
                                            </span>
                                            <span style={{ color: 'var(--text-muted)' }}>{type.count} ({percentage}%)</span>
                                        </div>
                                        <div style={{
                                            height: '8px',
                                            background: '#f3f4f6',
                                            borderRadius: '4px',
                                            overflow: 'hidden'
                                        }}>
                                            <div style={{
                                                height: '100%',
                                                width: `${percentage}%`,
                                                background: color,
                                                transition: 'width 0.3s ease'
                                            }} />
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
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                    <Clock size={20} style={{ color: 'var(--primary)' }} />
                    <h3 style={{ margin: 0 }}>Recent Attendance Activity</h3>
                </div>

                {(s.recent_activity?.length || 0) === 0 ? (
                    <div style={{ color: 'var(--text-muted)', padding: '2rem', background: '#f9fafb', borderRadius: '8px', textAlign: 'center' }}>
                        No attendance logs today yet.
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
                                        <td style={{ fontWeight: 500 }}>{log.employee_name}</td>
                                        <td>
                                            <span style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                                                {log.emp_code}
                                            </span>
                                        </td>
                                        <td>
                                            {log.department ? (
                                                <span className="badge" style={{ background: '#e0f2fe', color: '#0284c7' }}>
                                                    {log.department}
                                                </span>
                                            ) : (
                                                <span style={{ color: 'var(--text-muted)' }}>-</span>
                                            )}
                                        </td>
                                        <td>{log.time}</td>
                                        <td>
                                            <span className={`badge ${log.status === 'present' ? 'badge-success' : 'badge-warning'}`}>
                                                {log.status.toUpperCase()}
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
