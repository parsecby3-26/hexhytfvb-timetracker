import React, { useState, useEffect } from 'react';
import { projectsAPI, usersAPI } from '../services/api';
import useAuthStore from '../stores/authStore';
import { Plus, Edit2, Trash2 } from 'lucide-react';

const Projects = () => {
  const { user, isAdmin, isManager } = useAuthStore();
  const [projects, setProjects] = useState([]);
  const [managers, setManagers] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [formData, setFormData] = useState({ name: '', client: '', client_id: '', client_id: '', manager_id: '', reporting_area: '' });
  const [modalMembers, setModalMembers] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProjects();
    fetchInitialData();
  }, []);

  const fetchProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Fetching projects from:', projectsAPI);
      const response = await projectsAPI.list();
      console.log('Projects response:', response);
      
      // Handle different response structures
      const projectsList = response?.data?.data?.projects || response?.data?.data || response?.data || [];
      let projectsArray = Array.isArray(projectsList) ? projectsList : [];
      
      // Ensure it's always an array
      if (!Array.isArray(projectsArray)) {
        projectsArray = [];
      }
      
      // Fetch members for each project
      const projectsWithMembers = await Promise.all(
        projectsArray.map(async (project) => {
          try {
            const membersRes = await projectsAPI.getMembers(project.id);
            return {
              ...project,
              members: Array.isArray(membersRes?.data?.data) ? membersRes.data.data : []
            };
          } catch (err) {
            console.error(`Error fetching members for project ${project.id}:`, err);
            return { ...project, members: [] };
          }
        })
      );
      
      setProjects(Array.isArray(projectsWithMembers) ? projectsWithMembers : []);
    } catch (error) {
      console.error('Error fetching projects:', error.message, error.response?.data);
      setError(`Failed to load projects: ${error.response?.data?.message || error.message}`);
      setProjects([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchInitialData = async () => {
    try {
      const [mgrRes, userRes] = await Promise.all([usersAPI.getManagers(), usersAPI.list()]);
      
      let managersList = mgrRes?.data?.data || [];
      let usersList = userRes?.data?.data || [];
      
      // Handle nested response structure from backend
      if (usersList && typeof usersList === 'object' && !Array.isArray(usersList)) {
        // If data has "users" property, extract it
        if (usersList.users) {
          usersList = usersList.users;
        } else {
          // Otherwise try to find array in object values
          const values = Object.values(usersList);
          if (Array.isArray(values[0]) && values[0].length > 0 && values[0][0]?.id) {
            usersList = values[0];
          } else {
            usersList = values.filter(v => Array.isArray(v) && v[0]?.id);
            if (usersList.length > 0) {
              usersList = usersList[0];
            }
          }
        }
      }
      
      console.log('Processed managers:', managersList);
      console.log('Processed users:', usersList);
      
      setManagers(Array.isArray(managersList) ? managersList : []);
      setAllUsers(Array.isArray(usersList) ? usersList : []);
    } catch (error) {
      console.error('Error fetching data:', error.message, error.response?.data);
      setManagers([]);
      setAllUsers([]);
    }
  };

  const handleAddMember = async (projectId, userId) => {
    if (!userId) return;
    try {
      await projectsAPI.addMember(projectId, { user_id: parseInt(userId), bill_rate: 0 });
      await fetchProjects();
      // Reset the select by triggering a re-render
    } catch (error) {
      console.error('Error assigning member:', error);
      alert('Failed to assign member');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const finalData = { 
      ...formData, 
      manager_id: isAdmin ? (formData.manager_id === '' ? null : parseInt(formData.manager_id)) : user?.id 
    };
    try {
      if (selectedProject) { await projectsAPI.update(selectedProject.id, finalData); }
      else { await projectsAPI.create(finalData); }
      
      // Save members if we're updating and modal members were modified
      if (selectedProject) {
        await handleSaveProjectMembers();
      }
      
      setShowModal(false);
      setModalMembers([]);
      fetchProjects();
    } catch (error) {
      console.error('Error saving project:', error);
      alert('Failed to save project');
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        await projectsAPI.delete(projectId);
        fetchProjects();
      } catch (error) {
        alert('Failed to delete project');
      }
    }
  };

  const handleAddMemberToModal = (userId) => {
    const user = allUsers.find(u => u.id === parseInt(userId));
    if (user && !modalMembers.some(m => m.user_id === user.id)) {
      console.log('Adding member:', user);
      setModalMembers([...modalMembers, { user_id: user.id, user_name: user.name }]);
    }
  };

  const handleRemoveMemberFromModal = (userId) => {
    setModalMembers(modalMembers.filter(m => m.user_id !== userId));
  };

  const handleSaveProjectMembers = async () => {
    try {
      // Get current members from the project
      const currentMembers = selectedProject?.members || [];
      const currentMemberIds = new Set(currentMembers.map(m => m.user_id));
      const newMemberIds = new Set(modalMembers.map(m => m.user_id));
      
      if (!selectedProject?.id) {
        console.error('Cannot save members: No project selected or project has no ID');
        return;
      }

      // Add new members
      for (const memberId of newMemberIds) {
        if (memberId && !currentMemberIds.has(memberId)) {
          await projectsAPI.addMember(selectedProject.id, { user_id: memberId, bill_rate: 0 });
        }
      }
      
      // Remove members not in the list
      for (const memberId of currentMemberIds) {
        if (memberId && !newMemberIds.has(memberId)) {
          await projectsAPI.removeMember(selectedProject.id, memberId);
        }
      }
      
      await fetchProjects();
    } catch (error) {
      console.error('Error saving members:', error);
      alert('Failed to save project members');
    }
  };

  return (
    <div className="page-container">
      <header className="header">
        <div className="header-title"><h2>Projects</h2></div>
        {(isAdmin || isManager) && (
          <div className="flex gap-2">
            <button
              className="btn btn-secondary"
              onClick={() => document.getElementById('project-csv-import').click()}
            >
              <Plus size={18} /> Bulk Import
            </button>
            <input
              type="file"
              id="project-csv-import"
              hidden
              accept=".csv"
              onChange={async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                
                if (window.confirm(`Import projects from ${file.name}?`)) {
                  try {
                    setLoading(true);
                    const { importAPI } = await import('../services/api');
                    const response = await importAPI.projects(file);
                    alert(response.data.message);
                    fetchProjects();
                  } catch (error) {
                    console.error('Import failed:', error);
                    alert('Import failed: ' + (error.response?.data?.detail || 'Unknown error'));
                  } finally {
                    setLoading(false);
                    e.target.value = '';
                  }
                }
              }}
            />
            <button className="btn btn-primary" onClick={() => { setSelectedProject(null); setFormData({ name: '', client: '', client_id: '', manager_id: isAdmin ? '' : user?.id, reporting_area: '' }); setShowModal(true); }}>
              <Plus size={18} /> New Project
            </button>
          </div>
        )}
      </header>

      <div className="page-content">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        {loading ? (
          <div className="text-center py-8">Loading projects...</div>
        ) : !Array.isArray(projects) || projects.length === 0 ? (
          <div className="text-center py-8 text-secondary">No projects found</div>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Project / Client</th>
                  <th>Manager</th>
                  <th>Team Allocation</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {Array.isArray(projects) && projects.map(p => {
                  const canManage = isAdmin || (isManager && p.manager_id === user?.id);
                  const projectMembers = Array.isArray(p?.members) ? p.members : [];
                  const availableUsers = (Array.isArray(allUsers) ? allUsers : []).filter(u => !projectMembers.some(m => m.user_id === u.id));
                  return (
                    <tr key={p.id}>
                      <td><div className="font-bold">{p.name}</div><div className="text-xs text-secondary">{p.client}</div></td>
                      <td>{p.manager_name}</td>
                      <td>
                        <div className="flex flex-wrap gap-2 items-center">
                          {/* Show member names if: admin, manager, or employee assigned to this project */}
                          {(() => {
                            const isEmployeeOnProject = projectMembers.some(m => m.user_id === user?.id);
                            const canViewMembers = isAdmin || isManager || isEmployeeOnProject;
                            
                            if (canViewMembers) {
                              return (
                                <>
                                  {projectMembers.slice(0, 2).map(m => (
                                    <span key={m.user_id} className="px-2 py-1 bg-slate-100 rounded text-xs border border-slate-200">{m.user_name}</span>
                                  ))}
                                  {projectMembers.length > 2 && (
                                    <span className="px-2 py-1 bg-slate-200 rounded text-xs border border-slate-300 font-semibold">+{projectMembers.length - 2}</span>
                                  )}
                                </>
                              );
                            } else {
                              // Employee not on this project - show count only
                              return (
                                <span className="text-sm text-muted">
                                  {projectMembers.length} member{projectMembers.length !== 1 ? 's' : ''}
                                </span>
                              );
                            }
                          })()}
                          {canManage && availableUsers.length > 0 && (
                            <select 
                              className="form-select text-xs py-1 px-2" 
                              onChange={(e) => {
                                if (e.target.value) {
                                  handleAddMember(p.id, e.target.value);
                                  e.target.value = '';
                                }
                              }} 
                              value=""
                              defaultValue=""
                            >
                              <option value="" disabled>+ Assign</option>
                              {availableUsers.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}
                            </select>
                          )}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                          {canManage && (
                            <button className="btn-icon" onClick={() => { 
                              console.log('Opening edit modal. allUsers:', allUsers);
                              setSelectedProject(p); 
                              setFormData(p); 
                              setModalMembers(Array.isArray(p.members) ? p.members : []); 
                              setShowModal(true); 
                            }} title="Edit"><Edit2 size={16} /></button>
                          )}
                          {isAdmin && (
                            <button className="btn-icon btn-danger" onClick={() => handleDeleteProject(p.id)} title="Delete"><Trash2 size={16} /></button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <form onSubmit={handleSubmit}>
              <div className="modal-header"><h3>{selectedProject ? 'Edit' : 'Create'} Project</h3></div>
              <div className="modal-body">
                <input className="form-input mb-4" placeholder="Name" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} required />
                <input className="form-input mb-4" placeholder="Client" value={formData.client} onChange={e => setFormData({ ...formData, client: e.target.value })} required />
                <select className="form-select mb-4" value={formData.manager_id || ''} onChange={e => setFormData({ ...formData, manager_id: e.target.value })} required disabled={!isAdmin}>
                  <option value="">Select Manager</option>
                  {(Array.isArray(managers) ? managers : []).map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                </select>
                
                {selectedProject && (
                  <div className="mb-4">
                    <label className="block text-sm font-semibold mb-2">Project Members</label>
                    
                    {/* Current Members */}
                    {modalMembers.length > 0 && (
                      <div className="mb-3 p-3 bg-slate-50 rounded border border-slate-200">
                        <p className="text-xs font-semibold text-slate-600 mb-2">Assigned Members:</p>
                        <div className="flex flex-wrap gap-2">
                          {modalMembers.map(m => (
                            <div key={m.user_id} className="flex items-center gap-2 px-2 py-1 bg-blue-100 rounded text-xs border border-blue-300">
                              <span>{m.user_name}</span>
                              <button
                                type="button"
                                className="text-red-600 hover:text-red-800 font-bold"
                                onClick={() => handleRemoveMemberFromModal(m.user_id)}
                                title="Remove member"
                              >
                                ×
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Add Members */}
                    <div>
                      <p className="text-xs text-slate-600 mb-2">Available members: {Array.isArray(allUsers) ? allUsers.length : 0} total</p>
                      {Array.isArray(allUsers) && allUsers.length > 0 ? (
                        <select 
                          className="form-select text-sm w-full" 
                          onChange={(e) => {
                            console.log('Selected user:', e.target.value);
                            if (e.target.value) {
                              handleAddMemberToModal(e.target.value);
                              e.target.value = '';
                            }
                          }}
                          value=""
                          defaultValue=""
                        >
                          <option value="" disabled>+ Add Member</option>
                          {(allUsers || []).map(u => {
                            const isAssigned = modalMembers.some(m => m.user_id === u.id);
                            return (
                              <option key={u.id} value={u.id} disabled={isAssigned}>
                                {u.name} {isAssigned ? '(assigned)' : ''}
                              </option>
                            );
                          })}
                        </select>
                      ) : (
                        <div className="text-sm text-slate-500 p-2 border border-slate-200 rounded">
                          {Array.isArray(allUsers) ? 'No members available to add' : 'Loading members...'}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => { setShowModal(false); setModalMembers([]); }}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save Project</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Projects;




