import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'router-dom';
import { Plus, Edit2, Trash2, Filter, Search, Building2, Briefcase } from 'lucide-react';

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
    const departments = Array.from(new Set(employees.map(e => e.department).filter(Boolean)));
    const employeeTypes = Array.from(new Set(employees.map(e => e.employee_type).filter(Boolean)));

    if (loading) return <div className="p-4">Loading employees...</div>;

    return (
        <div>
            <div className="page-header">
                <h2>Employee Management</h2>
                <Link to="/register" className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Plus size={18} />
                    Add Employee
                </Link>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            {/* Filters */}
            <div className="card" style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
                    <div style={{ flex: 1, minWidth: '200px' }}>
                        <div style={{ position: 'relative' }}>
                            <Search size={18} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input
                                type="text"
                                placeholder="Search by name, code, or mobile..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                style={{ paddingLeft: '2.5rem', width: '100%' }}
                                className="input"
                            />
                        </div>
                    </div>

                    <select
                        value={departmentFilter}
                        onChange={(e) => setDepartmentFilter(e.target.value)}
                        className="input"
                        style={{ minWidth: '150px' }}
                    >
                        <option value="">All Departments</option>
                        {departments.map(dept => (
                            <option key={dept} value={dept}>{dept}</option>
                        ))}
                    </select>

                    <select
                        value={employeeTypeFilter}
                        onChange={(e) => setEmployeeTypeFilter(e.target.value)}
                        className="input"
                        style={{ minWidth: '150px' }}
                    >
                        <option value="">All Types</option>
                        {employeeTypes.map(type => (
                            <option key={type} value={type}>
                                {type?.replace('_', ' ').toUpperCase()}
                            </option>
                        ))}
                    </select>

                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="input"
                        style={{ minWidth: '120px' }}
                    >
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                    </select>
                </div>

                <div style={{ marginTop: '0.75rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                    Showing {filteredEmployees.length} of {employees.length} employees
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
                                            <span style={{ fontFamily: 'monospace', fontWeight: 600 }}>{emp.emp_code}</span>
                                        </td>
                                        <td>
                                            <div style={{ fontWeight: 500 }}>{emp.full_name}</div>
                                            {emp.email && <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{emp.email}</div>}
                                        </td>
                                        <td>
                                            {emp.department ? (
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                    <Building2 size={14} style={{ color: 'var(--text-muted)' }} />
                                                    {emp.department}
                                                </div>
                                            ) : (
                                                <span style={{ color: 'var(--text-muted)' }}>-</span>
                                            )}
                                        </td>
                                        <td>
                                            {emp.designation ? (
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                    <Briefcase size={14} style={{ color: 'var(--text-muted)' }} />
                                                    {emp.designation}
                                                </div>
                                            ) : (
                                                <span style={{ color: 'var(--text-muted)' }}>-</span>
                                            )}
                                        </td>
                                        <td>
                                            <span className="badge" style={{ background: '#e0f2fe', color: '#0284c7' }}>
                                                {emp.employee_type?.replace('_', ' ').toUpperCase() || 'FULL TIME'}
                                            </span>
                                        </td>
                                        <td>{emp.mobile_no}</td>
                                        <td>
                                            {emp.status === 'active' ? (
                                                <span className="badge badge-success">Active</span>
                                            ) : (
                                                <span className="badge badge-warning">Inactive</span>
                                            )}
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <button
                                                    onClick={() => handleEdit(emp)}
                                                    className="btn btn-sm"
                                                    style={{ padding: '0.375rem 0.75rem' }}
                                                    title="Edit"
                                                >
                                                    <Edit2 size={14} />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(emp.id)}
                                                    className="btn btn-sm"
                                                    style={{ padding: '0.375rem 0.75rem', background: '#fee2e2', color: '#dc2626' }}
                                                    title="Deactivate"
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

            {/* Edit Modal */}
            {showEditModal && editingEmployee && (
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
                        <h3 style={{ marginBottom: '1.5rem' }}>Edit Employee</h3>

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

                        <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', justifyContent: 'flex-end' }}>
                            <button
                                onClick={() => setShowEditModal(false)}
                                className="btn"
                                style={{ background: '#f3f4f6', color: '#374151' }}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSaveEdit}
                                className="btn btn-primary"
                            >
                                Save Changes
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
