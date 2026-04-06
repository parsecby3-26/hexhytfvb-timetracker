import React, { useState, useEffect } from 'react';
import { usersAPI } from '../services/api';
import useAuthStore from '../stores/authStore';
import {
  Plus,
  X,
  Edit2,
  Trash2,
  Shield,
  UserPlus,
  Search,
} from 'lucide-react';

const UserProvisioning = () => {
  const { isAdmin } = useAuthStore();
  const [users, setUsers] = useState([]);
  const [managers, setManagers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    parent_id: '',
    roles: ['Member'],
  });

  useEffect(() => {
    fetchUsers();
    fetchManagers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await usersAPI.list();
      setUsers(response.data.data.users || []);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchManagers = async () => {
    try {
      const response = await usersAPI.getManagers();
      setManagers(response.data.data || []);
    } catch (error) {
      console.error('Error fetching managers:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (selectedUser) {
        await usersAPI.update(selectedUser.id, {
          name: formData.name,
          email: formData.email,
          parent_id: formData.parent_id === '' ? null : parseInt(formData.parent_id),
        });
        await usersAPI.updateRoles(selectedUser.id, formData.roles);
      } else {
        const payload = {
          ...formData,
          parent_id: formData.parent_id === '' ? null : parseInt(formData.parent_id)
        };
        await usersAPI.create(payload);
      }
      setShowModal(false);
      setSelectedUser(null);
      setFormData({ name: '', email: '', password: '', parent_id: '', roles: ['Member'] });
      fetchUsers();
    } catch (error) {
      console.error('Error saving user:', error);
      alert('Failed to save user. Email may already be registered.');
    }
  };

  const handleEdit = (user) => {
    setSelectedUser(user);
    setFormData({
      name: user.name,
      email: user.email,
      password: '',
      parent_id: user.parent_id || '',
      roles: user.roles.map(r => r.value),
    });
    setShowModal(true);
  };

  const handleDelete = async (userId) => {
    if (window.confirm('Are you sure you want to deactivate this user?')) {
      try {
        await usersAPI.delete(userId);
        fetchUsers();
      } catch (error) {
        console.error('Error deactivating user:', error);
      }
    }
  };

  const handleRoleChange = (role) => {
    const currentRoles = [...formData.roles];
    const index = currentRoles.indexOf(role);
    if (index > -1) {
      currentRoles.splice(index, 1);
    } else {
      currentRoles.push(role);
    }
    setFormData({ ...formData, roles: currentRoles });
  };

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getRoleBadgeClass = (role) => {
    switch (role) {
      case 'Admin':
        return 'role-badge admin';
      case 'Manager':
        return 'role-badge manager';
      default:
        return 'role-badge member';
    }
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
          <h2>User Provisioning</h2>
          <p>Manage users and role assignments</p>
        </div>
        <div className="header-actions">
          <div className="search-container">
            <Search className="search-icon" size={18} />
            <input
              type="text"
              className="form-input search-input"
              placeholder="Search users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button
            className="btn btn-secondary"
            onClick={() => document.getElementById('user-csv-import').click()}
          >
            <Plus size={18} />
            Bulk Import
          </button>
          <input
            type="file"
            id="user-csv-import"
            hidden
            accept=".csv"
            onChange={async (e) => {
              const file = e.target.files[0];
              if (!file) return;
              
              if (window.confirm(`Are you sure you want to import users from ${file.name}? all passwords will be set to hexhytfvb@123`)) {
                try {
                  setLoading(true);
                  const { importAPI } = await import('../services/api');
                  const response = await importAPI.users(file);
                  alert(response.data.message);
                  fetchUsers();
                } catch (error) {
                  console.error('Import failed:', error);
                  alert('Import failed: ' + (error.response?.data?.detail || 'Unknown error'));
                } finally {
                  setLoading(false);
                  e.target.value = ''; // Reset
                }
              }
            }}
          />
          <button
            className="btn btn-primary"
            onClick={() => {
              setSelectedUser(null);
              setFormData({ name: '', email: '', password: '', parent_id: '', roles: ['Member'] });
              setShowModal(true);
            }}
          >
            <UserPlus size={18} />
            Add User
          </button>
        </div>
      </header>

      <div className="page-content">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">All Users ({filteredUsers.length})</h3>
          </div>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Email</th>
                  <th>Roles</th>
                  <th>Manager</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((user) => (
                  <tr key={user.id}>
                    <td>
                      <div className="flex items-center gap-3">
                        <div className="avatar">
                          {user.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                        </div>
                        <div>
                          <div className="font-medium">{user.name}</div>
                          <div className="text-xs text-muted">ID: {user.id}</div>
                        </div>
                      </div>
                    </td>
                    <td>{user.email}</td>
                    <td>
                      <div className="flex gap-1 flex-wrap">
                        {user.roles.map((role) => (
                          <span key={role.id} className={getRoleBadgeClass(role.value)}>
                            {role.value}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>{user.manager_name || '-'}</td>
                    <td>
                      <span className={`badge badge-${user.status ? 'active' : 'inactive'}`}>
                        {user.status ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <div className="flex gap-2">
                        <button
                          className="btn btn-icon"
                          onClick={() => handleEdit(user)}
                          title="Edit"
                        >
                          <Edit2 size={16} />
                        </button>
                        <button
                          className="btn btn-icon"
                          onClick={() => handleDelete(user.id)}
                          title="Deactivate"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Stats */}
        <div className="stats-grid" style={{ marginTop: '24px' }}>
          <div className="stat-card">
            <div className="stat-card-header">
              <div className="stat-icon teal">
                <Shield size={24} />
              </div>
            </div>
            <div className="stat-value">{users.filter(u => u.roles.some(r => r.value === 'Admin')).length}</div>
            <div className="stat-label">Admins</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-header">
              <div className="stat-icon blue">
                <UserPlus size={24} />
              </div>
            </div>
            <div className="stat-value">{users.filter(u => u.roles.some(r => r.value === 'Manager')).length}</div>
            <div className="stat-label">Managers</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-header">
              <div className="stat-icon green">
                <Shield size={24} />
              </div>
            </div>
            <div className="stat-value">{users.filter(u => u.roles.some(r => r.value === 'Member')).length}</div>
            <div className="stat-label">Members</div>
          </div>
        </div>
      </div>

      {/* Add/Edit User Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">
                {selectedUser ? 'Edit User' : 'Create New User'}
              </h3>
              <button className="btn btn-icon" onClick={() => setShowModal(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Full Name</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="Enter full name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Email Address</label>
                  <input
                    type="email"
                    className="form-input"
                    placeholder="Enter email address"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                  />
                </div>

                {!selectedUser && (
                  <div className="form-group">
                    <label className="form-label">Password</label>
                    <input
                      type="password"
                      className="form-input"
                      placeholder="Enter password"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      required={!selectedUser}
                    />
                  </div>
                )}

                <div className="form-group">
                  <label className="form-label">Reporting Manager</label>
                  <select
                    className="form-select"
                    value={formData.parent_id}
                    onChange={(e) => setFormData({ ...formData, parent_id: e.target.value })}
                  >
                    <option value="">No manager assigned</option>
                    {managers.map((manager) => (
                      <option key={manager.id} value={manager.id}>
                        {manager.name} ({manager.email})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Roles</label>
                  <div className="flex gap-4">
                    {['Admin', 'Manager', 'Member'].map((role) => (
                      <label key={role} className="checkbox-container">
                        <div
                          className={`checkbox ${formData.roles.includes(role) ? 'checked' : ''}`}
                          onClick={() => handleRoleChange(role)}
                        >
                          {formData.roles.includes(role) && (
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                              <polyline points="20 6 9 17 4 12" />
                            </svg>
                          )}
                        </div>
                        <span>{role}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {selectedUser ? 'Update User' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserProvisioning;



