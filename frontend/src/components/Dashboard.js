import React, { useState, useEffect } from 'react';
import useAuthStore from '../stores/authStore';
import { timeEntriesAPI, reportsAPI, projectsAPI } from '../services/api';
import {
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  TrendingUp,
  Calendar,
  Users,
  FolderKanban,
} from 'lucide-react';

const Dashboard = () => {
  const { user, isAdmin, isManager } = useAuthStore();
  const [stats, setStats] = useState({
    totalHours: 0,
    pendingEntries: 0,
    approvedEntries: 0,
    rejectedEntries: 0,
    totalProjects: 0,
    totalUsers: 0,
  });
  const [recentEntries, setRecentEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const today = new Date();
      const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);

      // Fetch time entries
      const entriesResponse = await timeEntriesAPI.list({
        start_date: startOfMonth.toISOString().split('T')[0],
        end_date: today.toISOString().split('T')[0],
      });

      const entries = entriesResponse.data.data.entries || [];
      
      // Calculate stats
      const totalHours = entries.reduce((sum, e) => sum + parseFloat(e.hours || 0), 0);
      const pendingEntries = entries.filter((e) => e.status === 'PENDING').length;
      const approvedEntries = entries.filter((e) => e.status === 'APPROVED').length;
      const rejectedEntries = entries.filter((e) => e.status === 'REJECTED').length;

      // Fetch projects
      const projectsResponse = await projectsAPI.list();
      const totalProjects = projectsResponse.data.data.total || 0;

      setStats({
        totalHours,
        pendingEntries,
        approvedEntries,
        rejectedEntries,
        totalProjects,
        totalUsers: 0,
      });

      setRecentEntries(entries.slice(0, 5));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const getStatusBadge = (status) => {
    return `badge badge-${status.toLowerCase()}`;
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <header className="header">
        <div className="header-title">
          <h2>{getGreeting()}, {user?.name}!</h2>
          <p>Here's what's happening with your time tracking</p>
        </div>
      </header>

      <div className="page-content">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-card-header">
              <div className="stat-icon teal">
                <Clock size={24} />
              </div>
            </div>
            <div className="stat-value">{stats.totalHours.toFixed(1)}h</div>
            <div className="stat-label">Total Hours This Month</div>
          </div>

          <div className="stat-card">
            <div className="stat-card-header">
              <div className="stat-icon orange">
                <AlertCircle size={24} />
              </div>
            </div>
            <div className="stat-value">{stats.pendingEntries}</div>
            <div className="stat-label">Pending Approvals</div>
          </div>

          <div className="stat-card">
            <div className="stat-card-header">
              <div className="stat-icon green">
                <CheckCircle size={24} />
              </div>
            </div>
            <div className="stat-value">{stats.approvedEntries}</div>
            <div className="stat-label">Approved Entries</div>
          </div>

          <div className="stat-card">
            <div className="stat-card-header">
              <div className="stat-icon blue">
                <FolderKanban size={24} />
              </div>
            </div>
            <div className="stat-value">{stats.totalProjects}</div>
            <div className="stat-label">Active Projects</div>
          </div>
        </div>

        <div className="card" style={{ marginBottom: '24px' }}>
          <div className="card-header">
            <h3 className="card-title">Recent Time Entries</h3>
          </div>
          <div className="table-container">
            {recentEntries.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">
                  <Calendar size={48} />
                </div>
                <div className="empty-state-title">No time entries yet</div>
                <div className="empty-state-text">Start tracking your time by adding entries in the Timesheets section.</div>
              </div>
            ) : (
              <table className="table">
                <thead>
                  <tr>
                    <th>Project</th>
                    <th>Date</th>
                    <th>Hours</th>
                    <th>Status</th>
                    <th>Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {recentEntries.map((entry) => (
                    <tr key={entry.id}>
                      <td>{entry.project_name}</td>
                      <td>{entry.work_date}</td>
                      <td>{entry.hours}h</td>
                      <td>
                        <span className={getStatusBadge(entry.status)}>
                          {entry.status}
                        </span>
                      </td>
                      <td>{entry.notes || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {(isAdmin() || isManager()) && (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Quick Actions</h3>
            </div>
            <div className="card-body">
              <div className="flex gap-4">
                <button className="btn btn-primary" onClick={() => window.location.href = '/users'}>
                  <Users size={18} />
                  Manage Users
                </button>
                <button className="btn btn-secondary" onClick={() => window.location.href = '/projects'}>
                  <FolderKanban size={18} />
                  Manage Projects
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
