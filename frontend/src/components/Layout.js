import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import {
  LayoutDashboard,
  Calendar,
  CheckSquare,
  FolderKanban,
  BarChart3,
  Users,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Bell,
  MessageSquare,
} from 'lucide-react';
import useNotificationStore from '../stores/notificationStore';
import { useEffect } from 'react';
import ErrorBoundary from './ErrorBoundary';

const Layout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, isAdmin, isManager } = useAuthStore();
  const { notifications, unreadCount, fetchNotifications, markAsRead, markAllAsRead } = useNotificationStore();
  const [collapsed, setCollapsed] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    if (user) {
      fetchNotifications();
      const interval = setInterval(fetchNotifications, 30000);
      return () => clearInterval(interval);
    }
  }, [user, fetchNotifications]);

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/timesheets', icon: Calendar, label: 'Timesheets' },
    ...(isAdmin() || isManager()
      ? [{ path: '/approvals', icon: CheckSquare, label: 'Approvals' }]
      : []),
    { path: '/projects', icon: FolderKanban, label: 'Projects' },
    { path: '/reports', icon: BarChart3, label: 'Reports' },
    ...(isAdmin()
      ? [{ path: '/users', icon: Users, label: 'User Provisioning' }]
      : []),
    { path: '/support', icon: MessageSquare, label: 'Support' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const getInitials = (name) => {
    return name
      ?.split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2) || 'U';
  };

  const getRoleBadgeClass = (role) => {
    switch (role) {
      case 'Admin': return 'role-badge admin';
      case 'Manager': return 'role-badge manager';
      default: return 'role-badge member';
    }
  };

  return (
    <div className="app-container">
      <aside
        className="sidebar"
        style={{ width: collapsed ? '80px' : '260px', transition: 'width 0.3s ease' }}
      >
        <div className="sidebar-logo" style={{ padding: '20px', textAlign: 'center', position: 'relative' }}>
          <img
            src="/logo.png"
            alt="hexhytfvb Logo"
            style={{
              height: collapsed ? '24px' : '40px',
              maxWidth: '100%',
              transition: 'height 0.3s ease'
            }}
          />
          {!collapsed && (
            <div style={{ color: 'white', fontWeight: 'bold', marginTop: '8px', fontSize: '18px' }}>
              hexhytfvb
            </div>
          )}
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <div
                key={item.path}
                className={`nav-item ${isActive ? 'active' : ''}`}
                onClick={() => navigate(item.path)}
                title={collapsed ? item.label : ''}
              >
                <Icon size={20} />
                {!collapsed && <span>{item.label}</span>}
              </div>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="user-info" style={{ flexDirection: collapsed ? 'column' : 'row', alignItems: 'center' }}>
            <div className="user-avatar">{getInitials(user?.name)}</div>
            {!collapsed && (
              <div className="user-details">
                <div className="user-name">{user?.name}</div>
                <div className="user-role">
                  {user?.roles?.map((r, idx) => (
                    <span key={r.id || r.value || idx} className={getRoleBadgeClass(String(r.value || ''))}>
                      {String(r.value || '')}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
          {!collapsed && (
            <button
              className="btn btn-secondary"
              style={{
                width: '100%',
                marginTop: '16px',
                background: 'rgba(255,255,255,0.1)',
                color: 'white',
                borderColor: 'rgba(255,255,255,0.2)'
              }}
              onClick={handleLogout}
            >
              <LogOut size={18} />
              Sign Out
            </button>
          )}
        </div>

        <button
          className="btn-icon"
          style={{
            position: 'absolute',
            right: -12,
            top: '50%',
            transform: 'translateY(-50%)',
            background: 'white',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            borderRadius: '50%',
            width: '24px',
            height: '24px',
            padding: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100
          }}
          onClick={() => setCollapsed(!collapsed)}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </aside>

      <main className="main-content">
        <header className="top-bar">
          <div className="top-bar-spacer"></div>
          <div className="top-bar-actions">
            <ErrorBoundary fallback={<div className="error-text">!</div>}>
              <div className="notification-wrapper">
                <div 
                  className="notification-bell-container dark"
                  onClick={() => {
                    if (!showNotifications && unreadCount > 0) {
                      markAllAsRead();
                    }
                    setShowNotifications(!showNotifications);
                  }}
                  title="Notifications"
                >
                  <Bell size={20} />
                  {unreadCount > 0 && (
                    <span className="notification-badge">{unreadCount}</span>
                  )}
                </div>

                {showNotifications && (
                  <div className="notifications-dropdown top-right">
                    <div className="notifications-header">
                      <h3>Notifications</h3>
                      {unreadCount > 0 && (
                        <button onClick={markAllAsRead}>Mark all read</button>
                      )}
                    </div>
                    <div className="notifications-list">
                      {notifications.length > 0 ? (
                        notifications.map(n => (
                          <div 
                            key={n.id} 
                            className={`notification-item ${!n.is_read ? 'unread' : ''}`}
                            onClick={() => {
                              if (!n.is_read) markAsRead(n.id);
                              if (n.link) navigate(n.link);
                              setShowNotifications(false);
                            }}
                          >
                            <div className="notification-title">{n.title}</div>
                            <div className="notification-message">{n.message}</div>
                            <div className="notification-time">
                              {new Date(n.created_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="notification-empty">No notifications</div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </ErrorBoundary>
          </div>
        </header>
        <div className="content-inner">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;