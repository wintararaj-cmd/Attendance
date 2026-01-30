import { useEffect, useState } from 'react';
import axios from 'axios';
import { Plus, Edit2, Trash2, Users, Building2, X } from 'lucide-react';

interface Department {
    id: string;
    name: string;
    description?: string;
    department_head?: string;
    status: string;
    employee_count: number;
    created_at?: string;
    updated_at?: string;
}

export default function DepartmentManagement() {
    const [departments, setDepartments] = useState<Department[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [editingDept, setEditingDept] = useState<Department | null>(null);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        department_head: '',
        status: 'active'
    });

    useEffect(() => {
        fetchDepartments();
    }, []);

    const fetchDepartments = async () => {
        try {
            const res = await axios.get('/api/v1/departments');
            setDepartments(res.data);
        } catch (err: any) {
            setError('Failed to fetch departments');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = () => {
        setEditingDept(null);
        setFormData({ name: '', description: '', department_head: '', status: 'active' });
        setShowModal(true);
    };

    const handleEdit = (dept: Department) => {
        setEditingDept(dept);
        setFormData({
            name: dept.name,
            description: dept.description || '',
            department_head: dept.department_head || '',
            status: dept.status
        });
        setShowModal(true);
    };

    const handleDelete = async (deptId: string) => {
        if (!confirm('Are you sure you want to delete this department?')) return;

        try {
            await axios.delete(`/api/v1/departments/${deptId}`);
            alert('Department deleted successfully');
            fetchDepartments();
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Failed to delete department');
            console.error(err);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            if (editingDept) {
                // Update
                await axios.put(`/api/v1/departments/${editingDept.id}`, formData);
                alert('Department updated successfully');
            } else {
                // Create
                await axios.post('/api/v1/departments', formData);
                alert('Department created successfully');
            }
            setShowModal(false);
            fetchDepartments();
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Operation failed');
            console.error(err);
        }
    };

    if (loading) return <div className="p-4">Loading departments...</div>;

    return (
        <div>
            <div className="page-header">
                <h2>Department Management</h2>
                <button onClick={handleCreate} className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Plus size={18} />
                    Add Department
                </button>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            {/* Stats Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                <div className="card" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <p style={{ margin: 0, opacity: 0.9, fontSize: '0.875rem' }}>Total Departments</p>
                            <h2 style={{ margin: '0.5rem 0 0 0', fontSize: '2rem' }}>{departments.length}</h2>
                        </div>
                        <Building2 size={48} style={{ opacity: 0.3 }} />
                    </div>
                </div>

                <div className="card" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <p style={{ margin: 0, opacity: 0.9, fontSize: '0.875rem' }}>Active Departments</p>
                            <h2 style={{ margin: '0.5rem 0 0 0', fontSize: '2rem' }}>
                                {departments.filter(d => d.status === 'active').length}
                            </h2>
                        </div>
                        <Building2 size={48} style={{ opacity: 0.3 }} />
                    </div>
                </div>

                <div className="card" style={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <p style={{ margin: 0, opacity: 0.9, fontSize: '0.875rem' }}>Total Employees</p>
                            <h2 style={{ margin: '0.5rem 0 0 0', fontSize: '2rem' }}>
                                {departments.reduce((sum, d) => sum + d.employee_count, 0)}
                            </h2>
                        </div>
                        <Users size={48} style={{ opacity: 0.3 }} />
                    </div>
                </div>
            </div>

            {/* Department Table */}
            <div className="card">
                <div className="table-container">
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Department Name</th>
                                <th>Description</th>
                                <th>Department Head</th>
                                <th>Employees</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {departments.length === 0 ? (
                                <tr>
                                    <td colSpan={6} style={{ textAlign: 'center', padding: '2rem' }}>
                                        <div style={{ color: 'var(--text-muted)' }}>No departments found</div>
                                    </td>
                                </tr>
                            ) : (
                                departments.map(dept => (
                                    <tr key={dept.id}>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                <Building2 size={18} style={{ color: 'var(--primary)' }} />
                                                <span style={{ fontWeight: 600 }}>{dept.name}</span>
                                            </div>
                                        </td>
                                        <td>
                                            <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                                {dept.description || '-'}
                                            </span>
                                        </td>
                                        <td>{dept.department_head || '-'}</td>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                <Users size={14} style={{ color: 'var(--text-muted)' }} />
                                                <span>{dept.employee_count}</span>
                                            </div>
                                        </td>
                                        <td>
                                            {dept.status === 'active' ? (
                                                <span className="badge badge-success">Active</span>
                                            ) : (
                                                <span className="badge badge-warning">Inactive</span>
                                            )}
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <button
                                                    onClick={() => handleEdit(dept)}
                                                    className="btn btn-sm"
                                                    style={{ padding: '0.375rem 0.75rem' }}
                                                    title="Edit"
                                                >
                                                    <Edit2 size={14} />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(dept.id)}
                                                    className="btn btn-sm"
                                                    style={{ padding: '0.375rem 0.75rem', background: '#fee2e2', color: '#dc2626' }}
                                                    title="Delete"
                                                >
                                                    <Trash2 size={14} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Create/Edit Modal */}
            {showModal && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0, 0, 0, 0.5)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000
                }}>
                    <div className="card" style={{ maxWidth: '600px', width: '90%', maxHeight: '90vh', overflow: 'auto' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <h3 style={{ margin: 0 }}>{editingDept ? 'Edit Department' : 'Create Department'}</h3>
                            <button
                                onClick={() => setShowModal(false)}
                                className="btn btn-sm"
                                style={{ padding: '0.5rem' }}
                            >
                                <X size={18} />
                            </button>
                        </div>

                        <form onSubmit={handleSubmit}>
                            <div style={{ display: 'grid', gap: '1rem' }}>
                                <div>
                                    <label>Department Name *</label>
                                    <input
                                        type="text"
                                        className="input"
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        required
                                        placeholder="e.g., IT, HR, Finance"
                                    />
                                </div>

                                <div>
                                    <label>Description</label>
                                    <textarea
                                        className="input"
                                        value={formData.description}
                                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                        placeholder="Brief description of the department"
                                        rows={3}
                                        style={{ resize: 'vertical' }}
                                    />
                                </div>

                                <div>
                                    <label>Department Head</label>
                                    <input
                                        type="text"
                                        className="input"
                                        value={formData.department_head}
                                        onChange={(e) => setFormData({ ...formData, department_head: e.target.value })}
                                        placeholder="Name of department head"
                                    />
                                </div>

                                <div>
                                    <label>Status</label>
                                    <select
                                        className="input"
                                        value={formData.status}
                                        onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                                    >
                                        <option value="active">Active</option>
                                        <option value="inactive">Inactive</option>
                                    </select>
                                </div>
                            </div>

                            <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', justifyContent: 'flex-end' }}>
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="btn"
                                    style={{ background: '#f3f4f6', color: '#374151' }}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                >
                                    {editingDept ? 'Update' : 'Create'} Department
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
