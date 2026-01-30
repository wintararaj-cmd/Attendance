import { LayoutDashboard, Users, UserPlus, Banknote, FileText, Building2, LogOut } from 'lucide-react';
import { NavLink } from 'react-router-dom';

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <LayoutDashboard size={28} />
        <span>HR Admin</span>
      </div>

      <nav>
        <NavLink
          to="/"
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <LayoutDashboard size={20} />
          Dashboard
        </NavLink>

        <NavLink
          to="/employees"
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <Users size={20} />
          Employees
        </NavLink>

        <NavLink
          to="/departments"
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <Building2 size={20} />
          Departments
        </NavLink>

        <NavLink
          to="/register"
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <UserPlus size={20} />
          Register Face
        </NavLink>

        <NavLink
          to="/payroll"
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <Banknote size={20} />
          Payroll
        </NavLink>

        <NavLink
          to="/logs"
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <FileText size={20} />
          Attendance Logs
        </NavLink>
      </nav>

      <div style={{ marginTop: 'auto', padding: '1rem' }}>
        <button
          onClick={() => {
            if (confirm('Are you sure you want to logout?')) {
              localStorage.removeItem('admin_token');
              window.location.href = '/';
            }
          }}
          className="nav-item"
          style={{
            width: '100%',
            background: 'none',
            border: 'none',
            color: '#ef4444',
            cursor: 'pointer',
            marginTop: 'auto'
          }}
        >
          <LogOut size={20} />
          Logout
        </button>
      </div>
    </aside>
  );
}
