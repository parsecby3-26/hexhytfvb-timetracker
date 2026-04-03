import React, { useState, useEffect } from 'react';
import { timeEntriesAPI, projectsAPI } from '../services/api';
import { ChevronLeft, ChevronRight, Plus, Calendar as CalendarIcon, List, AlertCircle, Edit2 } from 'lucide-react';

const Timesheets = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [entries, setEntries] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedDate, setSelectedDate] = useState(null);
  const [viewMode, setViewMode] = useState('calendar');
  const [editingEntry, setEditingEntry] = useState(null);
  const [formData, setFormData] = useState({ project_id: '', hours: '', notes: '' });

  useEffect(() => { fetchProjects(); }, []);
  useEffect(() => { fetchEntries(); }, [currentDate]);

  const fetchProjects = async () => {
    try {
      const response = await projectsAPI.list();
      setProjects(response?.data?.data?.projects || []);
    } catch (error) { console.error(error); }
  };

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth();
      const response = await timeEntriesAPI.list({
        start_date: new Date(year, month, 1).toISOString().split('T')[0],
        end_date: new Date(year, month + 1, 0).toISOString().split('T')[0]
      });
      setEntries(response?.data?.data?.entries || []);
    } catch (error) { console.error(error); }
    finally { setLoading(false); }
  };

  const isDateInCurrentWeek = (date) => {
    if (!date) return false;
    const now = new Date();
    const dayOfWeek = now.getDay(); // 0 is Sunday
    const diffToMonday = now.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
    const monday = new Date(now.setDate(diffToMonday));
    monday.setHours(0, 0, 0, 0);

    const sunday = new Date(monday);
    sunday.setDate(monday.getDate() + 6);
    sunday.setHours(23, 59, 59, 999);

    const checkDate = new Date(date);
    return checkDate >= monday && checkDate <= sunday;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (editingEntry) {
      // Editing existing entry (new hours)
      try {
        // Validate hours
        const hoursValue = parseFloat(formData.hours);
        console.log('Hours validation - formData.hours:', formData.hours, 'parsed:', hoursValue);
        
        if (isNaN(hoursValue)) {
          alert('Please enter valid hours');
          return;
        }
        if (hoursValue < 0 || hoursValue > 24) {
          alert('Hours must be between 0 and 24');
          return;
        }

        const updateData = { 
          hours: hoursValue
        };
        
        // Only send notes if it has a value (not empty string)
        if (formData.notes && formData.notes.trim()) {
          updateData.notes = formData.notes.trim();
        }
        
        console.log('Project comparison - formData.project_id:', formData.project_id, 'type:', typeof formData.project_id, 
                   'editingEntry.project_id:', editingEntry.project_id, 'type:', typeof editingEntry.project_id);
        
        // Only include project_id if it's different from original
        if (formData.project_id && parseInt(formData.project_id) !== editingEntry.project_id) {
          updateData.project_id = parseInt(formData.project_id);
          console.log('Including project_id in update');
        }
        
        console.log('Final update payload:', JSON.stringify(updateData));
        console.log('Updating entry:', editingEntry.id, 'with data:', updateData);
        console.log('Entry details - ID:', editingEntry.id, 'Status:', editingEntry.status, 'User ID:', editingEntry.user_id);
        const response = await timeEntriesAPI.update(editingEntry.id, updateData);
        console.log('Update response:', response);
        setShowModal(false);
        setEditingEntry(null);
        fetchEntries();
        setFormData({ project_id: '', hours: '', notes: '' });
        alert('Entry resubmitted successfully!');
      } catch (error) {
        console.error('Update error full:', error);
        console.error('Error response:', error.response?.data);
        console.error('Error config:', error.config);
        const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || "Save failed"; 
        alert(errorMsg);
      }
    } else {
      // Creating new entry
      const existingHours = entries
        .filter(e => e.work_date === selectedDate)
        .reduce((sum, entry) => sum + parseFloat(entry.hours), 0);

      const totalHours = existingHours + parseFloat(formData.hours);
      
      // Allow any entry to be saved; total hours requirement is checked at submission
      if (isNaN(totalHours) || totalHours <= 0) {
        alert("Please enter valid hours.");
        return;
      }

      try {
        await timeEntriesAPI.create({ ...formData, work_date: selectedDate });
        setShowModal(false);
        fetchEntries();
        setFormData({ project_id: '', hours: '', notes: '' });
      } catch (error) { alert("Save failed"); }
    }
  };

  const getDaysInMonth = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const days = [];
    for (let i = 0; i < firstDay; i++) days.push(null);
    for (let i = 1; i <= daysInMonth; i++) days.push(new Date(year, month, i));
    return days;
  };

  const getDailyTotal = (date) => {
    return entries
      .filter(e => e.work_date === date)
      .reduce((sum, entry) => sum + parseFloat(entry.hours), 0);
  };

  const getProjectsForDate = (date) => {
    return entries.filter(e => e.work_date === date);
  };

  const getRejectedEntriesForDate = (date) => {
    return entries.filter(e => e.work_date === date && e.status === 'REJECTED');
  };

  const handleDateClick = (dateStr) => {
    setSelectedDate(dateStr);
    setEditingEntry(null);
    setFormData({ project_id: '', hours: '', notes: '' });
    setShowModal(true);
  };

  const handleEditRejectedEntry = (entry) => {
    console.log('Loading rejected entry for editing:', entry);
    setEditingEntry(entry);
    setFormData({
      project_id: entry.project_id ? entry.project_id.toString() : '',
      hours: entry.hours ? entry.hours.toString() : '',
      notes: entry.notes || ''
    });
    console.log('Form data set to:', {
      project_id: entry.project_id ? entry.project_id.toString() : '',
      hours: entry.hours ? entry.hours.toString() : '',
      notes: entry.notes || ''
    });
  };
  return (
    <div className="page-container">
      <header className="header">
        <div className="header-title"><h2>Timesheets</h2><p>{currentDate.toLocaleString('default', { month: 'long', year: 'numeric' })}</p></div>
        <div className="flex gap-2">
          <button className="btn btn-secondary" onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1))}><ChevronLeft /></button>
          <button className="btn btn-secondary" onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1))}><ChevronRight /></button>
        </div>
      </header>

      <div className="page-content">
        <div className="calendar-grid">
          {getDaysInMonth().map((day, idx) => {
            const dateStr = day?.toISOString().split('T')[0];
            const active = isDateInCurrentWeek(day);
            return (
              <div
                key={idx}
                className={`calendar-day ${!day ? 'empty' : ''} ${!active && day ? 'day-disabled' : ''}`}
                onClick={() => active && handleDateClick(dateStr)}
                style={!active && day ? { background: '#f8f9fa', opacity: 0.5, cursor: 'not-allowed' } : {}}
              >
                {day && <span className="day-number">{day.getDate()}</span>}
                <div className="day-entries">
                  {entries.filter(e => e.work_date === dateStr).map(e => <div key={e.id} className="text-xs">{e.hours}h</div>)}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => { setShowModal(false); setEditingEntry(null); }}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            {/* Rejected Entries Section */}
            {getRejectedEntriesForDate(selectedDate).length > 0 && !editingEntry && (
              <div style={{ marginBottom: '0', borderBottom: '1px solid var(--border)' }}>
                <div className="modal-header" style={{ paddingBottom: '12px', borderBottom: 'none' }}>
                  <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: '0 0 12px 0' }}>
                    <AlertCircle size={20} color="var(--error)" />
                    Rejected Entries - Please Review
                  </h3>
                </div>
                <div style={{ padding: '16px', background: 'rgba(220, 38, 38, 0.05)' }}>
                  {getRejectedEntriesForDate(selectedDate).map(rejectedEntry => (
                    <div key={rejectedEntry.id} style={{
                      padding: '12px',
                      marginBottom: '12px',
                      borderRadius: '8px',
                      border: '1px solid var(--error)',
                      background: 'white'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                        <div>
                          <div style={{ fontWeight: '600', color: 'var(--text)' }}>
                            {rejectedEntry.project_name} - {parseFloat(rejectedEntry.hours).toFixed(1)}h
                          </div>
                          <div style={{ fontSize: '12px', color: 'var(--error)', marginTop: '4px' }}>
                            Rejection reason: {rejectedEntry.rejection_reason || 'No reason provided'}
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleEditRejectedEntry(rejectedEntry)}
                          style={{
                            padding: '6px 12px',
                            borderRadius: '6px',
                            border: 'none',
                            background: 'var(--primary)',
                            color: 'white',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            fontSize: '12px',
                            fontWeight: '500'
                          }}
                        >
                          <Edit2 size={14} />
                          Edit & Resubmit
                        </button>
                      </div>
                      {rejectedEntry.notes && (
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '8px', fontStyle: 'italic' }}>
                          Original notes: "{rejectedEntry.notes}"
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="modal-header">
                <h3>{editingEntry ? `Edit & Resubmit: ${editingEntry.project_name}` : `Log Time: ${selectedDate}`}</h3>
              </div>
              <div className="modal-body">
                {/* Daily Total Summary */}
                <div style={{ 
                  padding: '12px', 
                  marginBottom: '16px', 
                  borderRadius: '8px',
                  background: 'rgba(13, 148, 136, 0.1)',
                  border: '1px solid rgba(13, 148, 136, 0.3)'
                }}>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Daily Total</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ fontSize: '20px', fontWeight: '600', color: 'var(--primary)' }}>
                      {getDailyTotal(selectedDate).toFixed(1)} hours
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                      {formData.hours ? `+ ${parseFloat(formData.hours).toFixed(1)} = ${(getDailyTotal(selectedDate) + parseFloat(formData.hours)).toFixed(1)} hours` : ''}
                    </div>
                  </div>
                  {(getDailyTotal(selectedDate) + (formData.hours ? parseFloat(formData.hours) : 0)) < 8 && !editingEntry && (
                    <div style={{ fontSize: '11px', color: 'var(--warning)', marginTop: '6px' }}>
                      ⚠ Need {(8 - (getDailyTotal(selectedDate) + (formData.hours ? parseFloat(formData.hours) : 0))).toFixed(1)} more hours to reach 8-hour requirement
                    </div>
                  )}
                  {(getDailyTotal(selectedDate) + (formData.hours ? parseFloat(formData.hours) : 0)) >= 8 && formData.hours && !editingEntry && (
                    <div style={{ fontSize: '11px', color: 'var(--success)', marginTop: '6px' }}>
                      ✓ Daily requirement met!
                    </div>
                  )}
                </div>

                {/* Existing entries for this day */}
                {!editingEntry && getProjectsForDate(selectedDate).length > 0 && (
                  <div style={{ marginBottom: '16px' }}>
                    <div style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-secondary)', marginBottom: '8px' }}>Logged entries:</div>
                    <div style={{ fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {getProjectsForDate(selectedDate).filter(e => e.status !== 'REJECTED').map(e => (
                        <div key={e.id} style={{ color: 'var(--text-secondary)' }}>
                          {e.project_name || `Project ${e.project_id}`}: {parseFloat(e.hours).toFixed(1)}h
                          {e.status !== 'PENDING' && (
                            <span style={{ marginLeft: '8px', fontSize: '10px', padding: '2px 6px', borderRadius: '4px', background: e.status === 'APPROVED' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(100, 116, 139, 0.2)', color: e.status === 'APPROVED' ? 'var(--success)' : 'var(--text-secondary)' }}>
                              {e.status}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {editingEntry && (
                  <div style={{ marginBottom: '16px', padding: '12px', borderRadius: '8px', background: 'rgba(59, 130, 246, 0.05)', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                      <strong>Original rejection reason:</strong>
                    </div>
                    <div style={{ fontSize: '13px', color: 'var(--error)', marginTop: '4px' }}>
                      {editingEntry.rejection_reason || 'No reason provided'}
                    </div>
                  </div>
                )}

                <select className="form-select mb-4" value={formData.project_id} onChange={e => setFormData({ ...formData, project_id: e.target.value })} disabled={editingEntry} required>
                  <option value="">Select Project</option>
                  {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
                <input type="number" step="0.5" className="form-input mb-4" placeholder="Hours" value={formData.hours} onChange={e => setFormData({ ...formData, hours: e.target.value })} required />
                <textarea className="form-input" placeholder={editingEntry ? "Explain how you've fixed the issue..." : "Notes (optional)"} rows="4" value={formData.notes} onChange={e => setFormData({ ...formData, notes: e.target.value })} />
              </div>
              <div className="modal-footer">
                <button type="button" onClick={() => { setShowModal(false); setEditingEntry(null); }} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingEntry ? 'Resubmit Entry' : 'Save Entry'}
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