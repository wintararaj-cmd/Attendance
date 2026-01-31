import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import DashboardHome from './pages/DashboardHome';
import RegisterEmployee from './pages/RegisterEmployee';
import EmployeeList from './pages/EmployeeList';
import PayrollManagement from './pages/PayrollManagement';
import AttendanceLogs from './pages/AttendanceLogs';
import DepartmentManagement from './pages/DepartmentManagement';
import Login from './pages/Login';
import axios from 'axios';


// Configure Axios base URL for production
// Configure Axios base URL for production
const apiUrl = import.meta.env.VITE_API_BASE_URL || 'https://api.t3sol.in';
console.log("Configured API URL:", apiUrl);

if (apiUrl) {
  axios.defaults.baseURL = apiUrl;
}

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('admin_token'));

  useEffect(() => {
    if (token) {
      localStorage.setItem('admin_token', token);
      // Set default auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      localStorage.removeItem('admin_token');
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  if (!token) {
    return <Login onLogin={setToken} />;
  }

  return (
    <BrowserRouter>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<DashboardHome />} />
            <Route path="/register" element={<RegisterEmployee />} />
            <Route path="/employees" element={<EmployeeList />} />
            <Route path="/departments" element={<DepartmentManagement />} />
            <Route path="/payroll" element={<PayrollManagement />} />
            <Route path="/logs" element={<AttendanceLogs />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
