import { useEffect, useState } from 'react';
import axios from 'axios';
import { Calculator, Download, X, Settings, DollarSign, Users, TrendingUp, Filter, Search } from 'lucide-react';

interface Employee {
    id: string;
    emp_code: string;
    first_name: string;
    last_name?: string;
    department?: string;
    designation?: string;
    status: string;
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

interface SalaryStructure {
    basic_salary: number;
    // Allowances
    hra: number;
    conveyance_allowance: number;
    medical_allowance: number;
    special_allowance: number;
    education_allowance: number;
    other_allowance: number;
    // Deductions
    pf_employee: number;
    pf_employer: number;
    esi_employee: number;
    esi_employer: number;
    professional_tax: number;
    tds: number;
    // Benefits
    bonus: number;
    incentive: number;
    // Settings
    is_pf_applicable: boolean;
    is_esi_applicable: boolean;
}

export default function PayrollManagement() {
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [filteredEmployees, setFilteredEmployees] = useState<Employee[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedPayroll, setSelectedPayroll] = useState<PayrollData | null>(null);
    const [processingId, setProcessingId] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [departmentFilter, setDepartmentFilter] = useState('');

    // Config Modal State
    const [showConfigModal, setShowConfigModal] = useState(false);
    const [configEmpId, setConfigEmpId] = useState<string | null>(null);
    const [configEmpName, setConfigEmpName] = useState('');
    const [salaryForm, setSalaryForm] = useState<SalaryStructure>({
        basic_salary: 0,
        hra: 0,
        conveyance_allowance: 0,
        medical_allowance: 0,
        special_allowance: 0,
        education_allowance: 0,
        other_allowance: 0,
        pf_employee: 0,
        pf_employer: 0,
        esi_employee: 0,
        esi_employer: 0,
        professional_tax: 0,
        tds: 0,
        bonus: 0,
        incentive: 0,
        is_pf_applicable: true,
        is_esi_applicable: false
    });

    useEffect(() => {
        fetchEmployees();
    }, []);

    useEffect(() => {
        filterEmployees();
    }, [employees, searchTerm, departmentFilter]);

    const fetchEmployees = async () => {
        try {
            const res = await axios.get('/api/v1/employees?status=active');
            setEmployees(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const filterEmployees = () => {
        let filtered = employees;

        if (searchTerm) {
            filtered = filtered.filter(emp =>
                `${emp.first_name} ${emp.last_name || ''}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
                emp.emp_code.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        if (departmentFilter) {
            filtered = filtered.filter(emp => emp.department === departmentFilter);
        }

        setFilteredEmployees(filtered);
    };

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

    const handleOpenConfig = async (empId: string, empName: string) => {
        setConfigEmpId(empId);
        setConfigEmpName(empName);
        try {
            const res = await axios.get(`/api/v1/employees/${empId}/salary`);
            setSalaryForm(res.data);
            setShowConfigModal(true);
        } catch (err) {
            console.error(err);
            // Set default values if no salary structure exists
            setSalaryForm({
                basic_salary: 0,
                hra: 0,
                conveyance_allowance: 0,
                medical_allowance: 0,
                special_allowance: 0,
                education_allowance: 0,
                other_allowance: 0,
                pf_employee: 0,
                pf_employer: 0,
                esi_employee: 0,
                esi_employer: 0,
                professional_tax: 0,
                tds: 0,
                bonus: 0,
                incentive: 0,
                is_pf_applicable: true,
                is_esi_applicable: false
            });
            setShowConfigModal(true);
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

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Payslip_${selectedPayroll.employee_name}_${selectedPayroll.month}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error('Error downloading PDF:', error);
            alert("Failed to download PDF.");
        }
    };

    const calculateTotalPayroll = () => {
        // This would ideally come from the backend
        return filteredEmployees.length * 25000; // Placeholder
    };

    const departments = Array.from(new Set(employees.map(e => e.department).filter(Boolean)));

    if (loading) return <div className="p-4">Loading...</div>;

    return (
        <div>
            <div className="page-header">
                <h2>Payroll Management</h2>
            </div>

            {/* Stats Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                <div className="card" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <p style={{ margin: 0, opacity: 0.9, fontSize: '0.875rem' }}>Total Employees</p>
                            <h2 style={{ margin: '0.5rem 0 0 0', fontSize: '2rem' }}>{employees.length}</h2>
                        </div>
                        <Users size={48} style={{ opacity: 0.3 }} />
                    </div>
                </div>

                <div className="card" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <p style={{ margin: 0, opacity: 0.9, fontSize: '0.875rem' }}>Estimated Payroll</p>
                            <h2 style={{ margin: '0.5rem 0 0 0', fontSize: '2rem' }}>
                                ₹{(calculateTotalPayroll() / 1000).toFixed(0)}K
                            </h2>
                        </div>
                        <DollarSign size={48} style={{ opacity: 0.3 }} />
                    </div>
                </div>

                <div className="card" style={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <p style={{ margin: 0, opacity: 0.9, fontSize: '0.875rem' }}>Avg Salary</p>
                            <h2 style={{ margin: '0.5rem 0 0 0', fontSize: '2rem' }}>
                                ₹{employees.length > 0 ? (calculateTotalPayroll() / employees.length / 1000).toFixed(0) : 0}K
                            </h2>
                        </div>
                        <TrendingUp size={48} style={{ opacity: 0.3 }} />
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="card" style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
                    <div style={{ flex: 1, minWidth: '200px' }}>
                        <div style={{ position: 'relative' }}>
                            <Search size={18} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input
                                type="text"
                                placeholder="Search by name or code..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                style={{ paddingLeft: '2.5rem', width: '100%' }}
                                className="input"
                            />
                        </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Filter size={18} style={{ color: 'var(--text-muted)' }} />
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
                    </div>
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
                                <th>Employee</th>
                                <th>Code</th>
                                <th>Department</th>
                                <th>Designation</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredEmployees.length === 0 ? (
                                <tr>
                                    <td colSpan={5} style={{ textAlign: 'center', padding: '2rem' }}>
                                        <div style={{ color: 'var(--text-muted)' }}>No employees found</div>
                                    </td>
                                </tr>
                            ) : (
                                filteredEmployees.map(emp => (
                                    <tr key={emp.id}>
                                        <td>
                                            <div style={{ fontWeight: 500 }}>
                                                {emp.first_name} {emp.last_name || ''}
                                            </div>
                                        </td>
                                        <td>
                                            <span style={{ fontFamily: 'monospace', fontWeight: 600 }}>
                                                {emp.emp_code}
                                            </span>
                                        </td>
                                        <td>{emp.department || '-'}</td>
                                        <td>{emp.designation || '-'}</td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <button
                                                    className="btn"
                                                    style={{
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '0.5rem',
                                                        fontSize: '0.875rem',
                                                        padding: '0.5rem 0.75rem',
                                                        background: '#f3f4f6'
                                                    }}
                                                    onClick={() => handleOpenConfig(emp.id, `${emp.first_name} ${emp.last_name || ''}`)}
                                                >
                                                    <Settings size={16} />
                                                    Configure
                                                </button>
                                                <button
                                                    className="btn btn-primary"
                                                    style={{
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '0.5rem',
                                                        fontSize: '0.875rem',
                                                        padding: '0.5rem 0.75rem'
                                                    }}
                                                    onClick={() => handleRunPayroll(emp.id)}
                                                    disabled={!!processingId}
                                                >
                                                    {processingId === emp.id ? 'Processing...' : (
                                                        <>
                                                            <Calculator size={16} />
                                                            Calculate
                                                        </>
                                                    )}
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

            {/* Config Modal */}
            {showConfigModal && (
                <div style={modalOverlayStyle}>
                    <div className="card" style={{ width: '500px', maxHeight: '90vh', overflowY: 'auto' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                            <div>
                                <h3 style={{ margin: 0 }}>Configure Salary Structure</h3>
                                <p style={{ margin: '0.5rem 0 0 0', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                    {configEmpName}
                                </p>
                            </div>
                            <button
                                onClick={() => setShowConfigModal(false)}
                                style={{ background: 'none', border: 'none', cursor: 'pointer' }}
                            >
                                <X size={24} />
                            </button>
                        </div>

                        <div style={{ display: 'grid', gap: '1.5rem' }}>
                            {/* Earnings Section */}
                            <div>
                                <h4 style={{ margin: '0 0 1rem 0', color: '#059669', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <TrendingUp size={18} />
                                    Earnings & Allowances
                                </h4>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                    <div>
                                        <label style={labelStyle}>Basic Salary *</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.basic_salary}
                                            onChange={e => setSalaryForm({ ...salaryForm, basic_salary: Number(e.target.value) })}
                                            placeholder="e.g., 15000"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>HRA</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.hra}
                                            onChange={e => setSalaryForm({ ...salaryForm, hra: Number(e.target.value) })}
                                            placeholder="e.g., 5000"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Conveyance Allowance</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.conveyance_allowance}
                                            onChange={e => setSalaryForm({ ...salaryForm, conveyance_allowance: Number(e.target.value) })}
                                            placeholder="e.g., 1600"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Medical Allowance</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.medical_allowance}
                                            onChange={e => setSalaryForm({ ...salaryForm, medical_allowance: Number(e.target.value) })}
                                            placeholder="e.g., 1250"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Special Allowance</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.special_allowance}
                                            onChange={e => setSalaryForm({ ...salaryForm, special_allowance: Number(e.target.value) })}
                                            placeholder="e.g., 3000"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Education Allowance</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.education_allowance}
                                            onChange={e => setSalaryForm({ ...salaryForm, education_allowance: Number(e.target.value) })}
                                            placeholder="e.g., 100"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Other Allowance</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.other_allowance}
                                            onChange={e => setSalaryForm({ ...salaryForm, other_allowance: Number(e.target.value) })}
                                            placeholder="e.g., 500"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Deductions Section */}
                            <div>
                                <h4 style={{ margin: '0 0 1rem 0', color: '#dc2626', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <DollarSign size={18} />
                                    Deductions
                                </h4>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                    <div>
                                        <label style={labelStyle}>PF Employee (12%)</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.pf_employee}
                                            onChange={e => setSalaryForm({ ...salaryForm, pf_employee: Number(e.target.value) })}
                                            placeholder="e.g., 1800"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>PF Employer (12%)</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.pf_employer}
                                            onChange={e => setSalaryForm({ ...salaryForm, pf_employer: Number(e.target.value) })}
                                            placeholder="e.g., 1800"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>ESI Employee (0.75%)</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.esi_employee}
                                            onChange={e => setSalaryForm({ ...salaryForm, esi_employee: Number(e.target.value) })}
                                            placeholder="e.g., 150"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>ESI Employer (3.25%)</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.esi_employer}
                                            onChange={e => setSalaryForm({ ...salaryForm, esi_employer: Number(e.target.value) })}
                                            placeholder="e.g., 650"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Professional Tax</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.professional_tax}
                                            onChange={e => setSalaryForm({ ...salaryForm, professional_tax: Number(e.target.value) })}
                                            placeholder="e.g., 200"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>TDS</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.tds}
                                            onChange={e => setSalaryForm({ ...salaryForm, tds: Number(e.target.value) })}
                                            placeholder="e.g., 500"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Benefits Section */}
                            <div>
                                <h4 style={{ margin: '0 0 1rem 0', color: '#2563eb', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <TrendingUp size={18} />
                                    Benefits
                                </h4>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                    <div>
                                        <label style={labelStyle}>Bonus</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.bonus}
                                            onChange={e => setSalaryForm({ ...salaryForm, bonus: Number(e.target.value) })}
                                            placeholder="e.g., 2000"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Incentive</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.incentive}
                                            onChange={e => setSalaryForm({ ...salaryForm, incentive: Number(e.target.value) })}
                                            placeholder="e.g., 1000"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Settings Section */}
                            <div>
                                <h4 style={{ margin: '0 0 1rem 0', color: '#6b7280', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <Settings size={18} />
                                    Calculation Settings
                                </h4>
                                <div style={{ display: 'grid', gap: '0.75rem' }}>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                        <input
                                            type="checkbox"
                                            checked={salaryForm.is_pf_applicable}
                                            onChange={e => setSalaryForm({ ...salaryForm, is_pf_applicable: e.target.checked })}
                                            style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                                        />
                                        <span>PF Applicable</span>
                                    </label>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                        <input
                                            type="checkbox"
                                            checked={salaryForm.is_esi_applicable}
                                            onChange={e => setSalaryForm({ ...salaryForm, is_esi_applicable: e.target.checked })}
                                            style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                                        />
                                        <span>ESI Applicable</span>
                                    </label>
                                </div>
                            </div>

                            {/* Summary */}
                            <div style={{
                                padding: '1rem',
                                background: '#f8fafc',
                                borderRadius: '8px',
                                border: '1px solid #e2e8f0'
                            }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                    <span style={{ color: 'var(--text-muted)' }}>Gross Salary:</span>
                                    <span style={{ fontWeight: 600 }}>
                                        ₹{(
                                            salaryForm.basic_salary +
                                            salaryForm.hra +
                                            salaryForm.conveyance_allowance +
                                            salaryForm.medical_allowance +
                                            salaryForm.special_allowance +
                                            salaryForm.education_allowance +
                                            salaryForm.other_allowance
                                        ).toLocaleString('en-IN')}
                                    </span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                    <span style={{ color: 'var(--text-muted)' }}>Total Deductions:</span>
                                    <span style={{ fontWeight: 600, color: '#dc2626' }}>
                                        ₹{(
                                            salaryForm.pf_employee +
                                            salaryForm.esi_employee +
                                            salaryForm.professional_tax +
                                            salaryForm.tds
                                        ).toLocaleString('en-IN')}
                                    </span>
                                </div>
                                <div style={{
                                    borderTop: '2px solid #cbd5e1',
                                    paddingTop: '0.5rem',
                                    marginTop: '0.5rem',
                                    display: 'flex',
                                    justifyContent: 'space-between'
                                }}>
                                    <span style={{ fontWeight: 600 }}>Net Salary:</span>
                                    <span style={{ fontWeight: 700, fontSize: '1.25rem', color: '#2563eb' }}>
                                        ₹{(
                                            salaryForm.basic_salary +
                                            salaryForm.hra +
                                            salaryForm.conveyance_allowance +
                                            salaryForm.medical_allowance +
                                            salaryForm.special_allowance +
                                            salaryForm.education_allowance +
                                            salaryForm.other_allowance +
                                            salaryForm.bonus +
                                            salaryForm.incentive -
                                            salaryForm.pf_employee -
                                            salaryForm.esi_employee -
                                            salaryForm.professional_tax -
                                            salaryForm.tds
                                        ).toLocaleString('en-IN')}
                                    </span>
                                </div>
                            </div>

                            <button
                                className="btn btn-primary"
                                onClick={handleSaveSalary}
                                style={{ width: '100%', padding: '0.75rem' }}
                            >
                                Save Salary Configuration
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Payslip Modal */}
            {selectedPayroll && (
                <div style={modalOverlayStyle}>
                    <div className="card" style={{ width: '550px', maxHeight: '90vh', overflowY: 'auto' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <h3 style={{ margin: 0 }}>Payslip Preview</h3>
                            <button onClick={() => setSelectedPayroll(null)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                                <X size={24} />
                            </button>
                        </div>

                        <div style={{ textAlign: 'center', marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: '2px solid #e2e8f0' }}>
                            <h2 style={{ fontSize: '1.5rem', margin: '0 0 0.5rem 0', color: 'var(--primary)' }}>
                                {selectedPayroll.employee_name}
                            </h2>
                            <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                                {selectedPayroll.month}
                            </div>
                            <div className="badge badge-success" style={{ fontSize: '0.875rem' }}>
                                Present Days: {selectedPayroll.present_days} / 30
                            </div>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '1.5rem' }}>
                            <div>
                                <h4 style={{ color: '#059669', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <TrendingUp size={18} />
                                    Earnings
                                </h4>
                                <div style={{ fontSize: '0.9rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                        <span>Basic Salary</span>
                                        <span style={{ fontWeight: 500 }}>₹{selectedPayroll.payroll.earnings.basic.toLocaleString('en-IN')}</span>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                        <span>HRA</span>
                                        <span style={{ fontWeight: 500 }}>₹{selectedPayroll.payroll.earnings.hra.toLocaleString('en-IN')}</span>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                                        <span>Special Allowance</span>
                                        <span style={{ fontWeight: 500 }}>₹{selectedPayroll.payroll.earnings.special.toLocaleString('en-IN')}</span>
                                    </div>
                                    <div style={{ borderTop: '2px solid #059669', paddingTop: '0.5rem', fontWeight: 600, display: 'flex', justifyContent: 'space-between', color: '#059669' }}>
                                        <span>Gross Earned</span>
                                        <span>₹{selectedPayroll.payroll.earnings.gross_earned.toLocaleString('en-IN')}</span>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h4 style={{ color: '#dc2626', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <DollarSign size={18} />
                                    Deductions
                                </h4>
                                <div style={{ fontSize: '0.9rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                        <span>Provident Fund</span>
                                        <span style={{ fontWeight: 500 }}>₹{selectedPayroll.payroll.deductions.pf.toLocaleString('en-IN')}</span>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                        <span>Professional Tax</span>
                                        <span style={{ fontWeight: 500 }}>₹{selectedPayroll.payroll.deductions.prof_tax.toLocaleString('en-IN')}</span>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                                        <span>Loss of Pay (LOP)</span>
                                        <span style={{ fontWeight: 500 }}>₹{selectedPayroll.payroll.deductions.lop.toLocaleString('en-IN')}</span>
                                    </div>
                                    <div style={{ borderTop: '2px solid #dc2626', paddingTop: '0.5rem', fontWeight: 600, display: 'flex', justifyContent: 'space-between', color: '#dc2626' }}>
                                        <span>Total Deductions</span>
                                        <span>₹{selectedPayroll.payroll.deductions.total.toLocaleString('en-IN')}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div style={{
                            marginTop: '1.5rem',
                            padding: '1.5rem',
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            borderRadius: '12px',
                            textAlign: 'center',
                            color: 'white'
                        }}>
                            <div style={{ fontSize: '0.875rem', opacity: 0.9, marginBottom: '0.5rem' }}>
                                Net Salary Payable
                            </div>
                            <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>
                                ₹{selectedPayroll.payroll.net_salary.toLocaleString('en-IN')}
                            </div>
                        </div>

                        <button
                            className="btn btn-primary"
                            style={{ width: '100%', marginTop: '1.5rem', display: 'flex', justifyContent: 'center', gap: '0.5rem', padding: '0.75rem' }}
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
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.6)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
    backdropFilter: 'blur(4px)'
};

const labelStyle: React.CSSProperties = {
    display: 'block',
    fontSize: '0.875rem',
    fontWeight: 500,
    color: '#374151',
    marginBottom: '0.5rem'
};
