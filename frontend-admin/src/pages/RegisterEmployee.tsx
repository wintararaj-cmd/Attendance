import { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { ArrowLeft, Save } from 'lucide-react';

export default function RegisterEmployee() {
    const [formData, setFormData] = useState({
        name: '',
        empId: '',
        mobile: '',
    });
    const [file, setFile] = useState<File | null>(null);
    const [status, setStatus] = useState<{ type: 'success' | 'error' | '', msg: string }>({ type: '', msg: '' });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) {
            setStatus({ type: 'error', msg: "Please select an image" });
            return;
        }

        setLoading(true);
        setStatus({ type: '', msg: '' });

        const data = new FormData();
        data.append('name', formData.name);
        data.append('emp_id', formData.empId);
        data.append('mobile_no', formData.mobile);
        data.append('file', file);

        try {
            const res = await axios.post('/api/v1/attendance/register', data);
            setStatus({ type: 'success', msg: res.data.message });
            // Optional: reset form after success
            setFormData({ name: '', empId: '', mobile: '' });
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

            <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
                <form onSubmit={handleSubmit}>

                    {status.msg && (
                        <div className={`alert ${status.type === 'success' ? 'alert-success' : 'alert-error'}`}>
                            {status.msg}
                        </div>
                    )}

                    <div className="form-group">
                        <label>Employee Name</label>
                        <input
                            type="text"
                            required
                            value={formData.name}
                            onChange={e => setFormData({ ...formData, name: e.target.value })}
                            placeholder="e.g. John Doe"
                        />
                    </div>

                    <div className="form-group">
                        <label>Employee ID</label>
                        <input
                            type="text"
                            required
                            value={formData.empId}
                            onChange={e => setFormData({ ...formData, empId: e.target.value })}
                            placeholder="e.g. EMP001"
                        />
                    </div>

                    <div className="form-group">
                        <label>Mobile Number</label>
                        <input
                            type="tel"
                            required
                            value={formData.mobile}
                            onChange={e => setFormData({ ...formData, mobile: e.target.value })}
                            placeholder="e.g. 9876543210"
                        />
                    </div>

                    <div className="form-group">
                        <label>Face Photo (Clear Frontal View)</label>
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
                        </div>
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem', marginTop: '1rem' }}>
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
