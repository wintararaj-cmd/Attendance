import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { Plus, Edit2, Trash2, Search, Building2, Briefcase, Users, X, CheckCircle } from 'lucide-react';

interface Employee {
    id: string;
    emp_code: string;
    first_name: string;
    last_name?: string;
    full_name: string;
    mobile_no: string;
    email?: string;
    department?: string;
    designation?: string;
    employee_type?: string;
    joining_date?: string;
    status: string;
    is_face_registered: boolean;
}

export default function EmployeeList() {
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [filteredEmployees, setFilteredEmployees] = useState<Employee[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Filters
    const [searchTerm, setSearchTerm] = useState('');
    const [departmentFilter, setDepartmentFilter] = useState('');
    const [employeeTypeFilter, setEmployeeTypeFilter] = useState('');
    const [statusFilter, setStatusFilter] = useState('active');

    // Edit Modal
    const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);
    const [showEditModal, setShowEditModal] = useState(false);

    useEffect(() => {
        fetchEmployees();
    }, []);

    useEffect(() => {
        filterEmployees();
    }, [employees, searchTerm, departmentFilter, employeeTypeFilter, statusFilter]);

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

    const filterEmployees = () => {
        let filtered = employees;

        // Search filter
        if (searchTerm) {
            filtered = filtered.filter(emp =>
                emp.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                emp.emp_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
                emp.mobile_no.includes(searchTerm)
            );
        }

        // Department filter
        if (departmentFilter) {
            filtered = filtered.filter(emp => emp.department === departmentFilter);
        }

        // Employee type filter
        if (employeeTypeFilter) {
            filtered = filtered.filter(emp => emp.employee_type === employeeTypeFilter);
        }

        // Status filter
        if (statusFilter) {
            filtered = filtered.filter(emp => emp.status === statusFilter);
        }

        setFilteredEmployees(filtered);
    };

    const handleEdit = (employee: Employee) => {
        setEditingEmployee(employee);
        setShowEditModal(true);
    };

    const handleDelete = async (empId: string) => {
        if (!confirm('Are you sure you want to deactivate this employee?')) return;

        try {
            await axios.delete(`/api/v1/employees/${empId}`);
            alert('Employee deactivated successfully');
            fetchEmployees();
        } catch (err) {
            alert('Failed to deactivate employee');
            console.error(err);
        }
    };

    const handleSaveEdit = async () => {
        if (!editingEmployee) return;

        try {
            await axios.put(`/api/v1/employees/${editingEmployee.id}`, editingEmployee);
            alert('Employee updated successfully');
            setShowEditModal(false);
            fetchEmployees();
        } catch (err) {
            alert('Failed to update employee');
            console.error(err);
        }
    };

    // Get unique departments and types for filters
    const departments = Array.from(new Set((employees || []).map(e => e.department).filter(Boolean)));
    const employeeTypes = Array.from(new Set((employees || []).map(e => e.employee_type).filter(Boolean)));

    if (loading) return (
        <div className="loading-spinner">
            <div className="spinner" />
            <span>Loading employees…</span>
        </div>
    );

    return (
        <div>
            <div className="page-header">
                <div>
                    <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                        <Users size={22} style={{ color: 'var(--primary)' }} />
                        Employee Management
                    </h2>
                    <div className="page-header-subtitle">
                        {employees.length} total · {filteredEmployees.length} shown
                    </div>
                </div>
                <Link to="/register" className="btn btn-primary">
                    <Plus size={16} />
                    Add Employee
                </Link>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            {/* Filters */}
            <div className="card" style={{ marginBottom: '1.25rem', padding: '1.25rem' }}>
                <div style={{ display: 'flex', gap: '0.875rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                    <div style={{ flex: '1 1 200px' }}>
                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>Search</label>
                        <div style={{ position: 'relative' }}>
                            <Search size={15} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-faint)' }} />
                            <input
                                type="search"
                                placeholder="Name, code, or mobile…"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                style={{ paddingLeft: '2.25rem' }}
                            />
                        </div>
                    </div>

                    <div style={{ flex: '0 0 165px' }}>
                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>Department</label>
                        <select value={departmentFilter} onChange={(e) => setDepartmentFilter(e.target.value)}>
                            <option value="">All Departments</option>
                            {departments.map(dept => <option key={dept} value={dept}>{dept}</option>)}
                        </select>
                    </div>

                    <div style={{ flex: '0 0 155px' }}>
                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>Type</label>
                        <select value={employeeTypeFilter} onChange={(e) => setEmployeeTypeFilter(e.target.value)}>
                            <option value="">All Types</option>
                            {employeeTypes.map(type => (
                                <option key={type} value={type}>{type?.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>
                            ))}
                        </select>
                    </div>

                    <div style={{ flex: '0 0 140px' }}>
                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>Status</label>
                        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                            <option value="">All</option>
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Employee Table */}
            <div className="card">
                <div className="table-container">
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Code</th>
                                <th>Name</th>
                                <th>Department</th>
                                <th>Designation</th>
                                <th>Type</th>
                                <th>Mobile</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredEmployees.length === 0 ? (
                                <tr>
                                    <td colSpan={8} style={{ textAlign: 'center', padding: '2rem' }}>
                                        <div style={{ color: 'var(--text-muted)' }}>No employees found</div>
                                    </td>
                                </tr>
                            ) : (
                                filteredEmployees.map(emp => (
                                    <tr key={emp.id}>
                                        <td>
                                            <span style={{ fontFamily: 'monospace', fontSize: '0.8125rem', background: '#f1f5f9', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 600 }}>
                                                {emp.emp_code}
                                            </span>
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                                                <div style={{
                                                    width: '30px', height: '30px', borderRadius: '50%', flexShrink: 0,
                                                    background: `hsl(${emp.full_name.charCodeAt(0) * 5 % 360}, 65%, 90%)`,
                                                    color: `hsl(${emp.full_name.charCodeAt(0) * 5 % 360}, 65%, 35%)`,
                                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                    fontWeight: 700, fontSize: '0.75rem',
                                                }}>
                                                    {emp.full_name.charAt(0).toUpperCase()}
                                                </div>
                                                <div>
                                                    <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{emp.full_name}</div>
                                                    {emp.email && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{emp.email}</div>}
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            {emp.department ? (
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', color: 'var(--text-secondary)' }}>
                                                    <Building2 size={13} style={{ color: 'var(--text-faint)' }} />
                                                    {emp.department}
                                                </div>
                                            ) : <span style={{ color: 'var(--text-faint)' }}>—</span>}
                                        </td>
                                        <td>
                                            {emp.designation ? (
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', color: 'var(--text-secondary)' }}>
                                                    <Briefcase size={13} style={{ color: 'var(--text-faint)' }} />
                                                    {emp.designation}
                                                </div>
                                            ) : <span style={{ color: 'var(--text-faint)' }}>—</span>}
                                        </td>
                                        <td>
                                            <span className="badge badge-info">
                                                {emp.employee_type?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) || 'Full Time'}
                                            </span>
                                        </td>
                                        <td style={{ color: 'var(--text-secondary)' }}>{emp.mobile_no}</td>
                                        <td>
                                            {emp.status === 'active' ? (
                                                <span className="badge badge-success"><CheckCircle size={11} /> Active</span>
                                            ) : (
                                                <span className="badge badge-gray">Inactive</span>
                                            )}
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '0.375rem' }}>
                                                <button onClick={() => handleEdit(emp)} className="btn btn-ghost btn-sm" title="Edit">
                                                    <Edit2 size={14} />
                                                </button>
                                                <button onClick={() => handleDelete(emp.id)} className="btn btn-danger btn-sm" title="Deactivate">
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

            {/* Edit Modal */}
            {showEditModal && editingEmployee && (
                <div className="modal-overlay">
                    <div className="modal" style={{ maxWidth: '600px' }}>
                        <div className="modal-header">
                            <h3 className="modal-title">Edit Employee</h3>
                            <button className="modal-close" onClick={() => setShowEditModal(false)}><X size={16} /></button>
                        </div>
                        <div className="modal-body">

                            <div style={{ display: 'grid', gap: '1rem' }}>
                                <div>
                                    <label>First Name *</label>
                                    <input
                                        type="text"
                                        className="input"
                                        value={editingEmployee.first_name}
                                        onChange={(e) => setEditingEmployee({ ...editingEmployee, first_name: e.target.value })}
                                    />
                                </div>

                                <div>
                                    <label>Last Name</label>
                                    <input
                                        type="text"
                                        className="input"
                                        value={editingEmployee.last_name || ''}
                                        onChange={(e) => setEditingEmployee({ ...editingEmployee, last_name: e.target.value })}
                                    />
                                </div>

                                <div>
                                    <label>Email</label>
                                    <input
                                        type="email"
                                        className="input"
                                        value={editingEmployee.email || ''}
                                        onChange={(e) => setEditingEmployee({ ...editingEmployee, email: e.target.value })}
                                    />
                                </div>

                                <div>
                                    <label>Mobile Number *</label>
                                    <input
                                        type="tel"
                                        className="input"
                                        value={editingEmployee.mobile_no}
                                        onChange={(e) => setEditingEmployee({ ...editingEmployee, mobile_no: e.target.value })}
                                    />
                                </div>

                                <div>
                                    <label>Department</label>
                                    <input
                                        type="text"
                                        className="input"
                                        value={editingEmployee.department || ''}
                                        onChange={(e) => setEditingEmployee({ ...editingEmployee, department: e.target.value })}
                                        placeholder="e.g., IT, HR, Finance"
                                    />
                                </div>

                                <div>
                                    <label>Designation</label>
                                    <input
                                        type="text"
                                        className="input"
                                        value={editingEmployee.designation || ''}
                                        onChange={(e) => setEditingEmployee({ ...editingEmployee, designation: e.target.value })}
                                        placeholder="e.g., Manager, Developer"
                                    />
                                </div>

                                <div>
                                    <label>Employee Type</label>
                                    <select
                                        className="input"
                                        value={editingEmployee.employee_type || 'full_time'}
                                        onChange={(e) => setEditingEmployee({ ...editingEmployee, employee_type: e.target.value })}
                                    >
                                        <option value="full_time">Full Time</option>
                                        <option value="part_time">Part Time</option>
                                        <option value="contract">Contract</option>
                                        <option value="intern">Intern</option>
                                    </select>
                                </div>

                                <div>
                                    <label>Status</label>
                                    <select
                                        className="input"
                                        value={editingEmployee.status}
                                        onChange={(e) => setEditingEmployee({ ...editingEmployee, status: e.target.value })}
                                    >
                                        <option value="active">Active</option>
                                        <option value="inactive">Inactive</option>
                                    </select>
                                </div>
                            </div>

                        </div>
                        <div className="modal-footer">
                            <button onClick={() => setShowEditModal(false)} className="btn btn-ghost">
                                Cancel
                            </button>
                            <button onClick={handleSaveEdit} className="btn btn-primary">
                                Save Changes
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
