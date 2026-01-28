import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import DashboardHome from './pages/DashboardHome';
import RegisterEmployee from './pages/RegisterEmployee';
import EmployeeList from './pages/EmployeeList';
import PayrollManagement from './pages/PayrollManagement';
import AttendanceLogs from './pages/AttendanceLogs';

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<DashboardHome />} />
            <Route path="/register" element={<RegisterEmployee />} />
            <Route path="/employees" element={<EmployeeList />} />
            <Route path="/payroll" element={<PayrollManagement />} />
            <Route path="/logs" element={<AttendanceLogs />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
