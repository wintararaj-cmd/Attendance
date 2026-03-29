import { LayoutDashboard, Users, UserPlus, Banknote, FileText, Building2, LogOut, Fingerprint, Wallet } from 'lucide-react';
import { NavLink, useLocation } from 'react-router-dom';

const NAV_ITEMS: Array<{ section: string; items: Array<{ to: string; icon: any; label: string; exact?: boolean }> }> = [
  {
    section: 'Overview',
    items: [
      { to: '/', icon: LayoutDashboard, label: 'Dashboard', exact: true },
    ]
  },
  {
    section: 'Management',
    items: [
      { to: '/employees', icon: Users, label: 'Employees' },
      { to: '/departments', icon: Building2, label: 'Departments' },
      { to: '/register', icon: UserPlus, label: 'Register Face' },
    ]
  },
  {
    section: 'Reports',
    items: [
      { to: '/payroll', icon: Banknote, label: 'Payroll' },
      { to: '/loans', icon: Wallet, label: 'Loans' },
      { to: '/biometric-import', icon: Fingerprint, label: 'Attendance taken from Biometric Device' },
      { to: '/logs', icon: FileText, label: 'Attendance Logs' },
    ]
  }
];

export default function Sidebar() {
  const location = useLocation();

  const handleLogout = () => {
    if (confirm('Are you sure you want to logout?')) {
      localStorage.removeItem('admin_token');
      sessionStorage.removeItem('admin_token');
      window.location.href = '/';
    }
  };

  return (
    <aside className="sidebar">
      {/* Logo / Brand */}
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">
            <Fingerprint size={20} color="white" />
          </div>
          <div>
            <div className="sidebar-logo-text">AttendSys</div>
            <div className="sidebar-logo-sub">HR Admin Panel</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {NAV_ITEMS.map(({ section, items }) => (
          <div key={section}>
            <div className="sidebar-section-title">{section}</div>
            {items.map(({ to, icon: Icon, label, exact }) => {
              const isActive = exact
                ? location.pathname === to
                : location.pathname.startsWith(to);

              return (
                <NavLink
                  key={to}
                  to={to}
                  className={`nav-item ${isActive ? 'active' : ''}`}
                  end={exact}
                >
                  <Icon size={17} />
                  {label}
                </NavLink>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Footer / User Info */}
      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-avatar">A</div>
          <div className="sidebar-user-info">
            <div className="sidebar-user-name">Administrator</div>
            <div className="sidebar-user-role">Super Admin</div>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="nav-item"
          style={{ color: '#f87171', width: '100%', border: 'none' }}
        >
          <LogOut size={17} />
          Logout
        </button>
      </div>
    </aside>
  );
}
