import { useEffect, useState } from 'react';
import axios from 'axios';
import { Calculator, Download, X, Settings, DollarSign, Users, TrendingUp, Filter, Search, Eye, Save } from 'lucide-react';

interface Employee {
    id: string;
    emp_code: string;
    first_name: string;
    last_name?: string;
    department?: string;
    designation?: string;
    employee_type?: string;
    status: string;
}

interface PayrollData {
    employee_id: string;
    employee_name: string;
    employee_type?: string;
    month: string;
    present_days: number;
    payroll: {
        earnings: {
            basic: number;
            hra: number;
            gross_earned: number;
            special: number;
            conveyance: number;
            medical: number;
            education: number;
            other: number;
            bonus: number;
            incentive: number;
            overtime_regular: number;
            overtime_weekend: number;
            overtime_holiday: number;
            overtime_total: number;
            gross_salary: number;
        };
        deductions: {
            pf: number;
            prof_tax: number;
            lop: number;
            total: number;
            esi: number;
            tds: number;
        };
        net_salary: number;
        ctc: number;
    };
    attendance: {
        total_days: number;
        present_days: number;
        unpaid_leaves: number;
        ot_hours: number;
        ot_weekend_hours: number;
        ot_holiday_hours: number;
        total_hours_worked: number;
    };
    rates: {
        hourly_rate: number | null;
        contract_rate_per_day: number | null;
        base_hourly_rate: number;
        ot_rate_multiplier: number;
        ot_weekend_multiplier: number;
        ot_holiday_multiplier: number;
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
    // Part-time / Contract & OT
    is_hourly_based: boolean;
    hourly_rate: number;
    contract_rate_per_day: number;
    ot_rate_multiplier: number;
    ot_weekend_multiplier: number;
    ot_holiday_multiplier: number;
}

export default function PayrollManagement() {
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [filteredEmployees, setFilteredEmployees] = useState<Employee[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedPayroll, setSelectedPayroll] = useState<PayrollData | null>(null);
    const [processingId, setProcessingId] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [departmentFilter, setDepartmentFilter] = useState('');
    const [viewMode, setViewMode] = useState<'employees' | 'salary_sheet'>('employees');
    const [payrollList, setPayrollList] = useState<any[]>([]);
    const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
    const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
    const [generating, setGenerating] = useState(false);
    const [payrollSummary, setPayrollSummary] = useState({
        total_employees: 0,
        total_gross_salary: 0,
        total_net_salary: 0,
        total_pf_deduction: 0,
        total_esi_deduction: 0
    });

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
        is_esi_applicable: false,
        is_hourly_based: false,
        hourly_rate: 0,
        contract_rate_per_day: 0,
        ot_rate_multiplier: 1.5,
        ot_weekend_multiplier: 2.0,
        ot_holiday_multiplier: 2.5
    });

    useEffect(() => {
        fetchEmployees();
        fetchPayrollSummary();
    }, []);

    const fetchPayrollSummary = async () => {
        try {
            const res = await axios.get('/api/v1/payroll/summary', {
                params: { month: selectedMonth, year: selectedYear }
            });
            setPayrollSummary(res.data);
        } catch (err) {
            console.error("Failed to fetch payroll summary", err);
        }
    };

    useEffect(() => {
        if (viewMode === 'employees') {
            fetchEmployees();
        } else {
            fetchPayrollList();
        }
        fetchPayrollSummary();
    }, [viewMode, selectedMonth, selectedYear]);

    useEffect(() => {
        filterEmployees();
    }, [employees, searchTerm, departmentFilter]);

    const fetchPayrollList = async () => {
        try {
            setLoading(true);
            const res = await axios.get('/api/v1/payroll/list', {
                params: { month: selectedMonth, year: selectedYear }
            });
            setPayrollList(res.data);
        } catch (err) {
            console.error("Failed to fetch payroll list", err);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateAll = async () => {
        if (!confirm(`Generate payroll for all employees for ${selectedMonth}/${selectedYear}?`)) return;
        setGenerating(true);
        try {
            await axios.post('/api/v1/payroll/generate', { month: selectedMonth, year: selectedYear });
            alert("Payroll generated successfully!");
            fetchPayrollList();
            fetchPayrollSummary();
            if (viewMode === 'employees') setViewMode('salary_sheet');
        } catch (err: any) {
            alert("Failed to generate payroll: " + (err.response?.data?.detail || err.message));
        } finally {
            setGenerating(false);
        }
    };

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
            const res = await axios.get(`/api/v1/payroll/employee/${empId}`, {
                params: { month: selectedMonth, year: selectedYear }
            });
            setSelectedPayroll(res.data);
        } catch (err: any) {
            alert("Failed to calculate payroll: " + (err.response?.data?.detail || "Ensure salary is configured."));
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
                is_esi_applicable: false,
                is_hourly_based: false,
                hourly_rate: 0,
                contract_rate_per_day: 0,
                ot_rate_multiplier: 1.5,
                ot_weekend_multiplier: 2.0,
                ot_holiday_multiplier: 2.5
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

    const handleGenerateSingle = async () => {
        if (!selectedPayroll) return;
        if (!confirm(`Generate and save payroll for ${selectedPayroll.employee_name}?`)) return;

        try {
            await axios.post(`/api/v1/payroll/generate/${selectedPayroll.employee_id}`, {
                month: selectedMonth,
                year: selectedYear
            });
            alert("Payroll generated and saved successfully!");
            fetchPayrollSummary(); // Refresh summary stats
        } catch (err: any) {
            alert("Failed to generate payroll: " + (err.response?.data?.detail || err.message));
        }
    };

    const handleDownloadPdf = async () => {
        if (!selectedPayroll) return;
        try {
            const response = await axios.get(`/api/v1/payroll/payslip/${selectedPayroll.employee_id}/pdf`, {
                params: { month: selectedMonth, year: selectedYear },
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



    const departments = Array.from(new Set(employees.map(e => e.department).filter(Boolean)));

    const labelStyle = { fontSize: '0.85rem', fontWeight: 600, color: '#4b5563', display: 'block', marginBottom: '0.25rem' };
    const modalOverlayStyle: any = { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 };

    const handleDownloadPayslip = async (empId: string, empName: string) => {
        try {
            const response = await axios.get(
                `/api/v1/payroll/payslip/${empId}/pdf?month=${selectedMonth}&year=${selectedYear}`,
                { responseType: 'blob' }
            );
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Payslip_${empName.replace(' ', '_')}_${selectedMonth}_${selectedYear}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err: any) {
            alert("Failed to download payslip. Ensure payroll is generated.");
        }
    };

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
                            <p style={{ margin: 0, opacity: 0.9, fontSize: '0.875rem' }}>Total Processed</p>
                            <h2 style={{ margin: '0.5rem 0 0 0', fontSize: '2rem' }}>{payrollSummary.total_employees}</h2>
                        </div>
                        <Users size={48} style={{ opacity: 0.3 }} />
                    </div>
                </div>

                <div className="card" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <p style={{ margin: 0, opacity: 0.9, fontSize: '0.875rem' }}>Total Net Payable</p>
                            <h2 style={{ margin: '0.5rem 0 0 0', fontSize: '2rem' }}>
                                ₹{(payrollSummary.total_net_salary / 1000).toFixed(1)}K
                            </h2>
                        </div>
                        <DollarSign size={48} style={{ opacity: 0.3 }} />
                    </div>
                </div>

                <div className="card" style={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <p style={{ margin: 0, opacity: 0.9, fontSize: '0.875rem' }}>PF / ESI Total</p>
                            <h2 style={{ margin: '0.5rem 0 0 0', fontSize: '2rem' }}>
                                ₹{((payrollSummary.total_pf_deduction + payrollSummary.total_esi_deduction) / 1000).toFixed(1)}K
                            </h2>
                        </div>
                        <TrendingUp size={48} style={{ opacity: 0.3 }} />
                    </div>
                </div>
            </div>

            {/* Controls */}
            <div className="card" style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                        className={`btn ${viewMode === 'employees' ? 'btn-primary' : ''}`}
                        onClick={() => setViewMode('employees')}
                        style={{ border: viewMode === 'employees' ? 'none' : '1px solid #ccc' }}
                    >
                        Employees
                    </button>
                    <button
                        className={`btn ${viewMode === 'salary_sheet' ? 'btn-primary' : ''}`}
                        onClick={() => setViewMode('salary_sheet')}
                        style={{ border: viewMode === 'salary_sheet' ? 'none' : '1px solid #ccc' }}
                    >
                        Salary Sheet
                    </button>
                </div>

                <div style={{ width: '1px', height: '2rem', background: '#e5e7eb', margin: '0 0.5rem' }}></div>

                <select
                    value={selectedMonth}
                    onChange={e => setSelectedMonth(Number(e.target.value))}
                    className="input"
                    style={{ width: '120px' }}
                >
                    {Array.from({ length: 12 }, (_, i) => (
                        <option key={i + 1} value={i + 1}>{new Date(0, i).toLocaleString('default', { month: 'long' })}</option>
                    ))}
                </select>

                <select
                    value={selectedYear}
                    onChange={e => setSelectedYear(Number(e.target.value))}
                    className="input"
                    style={{ width: '100px' }}
                >
                    <option value={2025}>2025</option>
                    <option value={2026}>2026</option>
                </select>

                <div style={{ flex: 1 }}></div>

                <button
                    className="btn"
                    onClick={handleGenerateAll}
                    disabled={generating}
                    style={{ background: '#059669', color: 'white', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                >
                    <Calculator size={18} />
                    {generating ? 'Generating...' : 'Generate All Payroll'}
                </button>
            </div>
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

            {viewMode === 'employees' ? (
                /* ... employees table ... */
                <div className="card">
                    <div className="table-container">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Employee</th>
                                    <th>Code</th>
                                    <th>Type</th>
                                    <th>Department</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredEmployees.length === 0 ? (
                                    <tr>
                                        <td colSpan={5} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                                            No employees found
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
                                                <span style={{ fontFamily: 'monospace', fontWeight: 600 }}>{emp.emp_code}</span>
                                            </td>
                                            <td>
                                                <span className={`badge ${emp.employee_type === 'contract' ? 'badge-warning' : 'badge-primary'}`}>
                                                    {emp.employee_type || 'Staff'}
                                                </span>
                                            </td>
                                            <td>{emp.department || '-'}</td>
                                            <td>
                                                <button
                                                    className="btn"
                                                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', padding: '0.4rem 0.6rem', background: '#f3f4f6' }}
                                                    onClick={() => handleOpenConfig(emp.id, `${emp.first_name} ${emp.last_name || ''}`)}
                                                >
                                                    <Settings size={14} /> Configure
                                                </button>
                                                <button
                                                    className="btn"
                                                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', padding: '0.4rem 0.6rem', background: '#dbeafe', color: '#1e40af', opacity: processingId === emp.id ? 0.7 : 1 }}
                                                    onClick={() => handleRunPayroll(emp.id)}
                                                    disabled={processingId === emp.id}
                                                    title="Preview Payroll"
                                                >
                                                    {processingId === emp.id ? (
                                                        <span>...</span>
                                                    ) : (
                                                        <>
                                                            <Eye size={14} /> Preview
                                                        </>
                                                    )}
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            ) : (
                /* Salary Sheet Table */
                <div className="card">
                    <div className="table-container" style={{ overflowX: 'auto' }}>
                        <table className="table" style={{ fontSize: '0.85rem' }}>
                            <thead>
                                <tr style={{ background: '#f8fafc' }}>
                                    <th>Code</th>
                                    <th>Employee</th>
                                    <th>Days</th>
                                    <th>Gross</th>
                                    <th>Basic</th>
                                    <th>HRA</th>
                                    <th>Conveyance</th>
                                    <th>Other</th>
                                    <th>OT</th>
                                    <th style={{ borderLeft: '2px solid #ddd' }}>PF</th>
                                    <th>ESI</th>
                                    <th>PT</th>
                                    <th style={{ background: '#fef08a', borderLeft: '1px solid #eab308', borderRight: '1px solid #eab308' }}>Welfare</th>
                                    <th>Loan</th>
                                    <th style={{ borderLeft: '2px solid #ddd' }}>Total Ded</th>
                                    <th style={{ background: '#f0fdf4', fontWeight: 700 }}>NET SALARY</th>
                                    <th style={{ textAlign: 'center' }}>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {payrollList.length === 0 ? (
                                    <tr>
                                        <td colSpan={17} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                                            No payroll records generated for {new Date(0, selectedMonth - 1).toLocaleString('default', { month: 'long' })} {selectedYear}.
                                            <br />
                                            <span style={{ fontSize: '0.9rem' }}>Click "Generate All Payroll" to process.</span>
                                        </td>
                                    </tr>
                                ) : (
                                    payrollList.map(p => (
                                        <tr key={p.id}>
                                            <td style={{ fontFamily: 'monospace' }}>{p.emp_code}</td>
                                            <td style={{ fontWeight: 500 }}>{p.employee_name}</td>
                                            <td>{p.present_days}</td>
                                            <td style={{ fontWeight: 600 }}>{p.gross_salary}</td>
                                            <td>{p.basic_earned}</td>
                                            <td>{p.hra_earned || 0}</td>
                                            <td>{p.conveyance_earned || 0}</td>
                                            <td>{p.other_allowances || 0}</td>
                                            <td>{p.ot_amount || 0}</td>
                                            <td style={{ borderLeft: '2px solid #eee' }}>{p.pf_amount || 0}</td>
                                            <td>{p.esi_amount || 0}</td>
                                            <td>{p.pt_amount || 0}</td>
                                            <td style={{ background: '#fefce8', borderLeft: '1px solid #fef08a', borderRight: '1px solid #fef08a', fontWeight: 600 }}>
                                                {p.welfare_fund || 0}
                                            </td>
                                            <td>{p.loan_deduction || 0}</td>
                                            <td style={{ borderLeft: '2px solid #eee', color: '#dc2626' }}>{p.total_deductions}</td>
                                            <td style={{ background: '#f0fdf4', fontWeight: 700, color: '#16a34a', fontSize: '1rem' }}>
                                                {p.net_salary}
                                            </td>
                                            <td style={{ textAlign: 'center' }}>
                                                <button
                                                    onClick={() => handleDownloadPayslip(p.employee_id, p.employee_name)}
                                                    className="btn btn-icon"
                                                    title="Download Payslip"
                                                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#4f46e5' }}
                                                >
                                                    <Download size={16} />
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

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
                            {/* Employment Type & Rates Section */}
                            <div>
                                <h4 style={{ margin: '0 0 1rem 0', color: '#7c3aed', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <Users size={18} />
                                    Employment Type & Rates
                                </h4>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', gridColumn: 'span 2', padding: '1rem', background: '#f0f9ff', borderRadius: '8px', border: '1px solid #bae6fd' }}>
                                        <input
                                            type="checkbox"
                                            checked={salaryForm.is_hourly_based}
                                            onChange={e => setSalaryForm({ ...salaryForm, is_hourly_based: e.target.checked })}
                                            style={{ width: '20px', height: '20px', cursor: 'pointer' }}
                                        />
                                        <div>
                                            <span style={{ fontWeight: 600, display: 'block', color: '#0369a1' }}>Worker (Daily Rate Based)</span>
                                            <span style={{ fontSize: '0.8rem', color: '#0c4a6e' }}>Check this for Daily Wages. Uncheck for Staff (Monthly Salary).</span>
                                        </div>
                                    </label>

                                    {salaryForm.is_hourly_based && (
                                        <div>
                                            <label style={labelStyle}>Hourly Rate (₹)</label>
                                            <input
                                                type="number"
                                                className="input"
                                                value={salaryForm.hourly_rate}
                                                onChange={e => setSalaryForm({ ...salaryForm, hourly_rate: Number(e.target.value) })}
                                                placeholder="e.g., 200"
                                            />
                                        </div>
                                    )}

                                    <div>
                                        <label style={labelStyle}>Contract Rate (Per Day)</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.contract_rate_per_day}
                                            onChange={e => setSalaryForm({ ...salaryForm, contract_rate_per_day: Number(e.target.value) })}
                                            placeholder="e.g., 1000"
                                        />
                                        <span style={{ fontSize: '0.75rem', color: '#666' }}>For contract workers</span>
                                    </div>
                                </div>

                                <h5 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: '#555' }}>Overtime Multipliers</h5>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                                    <div>
                                        <label style={labelStyle}>Weekday OT</label>
                                        <input
                                            type="number"
                                            className="input"
                                            step="0.1"
                                            value={salaryForm.ot_rate_multiplier}
                                            onChange={e => setSalaryForm({ ...salaryForm, ot_rate_multiplier: Number(e.target.value) })}
                                            placeholder="1.5"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Weekend OT</label>
                                        <input
                                            type="number"
                                            className="input"
                                            step="0.1"
                                            value={salaryForm.ot_weekend_multiplier}
                                            onChange={e => setSalaryForm({ ...salaryForm, ot_weekend_multiplier: Number(e.target.value) })}
                                            placeholder="2.0"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Holiday OT</label>
                                        <input
                                            type="number"
                                            className="input"
                                            step="0.1"
                                            value={salaryForm.ot_holiday_multiplier}
                                            onChange={e => setSalaryForm({ ...salaryForm, ot_holiday_multiplier: Number(e.target.value) })}
                                            placeholder="2.5"
                                        />
                                    </div>
                                </div>
                            </div>
                            {/* Earnings Section */}
                            <div>
                                <h4 style={{ margin: '0 0 1rem 0', color: '#059669', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <TrendingUp size={18} />
                                    Earnings & Allowances
                                </h4>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                    <div>
                                        <label style={labelStyle}>Basic {salaryForm.is_hourly_based ? '(Per Day)' : '(Monthly)'} *</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.basic_salary}
                                            onChange={e => setSalaryForm({ ...salaryForm, basic_salary: Number(e.target.value) })}
                                            placeholder="e.g., 15000"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>HRA {salaryForm.is_hourly_based ? '(Per Day)' : '(Monthly)'}</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.hra}
                                            onChange={e => setSalaryForm({ ...salaryForm, hra: Number(e.target.value) })}
                                            placeholder="e.g., 5000"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Conveyance {salaryForm.is_hourly_based ? '(Per Day)' : '(Monthly)'}</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.conveyance_allowance}
                                            onChange={e => setSalaryForm({ ...salaryForm, conveyance_allowance: Number(e.target.value) })}
                                            placeholder="e.g., 1600"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Medical {salaryForm.is_hourly_based ? '(Per Day)' : '(Monthly)'}</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.medical_allowance}
                                            onChange={e => setSalaryForm({ ...salaryForm, medical_allowance: Number(e.target.value) })}
                                            placeholder="e.g., 1250"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Special {salaryForm.is_hourly_based ? '(Per Day)' : '(Monthly)'}</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.special_allowance}
                                            onChange={e => setSalaryForm({ ...salaryForm, special_allowance: Number(e.target.value) })}
                                            placeholder="e.g., 3000"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Education {salaryForm.is_hourly_based ? '(Per Day)' : '(Monthly)'}</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.education_allowance}
                                            onChange={e => setSalaryForm({ ...salaryForm, education_allowance: Number(e.target.value) })}
                                            placeholder="e.g., 100"
                                        />
                                    </div>
                                    <div>
                                        <label style={labelStyle}>Other {salaryForm.is_hourly_based ? '(Per Day)' : '(Monthly)'}</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={salaryForm.other_allowance}
                                            onChange={e => setSalaryForm({ ...salaryForm, other_allowance: Number(e.target.value) })}
                                            placeholder="e.g., 500"
                                        />
                                    </div>
                                </div>

                                {salaryForm.is_hourly_based && (
                                    <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#ecfeff', borderRadius: '6px', border: '1px solid #a5f3fc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <span style={{ color: '#0e7490', fontWeight: 600 }}>Total Daily Rate:</span>
                                        <span style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0891b2' }}>
                                            ₹{(
                                                (salaryForm.basic_salary || 0) +
                                                (salaryForm.hra || 0) +
                                                (salaryForm.conveyance_allowance || 0) +
                                                (salaryForm.medical_allowance || 0) +
                                                (salaryForm.special_allowance || 0) +
                                                (salaryForm.education_allowance || 0) +
                                                (salaryForm.other_allowance || 0)
                                            ).toFixed(2)}
                                        </span>
                                    </div>
                                )}
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
            )
            }

            {/* Payslip Modal */}
            {
                selectedPayroll && (
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
                                        {selectedPayroll.rates?.hourly_rate ? (
                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                                <span>Hourly Pay ({(selectedPayroll.attendance?.total_hours_worked || 0)} hrs @ ₹{selectedPayroll.rates.hourly_rate}/hr)</span>
                                                <span style={{ fontWeight: 500 }}>₹{(selectedPayroll.rates.hourly_rate * (selectedPayroll.attendance?.total_hours_worked || 0)).toLocaleString('en-IN')}</span>
                                            </div>
                                        ) : selectedPayroll.rates?.contract_rate_per_day ? (
                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                                <span>Daily Pay ({(selectedPayroll.attendance?.present_days || 0)} days @ ₹{selectedPayroll.rates.contract_rate_per_day}/day)</span>
                                                <span style={{ fontWeight: 500 }}>₹{(selectedPayroll.rates.contract_rate_per_day * (selectedPayroll.attendance?.present_days || 0)).toLocaleString('en-IN')}</span>
                                            </div>
                                        ) : (
                                            <>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                                    <span>Basic Salary</span>
                                                    <span style={{ fontWeight: 500 }}>₹{(selectedPayroll.payroll?.earnings?.basic || 0).toLocaleString('en-IN')}</span>
                                                </div>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                                    <span>HRA</span>
                                                    <span style={{ fontWeight: 500 }}>₹{(selectedPayroll.payroll?.earnings?.hra || 0).toLocaleString('en-IN')}</span>
                                                </div>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                                                    <span>Special Allowance</span>
                                                    <span style={{ fontWeight: 500 }}>₹{(selectedPayroll.payroll?.earnings?.special || 0).toLocaleString('en-IN')}</span>
                                                </div>
                                            </>
                                        )}

                                        {/* Overtime Section */}
                                        {((selectedPayroll.attendance?.ot_hours || 0) > 0 || (selectedPayroll.attendance?.ot_weekend_hours || 0) > 0 || (selectedPayroll.attendance?.ot_holiday_hours || 0) > 0) && (
                                            <div style={{ marginTop: '0.75rem', padding: '0.5rem', background: '#ecfdf5', borderRadius: '4px' }}>
                                                <div style={{ fontWeight: 600, color: '#059669', marginBottom: '0.25rem' }}>Overtime Earnings</div>
                                                {(selectedPayroll.attendance?.ot_hours || 0) > 0 && (
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                                                        <span>Regular ({(selectedPayroll.attendance?.ot_hours || 0)} hrs)</span>
                                                        <span>₹{(selectedPayroll.payroll?.earnings?.overtime_regular || 0).toLocaleString('en-IN')}</span>
                                                    </div>
                                                )}
                                                {(selectedPayroll.attendance?.ot_weekend_hours || 0) > 0 && (
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                                                        <span>Weekend ({(selectedPayroll.attendance?.ot_weekend_hours || 0)} hrs)</span>
                                                        <span>₹{(selectedPayroll.payroll?.earnings?.overtime_weekend || 0).toLocaleString('en-IN')}</span>
                                                    </div>
                                                )}
                                                {(selectedPayroll.attendance?.ot_holiday_hours || 0) > 0 && (
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                                                        <span>Holiday ({(selectedPayroll.attendance?.ot_holiday_hours || 0)} hrs)</span>
                                                        <span>₹{(selectedPayroll.payroll?.earnings?.overtime_holiday || 0).toLocaleString('en-IN')}</span>
                                                    </div>
                                                )}
                                                <div style={{ borderTop: '1px dashed #059669', marginTop: '0.25rem', paddingTop: '0.25rem', display: 'flex', justifyContent: 'space-between', fontWeight: 500 }}>
                                                    <span>Total OT</span>
                                                    <span>₹{(selectedPayroll.payroll?.earnings?.overtime_total || 0).toLocaleString('en-IN')}</span>
                                                </div>
                                            </div>
                                        )}

                                        <div style={{ borderTop: '2px solid #059669', paddingTop: '0.5rem', marginTop: '0.75rem', fontWeight: 600, display: 'flex', justifyContent: 'space-between', color: '#059669' }}>
                                            <span>Gross Earned</span>
                                            <span>₹{(selectedPayroll.payroll?.earnings?.gross_earned || 0).toLocaleString('en-IN')}</span>
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
                                            <span style={{ fontWeight: 500 }}>₹{(selectedPayroll.payroll?.deductions?.pf || 0).toLocaleString('en-IN')}</span>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                            <span>ESI</span>
                                            <span style={{ fontWeight: 500 }}>₹{(selectedPayroll.payroll?.deductions?.esi || 0).toLocaleString('en-IN')}</span>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                            <span>Professional Tax</span>
                                            <span style={{ fontWeight: 500 }}>₹{(selectedPayroll.payroll?.deductions?.prof_tax || 0).toLocaleString('en-IN')}</span>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                            <span>TDS</span>
                                            <span style={{ fontWeight: 500 }}>₹{(selectedPayroll.payroll?.deductions?.tds || 0).toLocaleString('en-IN')}</span>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                                            <span>Loss of Pay (LOP)</span>
                                            <span style={{ fontWeight: 500 }}>₹{(selectedPayroll.payroll?.deductions?.lop || 0).toLocaleString('en-IN')}</span>
                                        </div>
                                        <div style={{ borderTop: '2px solid #dc2626', paddingTop: '0.5rem', fontWeight: 600, display: 'flex', justifyContent: 'space-between', color: '#dc2626' }}>
                                            <span>Total Deductions</span>
                                            <span>₹{(selectedPayroll.payroll?.deductions?.total || 0).toLocaleString('en-IN')}</span>
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
                                    ₹{(selectedPayroll.payroll?.net_salary || 0).toLocaleString('en-IN')}
                                </div>
                            </div>

                            <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                                <button
                                    className="btn"
                                    style={{ flex: 1, display: 'flex', justifyContent: 'center', gap: '0.5rem', padding: '0.75rem', background: '#ecfdf5', color: '#059669', border: '1px solid #059669' }}
                                    onClick={handleGenerateSingle}
                                >
                                    <Save size={18} /> Approve &amp; Save
                                </button>
                                <button
                                    className="btn btn-primary"
                                    style={{ flex: 1, display: 'flex', justifyContent: 'center', gap: '0.5rem', padding: '0.75rem' }}
                                    onClick={handleDownloadPdf}
                                >
                                    <Download size={18} /> Download PDF
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }
        </div>
    );
}


