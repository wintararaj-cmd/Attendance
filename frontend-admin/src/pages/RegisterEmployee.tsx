import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { ArrowLeft, Save } from 'lucide-react';

interface Department {
    id: string;
    name: string;
}

export default function RegisterEmployee() {
    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        empId: '',
        mobile: '',
        email: '',
        department: '',
        designation: '',
        employeeType: 'full_time',
        joiningDate: '',
    });
    const [file, setFile] = useState<File | null>(null);
    const [status, setStatus] = useState<{ type: 'success' | 'error' | '', msg: string }>({ type: '', msg: '' });
    const [loading, setLoading] = useState(false);
    const [departments, setDepartments] = useState<Department[]>([]);

    useEffect(() => {
        // Fetch departments
        axios.get('/api/v1/departments?status=active')
            .then(res => setDepartments(res.data))
            .catch(err => console.error('Failed to fetch departments:', err));
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) {
            setStatus({ type: 'error', msg: "Please select an image" });
            return;
        }

        setLoading(true);
        setStatus({ type: '', msg: '' });

        const data = new FormData();
        // For face registration, we still use 'name' field (first name)
        data.append('name', formData.firstName);
        data.append('emp_id', formData.empId);
        data.append('mobile_no', formData.mobile);
        data.append('file', file);

        try {
            // First, register the face and create basic employee record
            const res = await axios.post('/api/v1/attendance/register', data);

            // Then, update the employee with additional details
            const employeeId = res.data.id;
            await axios.put(`/api/v1/employees/${employeeId}`, {
                first_name: formData.firstName,
                last_name: formData.lastName,
                email: formData.email,
                department: formData.department,
                designation: formData.designation,
                employee_type: formData.employeeType,
                joining_date: formData.joiningDate || null,
            });

            setStatus({ type: 'success', msg: 'Employee registered successfully with all details!' });
            // Reset form after success
            setFormData({
                firstName: '',
                lastName: '',
                empId: '',
                mobile: '',
                email: '',
                department: '',
                designation: '',
                employeeType: 'full_time',
                joiningDate: ''
            });
            setFile(null);
        } catch (err: any) {
            setStatus({ type: 'error', msg: err.response?.data?.detail || 'Registration Failed' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="page-header">
                <h2>Register New Employee</h2>
                <Link to="/employees" className="btn" style={{ background: '#e5e7eb', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <ArrowLeft size={18} />
                    Back to List
                </Link>
            </div>

            <div className="card" style={{ maxWidth: '800px', margin: '0 auto' }}>
                <form onSubmit={handleSubmit}>

                    {status.msg && (
                        <div className={`alert ${status.type === 'success' ? 'alert-success' : 'alert-error'}`}>
                            {status.msg}
                        </div>
                    )}

                    <h3 style={{ marginBottom: '1.5rem', color: 'var(--text-primary)' }}>Personal Information</h3>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                        <div className="form-group">
                            <label>First Name *</label>
                            <input
                                type="text"
                                required
                                value={formData.firstName}
                                onChange={e => setFormData({ ...formData, firstName: e.target.value })}
                                placeholder="e.g. John"
                            />
                        </div>

                        <div className="form-group">
                            <label>Last Name</label>
                            <input
                                type="text"
                                value={formData.lastName}
                                onChange={e => setFormData({ ...formData, lastName: e.target.value })}
                                placeholder="e.g. Doe"
                            />
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                        <div className="form-group">
                            <label>Employee ID *</label>
                            <input
                                type="text"
                                required
                                value={formData.empId}
                                onChange={e => setFormData({ ...formData, empId: e.target.value })}
                                placeholder="e.g. EMP001"
                            />
                        </div>

                        <div className="form-group">
                            <label>Mobile Number *</label>
                            <input
                                type="tel"
                                required
                                value={formData.mobile}
                                onChange={e => setFormData({ ...formData, mobile: e.target.value })}
                                placeholder="e.g. 9876543210"
                            />
                        </div>
                    </div>

                    <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                        <label>Email</label>
                        <input
                            type="email"
                            value={formData.email}
                            onChange={e => setFormData({ ...formData, email: e.target.value })}
                            placeholder="e.g. john.doe@company.com"
                        />
                    </div>

                    <h3 style={{ marginBottom: '1.5rem', marginTop: '2rem', color: 'var(--text-primary)' }}>Employment Details</h3>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                        <div className="form-group">
                            <label>Department</label>
                            <select
                                value={formData.department}
                                onChange={e => setFormData({ ...formData, department: e.target.value })}
                            >
                                <option value="">Select Department</option>
                                {departments.map(dept => (
                                    <option key={dept.id} value={dept.name}>{dept.name}</option>
                                ))}
                            </select>
                        </div>

                        <div className="form-group">
                            <label>Designation</label>
                            <input
                                type="text"
                                value={formData.designation}
                                onChange={e => setFormData({ ...formData, designation: e.target.value })}
                                placeholder="e.g. Manager, Developer"
                            />
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                        <div className="form-group">
                            <label>Employee Type</label>
                            <select
                                value={formData.employeeType}
                                onChange={e => setFormData({ ...formData, employeeType: e.target.value })}
                            >
                                <option value="full_time">Full Time</option>
                                <option value="part_time">Part Time</option>
                                <option value="contract">Contract</option>
                                <option value="intern">Intern</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>Joining Date</label>
                            <input
                                type="date"
                                value={formData.joiningDate}
                                onChange={e => setFormData({ ...formData, joiningDate: e.target.value })}
                            />
                        </div>
                    </div>

                    <h3 style={{ marginBottom: '1.5rem', marginTop: '2rem', color: 'var(--text-primary)' }}>Biometric Registration</h3>

                    <div className="form-group">
                        <label>Face Photo (Clear Frontal View) *</label>
                        <div style={{ border: '2px dashed #d1d5db', padding: '2rem', textAlign: 'center', borderRadius: '8px', cursor: 'pointer' }}>
                            <input
                                type="file"
                                required
                                accept="image/*"
                                onChange={e => setFile(e.target.files?.[0] || null)}
                                style={{ width: 'auto', border: 'none' }}
                            />
                            <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.5rem' }}>
                                Upload a clear photo of the face for biometric registration
                            </p>
                            {file && (
                                <p style={{ fontSize: '0.875rem', color: 'var(--primary)', marginTop: '0.5rem', fontWeight: 500 }}>
                                    Selected: {file.name}
                                </p>
                            )}
                        </div>
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem', marginTop: '2rem' }}>
                        {loading ? 'Processing...' : (
                            <>
                                <Save size={18} />
                                Register Employee
                            </>
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
}
