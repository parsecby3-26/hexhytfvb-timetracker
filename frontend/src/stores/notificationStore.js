import { create } from 'zustand';
import { notificationsAPI } from '../services/api';

const useNotificationStore = create((set, get) => ({
  notifications: [],
  unreadCount: 0,
  loading: false,
  error: null,

  fetchNotifications: async () => {
    set({ loading: true });
    try {
      const response = await notificationsAPI.getNotifications();
      const { notifications, unread_count } = response.data.data;
      set({ 
        notifications, 
        unreadCount: unread_count, 
        loading: false,
        error: null
      });
    } catch (error) {
      set({ 
        error: error.response?.data?.message || 'Failed to fetch notifications',
        loading: false 
      });
    }
  },

  markAsRead: async (id) => {
    try {
      await notificationsAPI.markAsRead(id);
      const { notifications, unreadCount } = get();
      const updatedNotifications = notifications.map(n => 
        n.id === id ? { ...n, is_read: true } : n
      );
      set({ 
        notifications: updatedNotifications,
        unreadCount: Math.max(0, unreadCount - 1)
      });
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  },

  markAllAsRead: async () => {
    try {
      await notificationsAPI.markAllAsRead();
      const { notifications } = get();
      const updatedNotifications = notifications.map(n => ({ ...n, is_read: true }));
      set({ 
        notifications: updatedNotifications,
        unreadCount: 0
      });
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  },

  addNotification: (notification) => {
    const { notifications, unreadCount } = get();
    set({
      notifications: [notification, ...notifications].slice(0, 50),
      unreadCount: unreadCount + 1
    });
  }
}));

export default useNotificationStore;
