import React, { useState, useEffect } from 'react';
import { reportsAPI } from '../services/api';
import useAuthStore from '../stores/authStore';
import {
  BarChart3,
  PieChart,
  TrendingUp,
  Calendar,
  Download,
  Users,
} from 'lucide-react';

const Reports = () => {
  const { isAdmin, isManager } = useAuthStore();
  const [reportData, setReportData] = useState([]);
  const [areaData, setAreaData] = useState([]);
  const [teamEntries, setTeamEntries] = useState([]); // Initialized as empty array to prevent .map crashes
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('summary');
  const [dateRange, setDateRange] = useState({
    start_date: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    fetchReports();
  }, [dateRange]);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const requests = [
        reportsAPI.getSummary(dateRange),
        reportsAPI.getByReportingArea(dateRange),
      ];

      // Allow Managers and Admins to see team data
      const canSeeTeamData = isAdmin() || isManager();
      if (canSeeTeamData) {
        requests.push(reportsAPI.getDaily(dateRange));
      }

      const results = await Promise.all(requests);
      setReportData(results[0]?.data?.data || null);
      setAreaData(results[1]?.data?.data || null);

      if (canSeeTeamData && results[2]) {
        let allEntries = [];
        const dailySummary = results[2]?.data?.data?.daily_summary || [];
        dailySummary.forEach(day => {
          if (day.entries) {
            const entriesWithDate = day.entries.map(e => ({ ...e, work_date: day.date }));
            allEntries = [...allEntries, ...entriesWithDate];
          }
        });
        setTeamEntries(allEntries);
      }
    } catch (error) {
      console.error('Error fetching reports:', error);
      setTeamEntries([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (field, value) => {
    setDateRange({ ...dateRange, [field]: value });
  };

  const exportToCSV = () => {
    if (!reportData) return;
    let csv = 'Project,Client,Reporting Area,Total Hours\n';
    reportData.project_summary.forEach(project => {
      csv += `"${project.project_name}","${project.client}","${project.reporting_area || 'N/A'}",${project.total_hours}\n`;
    });
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `time-report-${dateRange.start_date}-to-${dateRange.end_date}.csv`;
    a.click();
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
          <h2>Reports</h2>
          <p>View time tracking analytics and summaries</p>
        </div>
        <div className="header-actions">
          <div className="flex gap-2">
            <input
              type="date"
              className="form-input"
              style={{ width: 'auto' }}
              value={dateRange.start_date}
              onChange={(e) => handleDateChange('start_date', e.target.value)}
            />
            <span className="text-secondary" style={{ alignSelf: 'center' }}>to</span>
            <input
              type="date"
              className="form-input"
              style={{ width: 'auto' }}
              value={dateRange.end_date}
              onChange={(e) => handleDateChange('end_date', e.target.value)}
            />
          </div>
          <button className="btn btn-secondary" onClick={exportToCSV}>
            <Download size={18} />
            Export CSV
          </button>
        </div>
      </header>

      {(isManager() || isAdmin()) && (
        <div style={{ borderBottom: '1px solid var(--border)', marginBottom: '24px' }}>
          <div className="page-content" style={{ display: 'flex', gap: '24px', borderBottom: 'none', paddingBottom: '0' }}>
            <button
              onClick={() => setActiveTab('summary')}
              className={activeTab === 'summary' ? 'tab-active' : 'tab-inactive'}
              style={{
                padding: '12px 0', border: 'none', background: 'none', cursor: 'pointer',
                borderBottom: activeTab === 'summary' ? '2px solid var(--primary)' : 'none',
                color: activeTab === 'summary' ? 'var(--primary)' : 'var(--text-secondary)',
                fontWeight: activeTab === 'summary' ? '600' : '500', fontSize: '14px',
              }}
            >
              Analytics
            </button>
            <button
              onClick={() => setActiveTab('team')}
              style={{
                padding: '12px 0', border: 'none', background: 'none', cursor: 'pointer',
                borderBottom: activeTab === 'team' ? '2px solid var(--primary)' : 'none',
                color: activeTab === 'team' ? 'var(--primary)' : 'var(--text-secondary)',
                fontWeight: activeTab === 'team' ? '600' : '500', fontSize: '14px',
              }}
            >
              <Users size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
              Team Time Entries
            </button>
          </div>
        </div>
      )}

      <div className="page-content">
        {activeTab === 'summary' && (
          <>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-value">{reportData?.total_hours?.toFixed(1) || 0}h</div>
                <div className="stat-label">Total Hours</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{reportData?.total_projects || 0}</div>
                <div className="stat-label">Projects Tracked</div>
              </div>
            </div>

            <div className="card">
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Project</th>
                      <th>Client</th>
                      <th>Total Hours</th>
                    </tr>
                  </thead>
                  <tbody>
                    {((reportData?.project_summary || reportData?.data?.project_summary || []) || []).map((project) => (
                      <tr key={project.project_id}>
                        <td>{project.project_name}</td>
                        <td>{project.client}</td>
                        <td>{project.total_hours.toFixed(1)}h</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {activeTab === 'team' && (isAdmin() || isManager()) && (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Team Time Entries</h3>
            </div>
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Employee</th>
                    <th>Project</th>
                    <th>Date</th>
                    <th>Hours</th>
                    <th>Status</th>
                    <th>Approved By</th>
                  </tr>
                </thead>
                <tbody>
                  {teamEntries.length > 0 ? (
                    teamEntries.map((entry) => (
                      <tr key={entry.id}>
                        <td>{entry.user_name}</td>
                        <td>{entry.project_name}</td>
                        <td>{new Date(entry.work_date).toLocaleDateString()}</td>
                        <td>{entry.hours}h</td>
                        <td>
                          <span className={`status-badge status-${entry.status.toLowerCase()}`}>
                            {entry.status}
                          </span>
                        </td>
                        <td>{entry.approved_by_name || '-'}</td>
                      </tr>
                    ))
                  ) : (
                    <tr><td colSpan="6" className="text-center py-4">No entries found.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const Clock = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
  </svg>
);

export default Reports;
