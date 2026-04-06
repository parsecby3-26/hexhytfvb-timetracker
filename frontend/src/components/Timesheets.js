import React, { useState, useEffect } from 'react';
import { timeEntriesAPI, projectsAPI } from '../services/api';
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  X,
  Clock,
  AlertCircle,
} from 'lucide-react';

const Timesheets = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [entries, setEntries] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedDate, setSelectedDate] = useState(null);
  const [formData, setFormData] = useState({
    project_id: '',
    hours: '',
    notes: '',
  });
  const [viewMode, setViewMode] = useState('calendar'); // calendar or list

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    fetchEntries();
  }, [currentDate]);

  const fetchProjects = async () => {
    try {
      const response = await projectsAPI.list();
      setProjects(response.data.data.projects || []);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth();
      const startDate = new Date(year, month, 1);
      const endDate = new Date(year, month + 1, 0);

      const response = await timeEntriesAPI.list({
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
      });

      setEntries(response.data.data.entries || []);
    } catch (error) {
      console.error('Error fetching entries:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDay = firstDay.getDay();

    const days = [];
    for (let i = 0; i < startingDay; i++) {
      days.push({ date: null, isOtherMonth: true });
    }
    for (let i = 1; i <= daysInMonth; i++) {
      days.push({
        date: new Date(year, month, i),
        isOtherMonth: false,
      });
    }
    return days;
  };

  const getEntriesForDate = (date) => {
    if (!date) return [];
    const dateStr = date.toISOString().split('T')[0];
    return entries.filter((e) => e.work_date === dateStr);
  };

  const getTotalHoursForDate = (date) => {
    const dateEntries = getEntriesForDate(date);
    return dateEntries.reduce((sum, e) => sum + parseFloat(e.hours || 0), 0);
  };

  const handlePrevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const handleDayClick = (date) => {
    if (!date) return;
    setSelectedDate(date);
    setFormData({ project_id: '', hours: '', notes: '' });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await timeEntriesAPI.create({
        project_id: parseInt(formData.project_id),
        work_date: selectedDate.toISOString().split('T')[0],
        hours: parseFloat(formData.hours),
        notes: formData.notes,
      });
      setShowModal(false);
      fetchEntries();
    } catch (error) {
      console.error('Error creating entry:', error);
      alert('Failed to create time entry. You may already have an entry for this project on this date.');
    }
  };

  const getStatusBadge = (status) => `badge badge-${status.toLowerCase()}`;

  const isToday = (date) => {
    if (!date) return false;
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

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
          <h2>Timesheets</h2>
          <p>Track and manage your time entries</p>
        </div>
        <div className="header-actions">
          <div className="flex gap-2">
            <button
              className={`btn btn-sm ${viewMode === 'calendar' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('calendar')}
            >
              Calendar
            </button>
            <button
              className={`btn btn-sm ${viewMode === 'list' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('list')}
            >
              List View
            </button>
          </div>
          <button className="btn btn-primary" onClick={() => { setSelectedDate(new Date()); setShowModal(true); }}>
            <Plus size={18} />
            Add Entry
          </button>
        </div>
      </header>

      <div className="page-content">
        {viewMode === 'calendar' ? (
          <div className="card">
            <div className="calendar-header">
              <h3 className="calendar-title">
                {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
              </h3>
              <div className="calendar-nav">
                <button className="btn btn-icon" onClick={handlePrevMonth}>
                  <ChevronLeft size={20} />
                </button>
                <button className="btn btn-secondary btn-sm" onClick={() => setCurrentDate(new Date())}>
                  Today
                </button>
                <button className="btn btn-icon" onClick={handleNextMonth}>
                  <ChevronRight size={20} />
                </button>
              </div>
            </div>

            <div className="calendar-grid">
              {weekDays.map((day) => (
                <div key={day} className="calendar-day-header">
                  {day}
                </div>
              ))}
              {getDaysInMonth(currentDate).map((day, index) => {
                const dateEntries = getEntriesForDate(day.date);
                const totalHours = getTotalHoursForDate(day.date);
                
                return (
                  <div
                    key={index}
                    className={`calendar-day ${day.isOtherMonth ? 'other-month' : ''} ${isToday(day.date) ? 'today' : ''}`}
                    onClick={() => handleDayClick(day.date)}
                  >
                    {day.date && (
                      <>
                        <div className="calendar-day-number">{day.date.getDate()}</div>
                        {totalHours > 0 && (
                          <div style={{ fontSize: '12px', color: 'var(--primary)', fontWeight: 600 }}>
                            {totalHours.toFixed(1)}h
                          </div>
                        )}
                        {dateEntries.slice(0, 2).map((entry) => (
                          <div key={entry.id} className={`calendar-entry ${entry.status.toLowerCase()}`}>
                            {entry.project_name.slice(0, 10)} - {entry.hours}h
                          </div>
                        ))}
                        {dateEntries.length > 2 && (
                          <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                            +{dateEntries.length - 2} more
                          </div>
                        )}
                      </>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">All Time Entries</h3>
            </div>
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Project</th>
                    <th>Hours</th>
                    <th>Status</th>
                    <th>Notes</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {entries.map((entry) => (
                    <tr key={entry.id}>
                      <td>{entry.work_date}</td>
                      <td>{entry.project_name}</td>
                      <td>{entry.hours}h</td>
                      <td>
                        <span className={getStatusBadge(entry.status)}>
                          {entry.status}
                        </span>
                      </td>
                      <td>{entry.notes || '-'}</td>
                      <td>
                        {entry.status === 'REJECTED' && (
                          <button className="btn btn-sm btn-primary">Resubmit</button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Summary Cards */}
        <div className="stats-grid" style={{ marginTop: '24px' }}>
          <div className="stat-card">
            <div className="stat-card-header">
              <div className="stat-icon teal">
                <Clock size={24} />
              </div>
            </div>
            <div className="stat-value">
              {entries.reduce((sum, e) => sum + parseFloat(e.hours || 0), 0).toFixed(1)}h
            </div>
            <div className="stat-label">Total Hours This Month</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-header">
              <div className="stat-icon orange">
                <AlertCircle size={24} />
              </div>
            </div>
            <div className="stat-value">
              {entries.filter((e) => e.status === 'PENDING').length}
            </div>
            <div className="stat-label">Pending Entries</div>
          </div>
        </div>
      </div>

      {/* Add Entry Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Add Time Entry</h3>
              <button className="btn btn-icon" onClick={() => setShowModal(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Date</label>
                  <input
                    type="text"
                    className="form-input"
                    value={selectedDate?.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                    disabled
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Project</label>
                  <select
                    className="form-select"
                    value={formData.project_id}
                    onChange={(e) => setFormData({ ...formData, project_id: e.target.value })}
                    required
                  >
                    <option value="">Select a project</option>
                    {projects.map((project) => (
                      <option key={project.id} value={project.id}>
                        {project.name} - {project.client}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Hours</label>
                  <input
                    type="number"
                    className="form-input"
                    placeholder="Enter hours (0-24)"
                    value={formData.hours}
                    onChange={(e) => setFormData({ ...formData, hours: e.target.value })}
                    min="0"
                    max="24"
                    step="0.5"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Notes (Optional)</label>
                  <textarea
                    className="form-input"
                    placeholder="Add any notes about this time entry"
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    rows={3}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Entry
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Timesheets;
