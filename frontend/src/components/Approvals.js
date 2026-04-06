import React, { useState, useEffect } from 'react';
import { timeEntriesAPI } from '../services/api';
import { Check, X, Eye, Filter } from 'lucide-react';

const Approvals = () => {
  const [pendingEntries, setPendingEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [filter, setFilter] = useState('PENDING');

  useEffect(() => { fetchPendingApprovals(); }, [filter]);

  const fetchPendingApprovals = async () => {
    setLoading(true);
    try {
      const response = await timeEntriesAPI.getPendingApprovals({ status: filter });
      setPendingEntries(response.data.data || []);
    } catch (error) {
      console.error('Error fetching pending approvals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (entryId) => {
    try {
      await timeEntriesAPI.approve(entryId, { status: 'APPROVED' });
      fetchPendingApprovals();
    } catch (error) {
      console.error('Error approving entry:', error);
      alert('Failed to approve entry');
    }
  };

  const handleReject = async () => {
    if (!rejectionReason.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }
    try {
      await timeEntriesAPI.approve(selectedEntry.id, {
        status: 'REJECTED',
        rejection_reason: rejectionReason,
      });
      setShowRejectModal(false);
      setSelectedEntry(null);
      setRejectionReason('');
      fetchPendingApprovals();
    } catch (error) {
      console.error('Error rejecting entry:', error);
      alert('Failed to reject entry');
    }
  };

  const getStatusBadge = (status) => `badge badge-${status.toLowerCase()}`;

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
          <h2>Approvals</h2>
          <p>Review and approve time entries</p>
        </div>
        <div className="header-actions">
          <select
            className="form-select"
            style={{ width: 'auto' }}
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="PENDING">Pending</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
            <option value="ALL">All</option>
          </select>
        </div>
      </header>

      <div className="page-content">
        {pendingEntries.length === 0 ? (
          <div className="card">
            <div className="empty-state">
              <div className="empty-state-icon">
                <Check size={48} />
              </div>
              <div className="empty-state-title">All caught up!</div>
              <div className="empty-state-text">No pending approvals at this time.</div>
            </div>
          </div>
        ) : (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Pending Approvals ({pendingEntries.length})</h3>
            </div>
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Employee</th>
                    <th>Project</th>
                    <th>Date</th>
                    <th>Hours</th>
                    <th>Notes</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {pendingEntries.map((entry) => (
                    <tr key={entry.id}>
                      <td>
                        <div className="flex items-center gap-2">
                          <div className="avatar avatar-sm">
                            {entry.user_name.split(' ').map(n => n[0]).join('')}
                          </div>
                          <span>{entry.user_name}</span>
                        </div>
                      </td>
                      <td>{entry.project_name}</td>
                      <td>{entry.work_date}</td>
                      <td>{entry.hours}h</td>
                      <td>{entry.notes || '-'}</td>
                      <td>
                        <div className="flex gap-2">
                          <button
                            className="btn btn-sm btn-success"
                            onClick={() => handleApprove(entry.id)}
                            title="Approve"
                          >
                            <Check size={16} />
                          </button>
                          <button
                            className="btn btn-sm btn-danger"
                            onClick={() => { setSelectedEntry(entry); setShowRejectModal(true); }}
                            title="Reject"
                          >
                            <X size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="stats-grid" style={{ marginTop: '24px' }}>
          <div className="stat-card">
            <div className="stat-card-header">
              <div className="stat-icon orange">
                <Eye size={24} />
              </div>
            </div>
            <div className="stat-value">{pendingEntries.length}</div>
            <div className="stat-label">Pending Approvals</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-header">
              <div className="stat-icon teal">
                <Filter size={24} />
              </div>
            </div>
            <div className="stat-value">
              {pendingEntries.reduce((sum, e) => sum + parseFloat(e.hours || 0), 0).toFixed(1)}h
            </div>
            <div className="stat-label">Total Hours Pending</div>
          </div>
        </div>
      </div>

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="modal-overlay" onClick={() => setShowRejectModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Reject Time Entry</h3>
              <button className="btn btn-icon" onClick={() => setShowRejectModal(false)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">Employee</label>
                <input type="text" className="form-input" value={selectedEntry?.user_name} disabled />
              </div>
              <div className="form-group">
                <label className="form-label">Project</label>
                <input type="text" className="form-input" value={selectedEntry?.project_name} disabled />
              </div>
              <div className="form-group">
                <label className="form-label">Hours</label>
                <input type="text" className="form-input" value={`${selectedEntry?.hours}h`} disabled />
              </div>
              <div className="form-group">
                <label className="form-label">Reason for Rejection</label>
                <textarea
                  className="form-input"
                  placeholder="Please provide a reason for rejecting this time entry..."
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  rows={4}
                  required
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowRejectModal(false)}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={handleReject}>
                Reject Entry
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Approvals;









