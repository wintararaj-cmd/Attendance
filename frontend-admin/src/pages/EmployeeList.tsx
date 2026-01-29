import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { Plus } from 'lucide-react';

interface Employee {
    id: string;
    emp_code: string;
    first_name: string;
    last_name?: string;
    mobile_no: string;
    is_face_registered: boolean;
}

export default function EmployeeList() {
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchEmployees();
    }, []);

    const fetchEmployees = async () => {
        try {
            const res = await axios.get('/api/v1/employees');
            setEmployees(res.data);
        } catch (err: any) {
            setError('Failed to fetch employees');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-4">Loading stats...</div>;

    return (
        <div>
            <div className="page-header">
                <h2>Employee List</h2>
                <Link to="/register" className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Plus size={18} />
                    Add Employee
                </Link>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <div className="card">
                <div className="table-container">
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Code</th>
                                <th>Name</th>
                                <th>Mobile</th>
                                <th>Face Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(employees?.length || 0) === 0 ? (
                                <tr>
                                    <td colSpan={4} style={{ textAlign: 'center', padding: '2rem' }}>
                                        <div style={{ color: 'var(--text-muted)' }}>No employees found</div>
                                    </td>
                                </tr>
                            ) : (
                                employees?.map(emp => (
                                    <tr key={emp.id}>
                                        <td>
                                            <span style={{ fontFamily: 'monospace', fontWeight: 600 }}>{emp.emp_code}</span>
                                        </td>
                                        <td>
                                            <div style={{ fontWeight: 500 }}>{emp.first_name} {emp.last_name || ''}</div>
                                        </td>
                                        <td>{emp.mobile_no}</td>
                                        <td>
                                            {emp.is_face_registered ?
                                                <span className="badge badge-success">Active</span> :
                                                <span className="badge badge-warning">Pending</span>}
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
