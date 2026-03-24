import { useEffect, useState } from 'react';
import axios from 'axios';
import { Plus, Trash2, FileText, X, Search, AlertCircle, Wallet, CreditCard } from 'lucide-react';

interface Employee {
    id: string;
    emp_code: string;
    first_name: string;
    last_name?: string;
    department?: string;
}

interface Loan {
    id: string;
    employee_id: string;
    employee_name: string;
    emp_code: string;
    loan_type: string;
    loan_amount: number;
    emi_amount: number;
    total_emis: number;
    remaining_emis: number;
    start_date: string;
    end_date?: string;
    reason?: string;
    status: string;
    created_at: string;
}

interface OutstandingReport {
    report_date: string;
    total_employees: number;
    total_outstanding_amount: number;
    loans: Array<{
        loan_id: string;
        employee_id: string;
        employee_name: string;
        emp_code: string;
        department: string;
        loan_type: string;
        original_amount: number;
        emi_amount: number;
        total_emis: number;
        remaining_emis: number;
        outstanding_amount: number;
        start_date: string;
        end_date?: string;
    }>;
}

export default function LoanManagement() {
    const [loans, setLoans] = useState<Loan[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [showReportModal, setShowReportModal] = useState(false);
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    const [outstandingReport, setOutstandingReport] = useState<OutstandingReport | null>(null);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // Form state
    const [formData, setFormData] = useState({
        employee_id: '',
        loan_type: 'loan',
        loan_amount: 0,
        emi_amount: 0,
        total_emis: 1,
        start_date: new Date().toISOString().split('T')[0],
        reason: ''
    });

    // Searchable dropdown state
    const [employeeSearch, setEmployeeSearch] = useState('');
    const [showEmployeeDropdown, setShowEmployeeDropdown] = useState(false);

    const API_URL = (import.meta.env.VITE_API_BASE_URL || 'https://api.t3sol.in') + '/api/v1';

    useEffect(() => {
        fetchLoans();
        fetchEmployees();
    }, []);

    const fetchLoans = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('admin_token');
            const params = statusFilter ? `?status=${statusFilter}` : '';
            const response = await axios.get(`${API_URL}/loans${params}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setLoans(response.data);
        } catch (err: any) {
            setError('Failed to fetch loans');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const fetchEmployees = async () => {
        try {
            const token = localStorage.getItem('admin_token');
            const response = await axios.get(`${API_URL}/employees`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setEmployees(response.data);
        } catch (err: any) {
            console.error('Failed to fetch employees:', err);
        }
    };

    const fetchOutstandingReport = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('admin_token');
            const response = await axios.get(`${API_URL}/loans/outstanding-report`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setOutstandingReport(response.data);
            setShowReportModal(true);
        } catch (err: any) {
            setError('Failed to fetch outstanding report');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateLoan = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('admin_token');
            await axios.post(`${API_URL}/loans`, formData, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setSuccess('Loan/Advance created successfully');
            setShowModal(false);
            setFormData({
                employee_id: '',
                loan_type: 'loan',
                loan_amount: 0,
                emi_amount: 0,
                total_emis: 1,
                start_date: new Date().toISOString().split('T')[0],
                reason: ''
            });
            fetchLoans();
            setTimeout(() => setSuccess(''), 3000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to create loan');
            setTimeout(() => setError(''), 3000);
        }
    };

    const handleDeleteLoan = async (loanId: string) => {
        if (!confirm('Are you sure you want to cancel this loan?')) return;
        try {
            const token = localStorage.getItem('admin_token');
            await axios.delete(`${API_URL}/loans/${loanId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setSuccess('Loan cancelled successfully');
            fetchLoans();
            setTimeout(() => setSuccess(''), 3000);
        } catch (err: any) {
            setError('Failed to cancel loan');
            setTimeout(() => setError(''), 3000);
        }
    };

    const calculateEMI = () => {
        if (formData.loan_amount > 0 && formData.total_emis > 0) {
            const emi = formData.loan_amount / formData.total_emis;
            setFormData({ ...formData, emi_amount: Math.round(emi * 100) / 100 });
        }
    };

    const filteredLoans = loans.filter(loan => {
        const matchesSearch = loan.employee_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            loan.emp_code.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = !statusFilter || loan.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    const filteredEmployees = employees.filter(emp =>
        `${emp.first_name} ${emp.last_name || ''}`.toLowerCase().includes(employeeSearch.toLowerCase()) ||
        emp.emp_code.toLowerCase().includes(employeeSearch.toLowerCase())
    );

    const selectedEmployee = employees.find(e => e.id === formData.employee_id);

    return (
        <div style={{
            padding: '20px',
            minHeight: '100vh',
            background: '#f8fafc'
        }}>
            {/* Header */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '24px',
                flexWrap: 'wrap',
                gap: '16px'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        padding: '12px',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <Wallet size={24} color="white" />
                    </div>
                    <div>
                        <h1 style={{
                            margin: 0,
                            fontSize: 'clamp(1.5rem, 4vw, 2rem)',
                            fontWeight: 700,
                            color: '#1e293b'
                        }}>
                            Loan & Advance Management
                        </h1>
                        <p style={{
                            margin: 0,
                            color: '#64748b',
                            fontSize: 'clamp(0.875rem, 2vw, 1rem)'
                        }}>
                            Manage employee loans and track EMI deductions
                        </p>
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                    <button
                        className="btn"
                        onClick={fetchOutstandingReport}
                        style={{
                            background: 'white',
                            border: '1px solid #e2e8f0',
                            padding: '10px 20px',
                            borderRadius: '10px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            cursor: 'pointer',
                            fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                            color: '#475569',
                            fontWeight: 500,
                            boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                        }}
                    >
                        <FileText size={18} />
                        Outstanding Report
                    </button>
                    <button
                        onClick={() => setShowModal(true)}
                        style={{
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            border: 'none',
                            padding: '10px 20px',
                            borderRadius: '10px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            cursor: 'pointer',
                            fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                            color: 'white',
                            fontWeight: 600,
                            boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)'
                        }}
                    >
                        <Plus size={18} />
                        New Loan/Advance
                    </button>
                </div>
            </div>

            {/* Alerts */}
            {error && (
                <div style={{
                    padding: '16px',
                    background: '#fef2f2',
                    border: '1px solid #fecaca',
                    borderRadius: '12px',
                    marginBottom: '20px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    color: '#dc2626',
                    fontSize: 'clamp(0.875rem, 2vw, 1rem)'
                }}>
                    <AlertCircle size={20} />
                    {error}
                </div>
            )}
            {success && (
                <div style={{
                    padding: '16px',
                    background: '#f0fdf4',
                    border: '1px solid #bbf7d0',
                    borderRadius: '12px',
                    marginBottom: '20px',
                    color: '#16a34a',
                    fontSize: 'clamp(0.875rem, 2vw, 1rem)'
                }}>
                    {success}
                </div>
            )}

            {/* Filters */}
            <div style={{
                display: 'flex',
                gap: '16px',
                marginBottom: '24px',
                flexWrap: 'wrap',
                background: 'white',
                padding: '20px',
                borderRadius: '16px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
            }}>
                <div style={{
                    flex: '1',
                    minWidth: '280px',
                    position: 'relative'
                }}>
                    <Search size={20} style={{
                        position: 'absolute',
                        left: '16px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        color: '#94a3b8'
                    }} />
                    <input
                        type="text"
                        placeholder="Search by employee name or code..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '12px 16px 12px 48px',
                            border: '1px solid #e2e8f0',
                            borderRadius: '10px',
                            fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                            outline: 'none',
                            boxSizing: 'border-box'
                        }}
                    />
                </div>
                <select
                    value={statusFilter}
                    onChange={(e) => {
                        setStatusFilter(e.target.value);
                        fetchLoans();
                    }}
                    style={{
                        padding: '12px 16px',
                        border: '1px solid #e2e8f0',
                        borderRadius: '10px',
                        fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                        background: 'white',
                        color: '#475569',
                        minWidth: '150px',
                        cursor: 'pointer'
                    }}
                >
                    <option value="">All Status</option>
                    <option value="active">Active</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                </select>
            </div>

            {/* Loans Table */}
            <div style={{
                background: 'white',
                borderRadius: '16px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                overflow: 'hidden'
            }}>
                {loading ? (
                    <div style={{
                        padding: '60px',
                        textAlign: 'center',
                        color: '#64748b',
                        fontSize: 'clamp(1rem, 3vw, 1.25rem)'
                    }}>
                        Loading loans...
                    </div>
                ) : filteredLoans.length === 0 ? (
                    <div style={{
                        padding: '60px',
                        textAlign: 'center',
                        color: '#64748b',
                        fontSize: 'clamp(1rem, 3vw, 1.25rem)'
                    }}>
                        <Wallet size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
                        <p>No loans found</p>
                    </div>
                ) : (
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{
                            width: '100%',
                            borderCollapse: 'collapse',
                            minWidth: '800px'
                        }}>
                            <thead>
                                <tr style={{
                                    background: '#f8fafc',
                                    borderBottom: '1px solid #e2e8f0'
                                }}>
                                    <th style={{
                                        padding: '16px',
                                        textAlign: 'left',
                                        fontWeight: 600,
                                        color: '#475569',
                                        fontSize: 'clamp(0.75rem, 2vw, 0.875rem)',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.05em'
                                    }}>Employee</th>
                                    <th style={{
                                        padding: '16px',
                                        textAlign: 'left',
                                        fontWeight: 600,
                                        color: '#475569',
                                        fontSize: 'clamp(0.75rem, 2vw, 0.875rem)',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.05em'
                                    }}>Type</th>
                                    <th style={{
                                        padding: '16px',
                                        textAlign: 'right',
                                        fontWeight: 600,
                                        color: '#475569',
                                        fontSize: 'clamp(0.75rem, 2vw, 0.875rem)',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.05em'
                                    }}>Loan Amount</th>
                                    <th style={{
                                        padding: '16px',
                                        textAlign: 'right',
                                        fontWeight: 600,
                                        color: '#475569',
                                        fontSize: 'clamp(0.75rem, 2vw, 0.875rem)',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.05em'
                                    }}>EMI</th>
                                    <th style={{
                                        padding: '16px',
                                        textAlign: 'center',
                                        fontWeight: 600,
                                        color: '#475569',
                                        fontSize: 'clamp(0.75rem, 2vw, 0.875rem)',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.05em'
                                    }}>Total EMIs</th>
                                    <th style={{
                                        padding: '16px',
                                        textAlign: 'center',
                                        fontWeight: 600,
                                        color: '#475569',
                                        fontSize: 'clamp(0.75rem, 2vw, 0.875rem)',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.05em'
                                    }}>Remaining</th>
                                    <th style={{
                                        padding: '16px',
                                        textAlign: 'left',
                                        fontWeight: 600,
                                        color: '#475569',
                                        fontSize: 'clamp(0.75rem, 2vw, 0.875rem)',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.05em'
                                    }}>Start Date</th>
                                    <th style={{
                                        padding: '16px',
                                        textAlign: 'center',
                                        fontWeight: 600,
                                        color: '#475569',
                                        fontSize: 'clamp(0.75rem, 2vw, 0.875rem)',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.05em'
                                    }}>Status</th>
                                    <th style={{
                                        padding: '16px',
                                        textAlign: 'center',
                                        fontWeight: 600,
                                        color: '#475569',
                                        fontSize: 'clamp(0.75rem, 2vw, 0.875rem)',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.05em'
                                    }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredLoans.map((loan, index) => (
                                    <tr key={loan.id} style={{
                                        borderBottom: '1px solid #f1f5f9',
                                        background: index % 2 === 0 ? 'white' : '#fafafa',
                                        transition: 'background 0.2s'
                                    }}>
                                        <td style={{ padding: '16px' }}>
                                            <div style={{ fontWeight: 600, color: '#1e293b' }}>
                                                {loan.employee_name}
                                            </div>
                                            <div style={{ color: '#64748b', fontSize: 'clamp(0.75rem, 2vw, 0.875rem)' }}>
                                                {loan.emp_code}
                                            </div>
                                        </td>
                                        <td style={{ padding: '16px' }}>
                                            <span style={{
                                                padding: '6px 12px',
                                                borderRadius: '20px',
                                                fontSize: 'clamp(0.75rem, 2vw, 0.875rem)',
                                                fontWeight: 500,
                                                background: loan.loan_type === 'loan'
                                                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                                                    : '#f0f9ff',
                                                color: loan.loan_type === 'loan' ? 'white' : '#0369a1'
                                            }}>
                                                {loan.loan_type === 'loan' ? '💰 Loan' : '💵 Advance'}
                                            </span>
                                        </td>
                                        <td style={{
                                            padding: '16px',
                                            textAlign: 'right',
                                            fontWeight: 600,
                                            color: '#1e293b',
                                            fontSize: 'clamp(0.875rem, 2vw, 1rem)'
                                        }}>
                                            ₹{loan.loan_amount.toLocaleString()}
                                        </td>
                                        <td style={{
                                            padding: '16px',
                                            textAlign: 'right',
                                            color: '#475569'
                                        }}>
                                            ₹{loan.emi_amount.toLocaleString()}/mo
                                        </td>
                                        <td style={{
                                            padding: '16px',
                                            textAlign: 'center',
                                            color: '#475569'
                                        }}>
                                            {loan.total_emis}
                                        </td>
                                        <td style={{
                                            padding: '16px',
                                            textAlign: 'center',
                                            fontWeight: 600,
                                            color: loan.remaining_emis > 0 ? '#f59e0b' : '#22c55e'
                                        }}>
                                            {loan.remaining_emis}
                                        </td>
                                        <td style={{
                                            padding: '16px',
                                            color: '#475569'
                                        }}>
                                            {loan.start_date}
                                        </td>
                                        <td style={{ padding: '16px', textAlign: 'center' }}>
                                            <span style={{
                                                padding: '6px 12px',
                                                borderRadius: '20px',
                                                fontSize: 'clamp(0.75rem, 2vw, 0.875rem)',
                                                fontWeight: 500,
                                                background: loan.status === 'active' ? '#dcfce7' :
                                                    loan.status === 'completed' ? '#e0f2fe' : '#fee2e2',
                                                color: loan.status === 'active' ? '#16a34a' :
                                                    loan.status === 'completed' ? '#0284c7' : '#dc2626'
                                            }}>
                                                {loan.status}
                                            </span>
                                        </td>
                                        <td style={{ padding: '16px', textAlign: 'center' }}>
                                            <button
                                                onClick={() => handleDeleteLoan(loan.id)}
                                                disabled={loan.status !== 'active'}
                                                style={{
                                                    background: loan.status === 'active' ? '#fee2e2' : '#f1f5f9',
                                                    border: 'none',
                                                    padding: '8px',
                                                    borderRadius: '8px',
                                                    cursor: loan.status === 'active' ? 'pointer' : 'not-allowed',
                                                    color: loan.status === 'active' ? '#dc2626' : '#cbd5e1',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    margin: '0 auto'
                                                }}
                                                title="Cancel Loan"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Create Loan Modal */}
            {showModal && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0,0,0,0.5)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000,
                    padding: '20px'
                }} onClick={() => setShowModal(false)}>
                    <div style={{
                        background: 'white',
                        borderRadius: '20px',
                        width: '100%',
                        maxWidth: '560px',
                        maxHeight: '90vh',
                        overflow: 'auto',
                        boxShadow: '0 20px 50px rgba(0,0,0,0.2)'
                    }} onClick={(e) => e.stopPropagation()}>
                        <div style={{
                            padding: '24px',
                            borderBottom: '1px solid #e2e8f0',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center'
                        }}>
                            <h2 style={{
                                margin: 0,
                                fontSize: 'clamp(1.25rem, 3vw, 1.5rem)',
                                fontWeight: 700,
                                color: '#1e293b'
                            }}>
                                Create New Loan/Advance
                            </h2>
                            <button
                                onClick={() => setShowModal(false)}
                                style={{
                                    background: '#f1f5f9',
                                    border: 'none',
                                    padding: '10px',
                                    borderRadius: '10px',
                                    cursor: 'pointer',
                                    display: 'flex'
                                }}
                            >
                                <X size={20} color="#64748b" />
                            </button>
                        </div>
                        <form onSubmit={handleCreateLoan} style={{ padding: '24px' }}>
                            <div style={{ marginBottom: '20px' }}>
                                <label style={{
                                    display: 'block',
                                    marginBottom: '8px',
                                    fontWeight: 600,
                                    color: '#374151',
                                    fontSize: 'clamp(0.875rem, 2vw, 1rem)'
                                }}>
                                    Employee *
                                </label>
                                <div style={{ position: 'relative' }}>
                                    <div
                                        onClick={() => setShowEmployeeDropdown(!showEmployeeDropdown)}
                                        style={{
                                            width: '100%',
                                            padding: '12px 16px',
                                            border: '1px solid #e2e8f0',
                                            borderRadius: '10px',
                                            fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                                            background: 'white',
                                            cursor: 'pointer',
                                            display: 'flex',
                                            justifyContent: 'space-between',
                                            alignItems: 'center',
                                            boxSizing: 'border-box',
                                            minHeight: '48px'
                                        }}
                                    >
                                        {selectedEmployee ? (
                                            <span style={{ color: '#1e293b' }}>
                                                {selectedEmployee.first_name} {selectedEmployee.last_name || ''} ({selectedEmployee.emp_code})
                                            </span>
                                        ) : (
                                            <span style={{ color: '#94a3b8' }}>Search employee...</span>
                                        )}
                                        <span style={{ color: '#94a3b8' }}>▼</span>
                                    </div>

                                    {showEmployeeDropdown && (
                                        <div style={{
                                            position: 'absolute',
                                            top: '100%',
                                            left: 0,
                                            right: 0,
                                            background: 'white',
                                            border: '1px solid #e2e8f0',
                                            borderRadius: '10px',
                                            marginTop: '4px',
                                            maxHeight: '250px',
                                            overflow: 'auto',
                                            zIndex: 100,
                                            boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                                        }}>
                                            <div style={{ padding: '12px', borderBottom: '1px solid #e2e8f0' }}>
                                                <input
                                                    type="text"
                                                    placeholder="Search by name or code..."
                                                    value={employeeSearch}
                                                    onChange={(e) => setEmployeeSearch(e.target.value)}
                                                    autoFocus
                                                    style={{
                                                        width: '100%',
                                                        padding: '10px 12px',
                                                        border: '1px solid #e2e8f0',
                                                        borderRadius: '8px',
                                                        fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                                                        boxSizing: 'border-box',
                                                        outline: 'none'
                                                    }}
                                                    onClick={(e) => e.stopPropagation()}
                                                />
                                            </div>
                                            <div style={{ maxHeight: '200px', overflow: 'auto' }}>
                                                {filteredEmployees.length === 0 ? (
                                                    <div style={{
                                                        padding: '16px',
                                                        textAlign: 'center',
                                                        color: '#64748b'
                                                    }}>
                                                        No employees found
                                                    </div>
                                                ) : (
                                                    filteredEmployees.map((emp) => (
                                                        <div
                                                            key={emp.id}
                                                            onClick={() => {
                                                                setFormData({ ...formData, employee_id: emp.id });
                                                                setEmployeeSearch('');
                                                                setShowEmployeeDropdown(false);
                                                            }}
                                                            style={{
                                                                padding: '12px 16px',
                                                                cursor: 'pointer',
                                                                borderBottom: '1px solid #f1f5f9',
                                                                transition: 'background 0.2s',
                                                                background: formData.employee_id === emp.id ? '#f0f4ff' : 'white'
                                                            }}
                                                            onMouseEnter={(e) => e.currentTarget.style.background = '#f8fafc'}
                                                            onMouseLeave={(e) => e.currentTarget.style.background = formData.employee_id === emp.id ? '#f0f4ff' : 'white'}
                                                        >
                                                            <div style={{ fontWeight: 600, color: '#1e293b' }}>
                                                                {emp.first_name} {emp.last_name || ''}
                                                            </div>
                                                            <div style={{ color: '#64748b', fontSize: 'clamp(0.75rem, 2vw, 0.875rem)' }}>
                                                                {emp.emp_code}
                                                            </div>
                                                        </div>
                                                    ))
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                            <div style={{ marginBottom: '20px' }}>
                                <label style={{
                                    display: 'block',
                                    marginBottom: '8px',
                                    fontWeight: 600,
                                    color: '#374151',
                                    fontSize: 'clamp(0.875rem, 2vw, 1rem)'
                                }}>
                                    Type *
                                </label>
                                <div style={{ display: 'flex', gap: '12px' }}>
                                    <label style={{
                                        flex: 1,
                                        padding: '16px',
                                        border: formData.loan_type === 'loan' ? '2px solid #667eea' : '2px solid #e2e8f0',
                                        borderRadius: '12px',
                                        cursor: 'pointer',
                                        textAlign: 'center',
                                        background: formData.loan_type === 'loan' ? '#f0f4ff' : 'white',
                                        transition: 'all 0.2s'
                                    }}>
                                        <input
                                            type="radio"
                                            name="loan_type"
                                            value="loan"
                                            checked={formData.loan_type === 'loan'}
                                            onChange={(e) => setFormData({ ...formData, loan_type: e.target.value })}
                                            style={{ display: 'none' }}
                                        />
                                        <Wallet size={24} style={{ marginBottom: '8px', color: formData.loan_type === 'loan' ? '#667eea' : '#94a3b8' }} />
                                        <div style={{ fontWeight: 600, color: formData.loan_type === 'loan' ? '#667eea' : '#64748b' }}>Loan</div>
                                    </label>
                                    <label style={{
                                        flex: 1,
                                        padding: '16px',
                                        border: formData.loan_type === 'advance' ? '2px solid #667eea' : '2px solid #e2e8f0',
                                        borderRadius: '12px',
                                        cursor: 'pointer',
                                        textAlign: 'center',
                                        background: formData.loan_type === 'advance' ? '#f0f4ff' : 'white',
                                        transition: 'all 0.2s'
                                    }}>
                                        <input
                                            type="radio"
                                            name="loan_type"
                                            value="advance"
                                            checked={formData.loan_type === 'advance'}
                                            onChange={(e) => setFormData({ ...formData, loan_type: e.target.value })}
                                            style={{ display: 'none' }}
                                        />
                                        <CreditCard size={24} style={{ marginBottom: '8px', color: formData.loan_type === 'advance' ? '#667eea' : '#94a3b8' }} />
                                        <div style={{ fontWeight: 600, color: formData.loan_type === 'advance' ? '#667eea' : '#64748b' }}>Advance</div>
                                    </label>
                                </div>
                            </div>
                            <div style={{ display: 'flex', gap: '16px', marginBottom: '20px', flexWrap: 'wrap' }}>
                                <div style={{ flex: '1', minWidth: '200px' }}>
                                    <label style={{
                                        display: 'block',
                                        marginBottom: '8px',
                                        fontWeight: 600,
                                        color: '#374151',
                                        fontSize: 'clamp(0.875rem, 2vw, 1rem)'
                                    }}>
                                        Loan Amount *
                                    </label>
                                    <input
                                        type="number"
                                        value={formData.loan_amount}
                                        onChange={(e) => setFormData({ ...formData, loan_amount: parseFloat(e.target.value) })}
                                        min="0"
                                        step="0.01"
                                        required
                                        style={{
                                            width: '100%',
                                            padding: '12px 16px',
                                            border: '1px solid #e2e8f0',
                                            borderRadius: '10px',
                                            fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                                            boxSizing: 'border-box'
                                        }}
                                    />
                                </div>
                                <div style={{ flex: '1', minWidth: '200px' }}>
                                    <label style={{
                                        display: 'block',
                                        marginBottom: '8px',
                                        fontWeight: 600,
                                        color: '#374151',
                                        fontSize: 'clamp(0.875rem, 2vw, 1rem)'
                                    }}>
                                        Number of EMIs *
                                    </label>
                                    <input
                                        type="number"
                                        value={formData.total_emis}
                                        onChange={(e) => setFormData({ ...formData, total_emis: parseInt(e.target.value) })}
                                        min="1"
                                        required
                                        style={{
                                            width: '100%',
                                            padding: '12px 16px',
                                            border: '1px solid #e2e8f0',
                                            borderRadius: '10px',
                                            fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                                            boxSizing: 'border-box'
                                        }}
                                    />
                                </div>
                            </div>
                            <div style={{ display: 'flex', gap: '16px', marginBottom: '20px', flexWrap: 'wrap' }}>
                                <div style={{ flex: '1', minWidth: '200px' }}>
                                    <label style={{
                                        display: 'block',
                                        marginBottom: '8px',
                                        fontWeight: 600,
                                        color: '#374151',
                                        fontSize: 'clamp(0.875rem, 2vw, 1rem)'
                                    }}>
                                        EMI Amount *
                                    </label>
                                    <input
                                        type="number"
                                        value={formData.emi_amount}
                                        onChange={(e) => setFormData({ ...formData, emi_amount: parseFloat(e.target.value) })}
                                        min="0"
                                        step="0.01"
                                        required
                                        style={{
                                            width: '100%',
                                            padding: '12px 16px',
                                            border: '1px solid #e2e8f0',
                                            borderRadius: '10px',
                                            fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                                            boxSizing: 'border-box'
                                        }}
                                    />
                                    <button
                                        type="button"
                                        onClick={calculateEMI}
                                        style={{
                                            marginTop: '8px',
                                            background: 'none',
                                            border: 'none',
                                            color: '#667eea',
                                            fontSize: 'clamp(0.75rem, 2vw, 0.875rem)',
                                            cursor: 'pointer',
                                            fontWeight: 500
                                        }}
                                    >
                                        Calculate automatically →
                                    </button>
                                </div>
                                <div style={{ flex: '1', minWidth: '200px' }}>
                                    <label style={{
                                        display: 'block',
                                        marginBottom: '8px',
                                        fontWeight: 600,
                                        color: '#374151',
                                        fontSize: 'clamp(0.875rem, 2vw, 1rem)'
                                    }}>
                                        Start Date *
                                    </label>
                                    <input
                                        type="date"
                                        value={formData.start_date}
                                        onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                                        required
                                        style={{
                                            width: '100%',
                                            padding: '12px 16px',
                                            border: '1px solid #e2e8f0',
                                            borderRadius: '10px',
                                            fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                                            boxSizing: 'border-box'
                                        }}
                                    />
                                </div>
                            </div>
                            <div style={{ marginBottom: '24px' }}>
                                <label style={{
                                    display: 'block',
                                    marginBottom: '8px',
                                    fontWeight: 600,
                                    color: '#374151',
                                    fontSize: 'clamp(0.875rem, 2vw, 1rem)'
                                }}>
                                    Reason
                                </label>
                                <textarea
                                    value={formData.reason}
                                    onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                                    rows={3}
                                    placeholder="Enter reason for loan/advance..."
                                    style={{
                                        width: '100%',
                                        padding: '12px 16px',
                                        border: '1px solid #e2e8f0',
                                        borderRadius: '10px',
                                        fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                                        boxSizing: 'border-box',
                                        resize: 'vertical'
                                    }}
                                />
                            </div>
                            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    style={{
                                        background: '#f1f5f9',
                                        border: 'none',
                                        padding: '12px 24px',
                                        borderRadius: '10px',
                                        cursor: 'pointer',
                                        fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                                        color: '#475569',
                                        fontWeight: 600
                                    }}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    style={{
                                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                        border: 'none',
                                        padding: '12px 24px',
                                        borderRadius: '10px',
                                        cursor: 'pointer',
                                        fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                                        color: 'white',
                                        fontWeight: 600,
                                        boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)'
                                    }}
                                >
                                    Create Loan
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Outstanding Report Modal */}
            {showReportModal && outstandingReport && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0,0,0,0.5)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000,
                    padding: '20px'
                }} onClick={() => setShowReportModal(false)}>
                    <div style={{
                        background: 'white',
                        borderRadius: '20px',
                        width: '100%',
                        maxWidth: '900px',
                        maxHeight: '90vh',
                        overflow: 'auto',
                        boxShadow: '0 20px 50px rgba(0,0,0,0.2)'
                    }} onClick={(e) => e.stopPropagation()}>
                        <div style={{
                            padding: '24px',
                            borderBottom: '1px solid #e2e8f0',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center'
                        }}>
                            <h2 style={{
                                margin: 0,
                                fontSize: 'clamp(1.25rem, 3vw, 1.5rem)',
                                fontWeight: 700,
                                color: '#1e293b'
                            }}>
                                📊 Outstanding Loan Report
                            </h2>
                            <button
                                onClick={() => setShowReportModal(false)}
                                style={{
                                    background: '#f1f5f9',
                                    border: 'none',
                                    padding: '10px',
                                    borderRadius: '10px',
                                    cursor: 'pointer',
                                    display: 'flex'
                                }}
                            >
                                <X size={20} color="#64748b" />
                            </button>
                        </div>

                        {/* Summary Cards */}
                        <div style={{
                            display: 'flex',
                            gap: '16px',
                            padding: '24px',
                            flexWrap: 'wrap'
                        }}>
                            <div style={{
                                flex: '1',
                                minWidth: '200px',
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                padding: '24px',
                                borderRadius: '16px',
                                color: 'white'
                            }}>
                                <div style={{
                                    fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                                    opacity: 0.9,
                                    marginBottom: '8px'
                                }}>
                                    Total Employees
                                </div>
                                <div style={{
                                    fontSize: 'clamp(1.5rem, 4vw, 2.5rem)',
                                    fontWeight: 700
                                }}>
                                    {outstandingReport.total_employees}
                                </div>
                            </div>
                            <div style={{
                                flex: '1',
                                minWidth: '200px',
                                background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                                padding: '24px',
                                borderRadius: '16px',
                                color: 'white'
                            }}>
                                <div style={{
                                    fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                                    opacity: 0.9,
                                    marginBottom: '8px'
                                }}>
                                    Total Outstanding
                                </div>
                                <div style={{
                                    fontSize: 'clamp(1.5rem, 4vw, 2.5rem)',
                                    fontWeight: 700
                                }}>
                                    ₹{outstandingReport.total_outstanding_amount.toLocaleString()}
                                </div>
                            </div>
                        </div>

                        {/* Report Table */}
                        <div style={{ padding: '0 24px 24px', overflowX: 'auto' }}>
                            <table style={{
                                width: '100%',
                                borderCollapse: 'collapse',
                                minWidth: '700px'
                            }}>
                                <thead>
                                    <tr style={{
                                        background: '#f8fafc',
                                        borderBottom: '1px solid #e2e8f0'
                                    }}>
                                        <th style={{
                                            padding: '14px',
                                            textAlign: 'left',
                                            fontWeight: 600,
                                            color: '#475569',
                                            fontSize: 'clamp(0.75rem, 2vw, 0.875rem)'
                                        }}>Employee</th>
                                        <th style={{
                                            padding: '14px',
                                            textAlign: 'left',
                                            fontWeight: 600,
                                            color: '#475569',
                                            fontSize: 'clamp(0.75rem, 2vw, 0.875rem)'
                                        }}>Type</th>
                                        <th style={{
                                            padding: '14px',
                                            textAlign: 'right',
                                            fontWeight: 600,
                                            color: '#475569',
                                            fontSize: 'clamp(0.75rem, 2vw, 0.875rem)'
                                        }}>Original</th>
                                        <th style={{
                                            padding: '14px',
                                            textAlign: 'right',
                                            fontWeight: 600,
                                            color: '#475569',
                                            fontSize: 'clamp(0.75rem, 2vw, 0.875rem)'
                                        }}>EMI</th>
                                        <th style={{
                                            padding: '14px',
                                            textAlign: 'center',
                                            fontWeight: 600,
                                            color: '#475569',
                                            fontSize: 'clamp(0.75rem, 2vw, 0.875rem)'
                                        }}>Remaining</th>
                                        <th style={{
                                            padding: '14px',
                                            textAlign: 'right',
                                            fontWeight: 600,
                                            color: '#475569',
                                            fontSize: 'clamp(0.75rem, 2vw, 0.875rem)'
                                        }}>Outstanding</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {outstandingReport.loans.map((loan, index) => (
                                        <tr key={loan.loan_id} style={{
                                            borderBottom: '1px solid #f1f5f9',
                                            background: index % 2 === 0 ? 'white' : '#fafafa'
                                        }}>
                                            <td style={{ padding: '14px' }}>
                                                <div style={{ fontWeight: 600, color: '#1e293b' }}>
                                                    {loan.employee_name}
                                                </div>
                                                <div style={{ color: '#64748b', fontSize: 'clamp(0.75rem, 2vw, 0.875rem)' }}>
                                                    {loan.emp_code} • {loan.department}
                                                </div>
                                            </td>
                                            <td style={{ padding: '14px' }}>
                                                <span style={{
                                                    padding: '4px 10px',
                                                    borderRadius: '12px',
                                                    fontSize: 'clamp(0.75rem, 2vw, 0.875rem)',
                                                    background: loan.loan_type === 'loan' ? '#f0f4ff' : '#fdf4f4',
                                                    color: loan.loan_type === 'loan' ? '#0369a1' : '#be123c'
                                                }}>
                                                    {loan.loan_type}
                                                </span>
                                            </td>
                                            <td style={{
                                                padding: '14px',
                                                textAlign: 'right',
                                                fontWeight: 500,
                                                color: '#475569'
                                            }}>
                                                ₹{loan.original_amount.toLocaleString()}
                                            </td>
                                            <td style={{
                                                padding: '14px',
                                                textAlign: 'right',
                                                color: '#475569'
                                            }}>
                                                ₹{loan.emi_amount.toLocaleString()}
                                            </td>
                                            <td style={{
                                                padding: '14px',
                                                textAlign: 'center',
                                                fontWeight: 600,
                                                color: '#f59e0b'
                                            }}>
                                                {loan.remaining_emis}
                                            </td>
                                            <td style={{
                                                padding: '14px',
                                                textAlign: 'right',
                                                fontWeight: 700,
                                                color: '#dc2626',
                                                fontSize: 'clamp(0.875rem, 2vw, 1rem)'
                                            }}>
                                                ₹{loan.outstanding_amount.toLocaleString()}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div style={{
                            padding: '24px',
                            borderTop: '1px solid #e2e8f0',
                            display: 'flex',
                            justifyContent: 'flex-end'
                        }}>
                            <button
                                onClick={() => setShowReportModal(false)}
                                style={{
                                    background: '#f1f5f9',
                                    border: 'none',
                                    padding: '12px 24px',
                                    borderRadius: '10px',
                                    cursor: 'pointer',
                                    fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                                    color: '#475569',
                                    fontWeight: 600
                                }}
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
