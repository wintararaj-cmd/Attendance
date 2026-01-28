import { useEffect, useState } from 'react';
import axios from 'axios';
import { Users, UserCheck, UserX, Clock } from 'lucide-react';

interface DashboardStats {
    total_employees: number;
    present_today: number;
    absent_today: number;
    late_count: number;
    recent_activity: Array<{
        id: string;
        employee_name: string;
        time: string;
        status: string;
    }>;
}

export default function DashboardHome() {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
        // Refresh stats every 15 seconds for "real-time" feel
        const interval = setInterval(fetchStats, 15000);
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

    const s = stats || { total_employees: 0, present_today: 0, absent_today: 0, late_count: 0, recent_activity: [] };

    return (
        <div>
            <div className="page-header">
                <h2>Dashboard Overview</h2>
            </div>

            <div className="grid-3">
                <div className="card stat-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                            <h3>Total Employees</h3>
                            <div className="value">{s.total_employees}</div>
                        </div>
                        <div style={{ padding: '0.5rem', background: '#e0f2fe', borderRadius: '8px', color: '#0284c7' }}>
                            <Users size={24} />
                        </div>
                    </div>
                </div>

                <div className="card stat-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                            <h3 style={{ color: '#059669' }}>Present Today</h3>
                            <div className="value">{s.present_today}</div>
                        </div>
                        <div style={{ padding: '0.5rem', background: '#d1fae5', borderRadius: '8px', color: '#059669' }}>
                            <UserCheck size={24} />
                        </div>
                    </div>
                </div>

                <div className="card stat-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                            <h3 style={{ color: '#dc2626' }}>Absent / Late</h3>
                            <div className="value">{s.absent_today}</div>
                        </div>
                        <div style={{ padding: '0.5rem', background: '#fee2e2', borderRadius: '8px', color: '#dc2626' }}>
                            <UserX size={24} />
                        </div>
                    </div>
                </div>
            </div>

            <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                    <Clock size={20} className="text-muted" />
                    <h3 style={{ margin: 0 }}>Recent Activity</h3>
                </div>

                {s.recent_activity.length === 0 ? (
                    <div style={{ color: 'var(--text-muted)', padding: '1rem', background: '#f9fafb', borderRadius: '8px', textAlign: 'center' }}>
                        No attendance logs today yet.
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Time</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {s.recent_activity.map((log) => (
                                    <tr key={log.id}>
                                        <td style={{ fontWeight: 500 }}>{log.employee_name}</td>
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
