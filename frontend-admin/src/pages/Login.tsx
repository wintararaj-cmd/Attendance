import { useState } from 'react';
import axios from 'axios';
import { Lock, User, Fingerprint, Eye, EyeOff } from 'lucide-react';

export default function Login({ onLogin }: { onLogin: (token: string) => void }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!username || !password) {
            setError('Please enter your credentials');
            return;
        }
        try {
            setLoading(true);
            setError('');
            const params = new URLSearchParams();
            params.append('username', username);
            params.append('password', password);
            const res = await axios.post('/api/v1/auth/login', params, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            });
            if (res.data.access_token) {
                onLogin(res.data.access_token);
            }
        } catch {
            setError('Invalid username or password. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #0f172a 0%, #1a1f35 40%, #0f172a 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1rem',
            position: 'relative',
            overflow: 'hidden',
        }}>
            {/* Background Glows */}
            <div style={{
                position: 'absolute', top: '-100px', left: '-100px',
                width: '400px', height: '400px',
                background: 'radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%)',
                borderRadius: '50%', pointerEvents: 'none',
            }} />
            <div style={{
                position: 'absolute', bottom: '-100px', right: '-100px',
                width: '400px', height: '400px',
                background: 'radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 70%)',
                borderRadius: '50%', pointerEvents: 'none',
            }} />

            {/* Login Card */}
            <div style={{
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(20px)',
                borderRadius: '20px',
                padding: '2.5rem',
                width: '100%',
                maxWidth: '400px',
                position: 'relative',
                boxShadow: '0 25px 50px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.05)',
                animation: 'slideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
            }}>
                {/* Brand */}
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <div style={{
                        width: '56px', height: '56px',
                        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                        borderRadius: '16px',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        margin: '0 auto 1rem',
                        boxShadow: '0 8px 24px rgba(99, 102, 241, 0.4)',
                    }}>
                        <Fingerprint size={28} color="white" />
                    </div>
                    <h1 style={{
                        fontSize: '1.5rem', fontWeight: 800, color: '#f1f5f9',
                        letterSpacing: '-0.5px', margin: 0,
                    }}>
                        AttendSys
                    </h1>
                    <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                        HR Admin Panel — Sign in to continue
                    </p>
                </div>

                {/* Error */}
                {error && (
                    <div style={{
                        background: 'rgba(239, 68, 68, 0.15)',
                        border: '1px solid rgba(239, 68, 68, 0.3)',
                        color: '#fca5a5',
                        padding: '0.75rem 1rem',
                        borderRadius: '10px',
                        fontSize: '0.875rem',
                        marginBottom: '1.25rem',
                        textAlign: 'center',
                    }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    {/* Username */}
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{
                            display: 'block', color: '#94a3b8', fontSize: '0.8125rem',
                            fontWeight: 600, marginBottom: '0.375rem',
                        }}>
                            Username
                        </label>
                        <div style={{ position: 'relative' }}>
                            <User size={16} style={{
                                position: 'absolute', left: '0.875rem', top: '50%',
                                transform: 'translateY(-50%)', color: '#475569',
                            }} />
                            <input
                                type="text"
                                placeholder="Enter username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                autoComplete="username"
                                style={{
                                    width: '100%',
                                    padding: '0.75rem 0.875rem 0.75rem 2.5rem',
                                    background: 'rgba(0, 0, 0, 0.3)',
                                    border: '1.5px solid rgba(255, 255, 255, 0.1)',
                                    borderRadius: '10px',
                                    color: '#f1f5f9',
                                    fontSize: '0.9375rem',
                                    outline: 'none',
                                    transition: 'all 0.2s',
                                    fontFamily: 'inherit',
                                }}
                                onFocus={(e) => { e.currentTarget.style.borderColor = '#6366f1'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.2)'; }}
                                onBlur={(e) => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'; e.currentTarget.style.boxShadow = 'none'; }}
                            />
                        </div>
                    </div>

                    {/* Password */}
                    <div style={{ marginBottom: '1.75rem' }}>
                        <label style={{
                            display: 'block', color: '#94a3b8', fontSize: '0.8125rem',
                            fontWeight: 600, marginBottom: '0.375rem',
                        }}>
                            Password
                        </label>
                        <div style={{ position: 'relative' }}>
                            <Lock size={16} style={{
                                position: 'absolute', left: '0.875rem', top: '50%',
                                transform: 'translateY(-50%)', color: '#475569',
                            }} />
                            <input
                                type={showPassword ? 'text' : 'password'}
                                placeholder="Enter password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                autoComplete="current-password"
                                style={{
                                    width: '100%',
                                    padding: '0.75rem 3rem 0.75rem 2.5rem',
                                    background: 'rgba(0, 0, 0, 0.3)',
                                    border: '1.5px solid rgba(255, 255, 255, 0.1)',
                                    borderRadius: '10px',
                                    color: '#f1f5f9',
                                    fontSize: '0.9375rem',
                                    outline: 'none',
                                    transition: 'all 0.2s',
                                    fontFamily: 'inherit',
                                }}
                                onFocus={(e) => { e.currentTarget.style.borderColor = '#6366f1'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.2)'; }}
                                onBlur={(e) => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'; e.currentTarget.style.boxShadow = 'none'; }}
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(v => !v)}
                                style={{
                                    position: 'absolute', right: '0.75rem', top: '50%',
                                    transform: 'translateY(-50%)',
                                    background: 'none', border: 'none', cursor: 'pointer',
                                    color: '#475569', padding: '0.25rem',
                                    display: 'flex', alignItems: 'center',
                                }}
                            >
                                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                            </button>
                        </div>
                    </div>

                    {/* Submit */}
                    <button
                        type="submit"
                        disabled={loading}
                        style={{
                            width: '100%',
                            padding: '0.875rem',
                            borderRadius: '10px',
                            border: 'none',
                            background: loading
                                ? 'rgba(99, 102, 241, 0.5)'
                                : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                            color: 'white',
                            fontSize: '0.9375rem',
                            fontWeight: 700,
                            cursor: loading ? 'not-allowed' : 'pointer',
                            fontFamily: 'inherit',
                            transition: 'all 0.2s',
                            boxShadow: loading ? 'none' : '0 8px 20px rgba(99, 102, 241, 0.35)',
                            letterSpacing: '0.01em',
                        }}
                    >
                        {loading ? (
                            <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                                <span style={{
                                    width: '16px', height: '16px', border: '2px solid rgba(255,255,255,0.3)',
                                    borderTopColor: 'white', borderRadius: '50%',
                                    animation: 'spin 0.7s linear infinite', display: 'inline-block',
                                }} />
                                Signing in…
                            </span>
                        ) : 'Sign In'}
                    </button>
                </form>

                <div style={{ textAlign: 'center', marginTop: '1.5rem', color: '#475569', fontSize: '0.75rem' }}>
                    Secured system — Authorized personnel only
                </div>
            </div>

            <style>{`
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(24px) scale(0.97); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        input::placeholder { color: #334155 !important; }
      `}</style>
        </div>
    );
}
