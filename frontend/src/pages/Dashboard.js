import React from 'react';
import { useNavigate } from 'react-router-dom';
import { clearAuth, getUser } from '../api';

function Dashboard() {
  const navigate = useNavigate();
  const user = getUser();

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <button onClick={handleLogout} className="btn-secondary">
          Logout
        </button>
      </div>

      <div className="dashboard-content">
        <div className="welcome-box">
          <h2>Welcome, {user?.email}!</h2>
          <p>Role: <strong>{user?.role}</strong></p>
          <p className="placeholder-text">
            This is a protected page. Sweet shop management features will be added here.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
