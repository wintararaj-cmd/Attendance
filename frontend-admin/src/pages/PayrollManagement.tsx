import { useEffect, useState } from 'react';
import axios from 'axios';
import { Calculator, Download, X, Settings } from 'lucide-react';

interface Employee {
    id: string;
    emp_code: string;
    first_name: string;
    last_name?: string;
}

interface PayrollData {
    employee_id: string;
    employee_name: string;
    month: string;
    present_days: number;
    payroll: {
        earnings: {
            basic: number;
            hra: number;
            gross_earned: number;
            special: number;
        };
        deductions: {
            pf: number;
            prof_tax: number;
            lop: number;
            total: number;
        };
        net_salary: number;
    };
}

export default function PayrollManagement() {
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedPayroll, setSelectedPayroll] = useState<PayrollData | null>(null);
    const [processingId, setProcessingId] = useState<string | null>(null);

    // Config Modal State
    const [showConfigModal, setShowConfigModal] = useState(false);
    const [configEmpId, setConfigEmpId] = useState<string | null>(null);
    const [salaryForm, setSalaryForm] = useState({
        basic_salary: 0,
        hra_allowance: 0,
        special_allowance: 0,
        pf_deduction: 0,
        professional_tax: 0
    });

    useEffect(() => {
        axios.get('/api/v1/employees')
            .then(res => setEmployees(res.data))
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    const handleRunPayroll = async (empId: string) => {
        setProcessingId(empId);
        try {
            const res = await axios.get(`/api/v1/payroll/employee/${empId}`);
            setSelectedPayroll(res.data);
        } catch (err) {
            alert("Failed to calculate payroll. Ensure salary is configured.");
        } finally {
            setProcessingId(null);
        }
    };

    const handleOpenConfig = async (empId: string) => {
        setConfigEmpId(empId);
        try {
            const res = await axios.get(`/api/v1/employees/${empId}/salary`);
            setSalaryForm(res.data);
            setShowConfigModal(true);
        } catch (err) {
            console.error(err);
        }
    };

    const handleSaveSalary = async () => {
        if (!configEmpId) return;
        try {
            await axios.post(`/api/v1/employees/${configEmpId}/salary`, salaryForm);
            alert("Salary structure saved successfully!");
            setShowConfigModal(false);
        } catch (err) {
            alert("Failed to save salary.");
        }
    };

    const handleDownloadPdf = async () => {
        if (!selectedPayroll) return;
        try {
            const response = await axios.get(`/api/v1/payroll/payslip/${selectedPayroll.employee_id}/pdf`, {
                responseType: 'blob',
            });

            // Create blob link to download
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Payslip_${selectedPayroll.employee_name}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error('Error downloading PDF:', error);
            alert("Failed to download PDF.");
        }
    };

    if (loading) return <div className="p-4">Loading...</div>;

    return (
        <div>
            <div className="page-header">
                <h2>Payroll Management</h2>
            </div>

            <div className="card">
                <div className="table-container">
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Employee</th>
                                <th>Code</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {employees.map(emp => (
                                <tr key={emp.id}>
                                    <td>{emp.first_name} {emp.last_name || ''}</td>
                                    <td><span style={{ fontFamily: 'monospace' }}>{emp.emp_code}</span></td>
                                    <td>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            <button
                                                className="btn"
                                                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', border: '1px solid #e2e8f0' }}
                                                onClick={() => handleOpenConfig(emp.id)}
                                            >
                                                <Settings size={16} />
                                                Config Salary
                                            </button>
                                            <button
                                                className="btn btn-primary"
                                                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}
                                                onClick={() => handleRunPayroll(emp.id)}
                                                disabled={!!processingId}
                                            >
                                                {processingId === emp.id ? 'Calculating...' : (
                                                    <>
                                                        <Calculator size={16} />
                                                        Run Payroll
                                                    </>
                                                )}
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Config Modal */}
            {showConfigModal && (
                <div style={modalOverlayStyle}>
                    <div className="card" style={{ width: '400px', padding: '1.5rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                            <h3>Configure Salary</h3>
                            <button onClick={() => setShowConfigModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}><X size={20} /></button>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <div>
                                <label style={labelStyle}>Basic Salary</label>
                                <input type="number" style={inputStyle} value={salaryForm.basic_salary} onChange={e => setSalaryForm({ ...salaryForm, basic_salary: Number(e.target.value) })} />
                            </div>
                            <div>
                                <label style={labelStyle}>HRA Allowance</label>
                                <input type="number" style={inputStyle} value={salaryForm.hra_allowance} onChange={e => setSalaryForm({ ...salaryForm, hra_allowance: Number(e.target.value) })} />
                            </div>
                            <div>
                                <label style={labelStyle}>Special Allowance</label>
                                <input type="number" style={inputStyle} value={salaryForm.special_allowance} onChange={e => setSalaryForm({ ...salaryForm, special_allowance: Number(e.target.value) })} />
                            </div>
                            <div>
                                <label style={labelStyle}>PF Deduction</label>
                                <input type="number" style={inputStyle} value={salaryForm.pf_deduction} onChange={e => setSalaryForm({ ...salaryForm, pf_deduction: Number(e.target.value) })} />
                            </div>
                            <div>
                                <label style={labelStyle}>Professional Tax</label>
                                <input type="number" style={inputStyle} value={salaryForm.professional_tax} onChange={e => setSalaryForm({ ...salaryForm, professional_tax: Number(e.target.value) })} />
                            </div>

                            <button className="btn btn-primary" onClick={handleSaveSalary} style={{ marginTop: '1rem' }}>
                                Save Configuration
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Payslip Modal */}
            {selectedPayroll && (
                <div style={modalOverlayStyle}>
                    <div className="card" style={{ width: '500px', maxHeight: '90vh', overflowY: 'auto' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <h3 style={{ margin: 0 }}>Payslip Preview</h3>
                            <button onClick={() => setSelectedPayroll(null)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                                <X size={24} />
                            </button>
                        </div>

                        <div style={{ textAlign: 'center', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid #eee' }}>
                            <h2 style={{ fontSize: '1.25rem', margin: '0 0 0.5rem 0' }}>{selectedPayroll.employee_name}</h2>
                            <div className="text-muted">{selectedPayroll.month}</div>
                            <div className="badge badge-success" style={{ marginTop: '0.5rem' }}>
                                Present Days: {selectedPayroll.present_days}
                            </div>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                            <div>
                                <h4 style={{ color: '#059669', marginBottom: '0.5rem' }}>Earnings</h4>
                                <div style={{ fontSize: '0.9rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                                        <span>Basic</span>
                                        <span>{selectedPayroll.payroll.earnings.basic}</span>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                                        <span>HRA</span>
                                        <span>{selectedPayroll.payroll.earnings.hra}</span>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                        <span>Allowances</span>
                                        <span>{selectedPayroll.payroll.earnings.special}</span>
                                    </div>
                                    <div style={{ borderTop: '1px solid #eee', paddingTop: '0.5rem', fontWeight: 600, display: 'flex', justifyContent: 'space-between' }}>
                                        <span>Gross</span>
                                        <span>{selectedPayroll.payroll.earnings.gross_earned}</span>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h4 style={{ color: '#dc2626', marginBottom: '0.5rem' }}>Deductions</h4>
                                <div style={{ fontSize: '0.9rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                                        <span>PF</span>
                                        <span>{selectedPayroll.payroll.deductions.pf}</span>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                                        <span>Tax</span>
                                        <span>{selectedPayroll.payroll.deductions.prof_tax}</span>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                        <span>LOP</span>
                                        <span>{selectedPayroll.payroll.deductions.lop}</span>
                                    </div>
                                    <div style={{ borderTop: '1px solid #eee', paddingTop: '0.5rem', fontWeight: 600, display: 'flex', justifyContent: 'space-between' }}>
                                        <span>Total</span>
                                        <span>{selectedPayroll.payroll.deductions.total}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div style={{ marginTop: '1.5rem', padding: '1rem', background: '#f8fafc', borderRadius: '8px', textAlign: 'center' }}>
                            <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Net Salary Payable</div>
                            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2563eb' }}>
                                ₹{selectedPayroll.payroll.net_salary.toLocaleString('en-IN')}
                            </div>
                        </div>

                        <button
                            className="btn btn-primary"
                            style={{ width: '100%', marginTop: '1.5rem', display: 'flex', justifyContent: 'center', gap: '0.5rem' }}
                            onClick={handleDownloadPdf}
                        >
                            <Download size={18} /> Download Payslip PDF
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

const modalOverlayStyle: React.CSSProperties = {
    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
};

const labelStyle: React.CSSProperties = {
    display: 'block', fontSize: '0.85rem', color: '#64748b', marginBottom: '0.25rem'
};

const inputStyle: React.CSSProperties = {
    width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #cbd5e1'
};
