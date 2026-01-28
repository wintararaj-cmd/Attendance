import { LayoutDashboard, Users, UserPlus, Banknote, FileText } from 'lucide-react';
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
    </aside>
  );
}
