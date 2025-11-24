import { defineStore } from 'pinia';
import http from '@/utils/http';
import { API_ENDPOINTS } from '@/config/api';

interface AdminAuthState {
  token: string | null;
  username: string | null;
  isDefaultAdmin: boolean;
}

export const useAdminAuthStore = defineStore('adminAuth', {
  state: (): AdminAuthState => ({
    token: localStorage.getItem('adminToken'),
    username: localStorage.getItem('adminUsername'),
    isDefaultAdmin: localStorage.getItem('adminIsDefault') === 'true'
  }),
  getters: {
    isAuthenticated: (state) => !!state.token
  },
  actions: {
    setSession(token: string, username: string, isDefaultAdmin = false) {
      this.token = token;
      this.username = username;
      this.isDefaultAdmin = isDefaultAdmin;
      localStorage.setItem('adminToken', token);
      localStorage.setItem('adminUsername', username);
      localStorage.setItem('adminIsDefault', String(isDefaultAdmin));
    },
    logout() {
      this.token = null;
      this.username = null;
      this.isDefaultAdmin = false;
      localStorage.removeItem('adminToken');
      localStorage.removeItem('adminUsername');
      localStorage.removeItem('adminIsDefault');
    },
    async login(username: string, password: string) {
      const response = await http.post(API_ENDPOINTS.adminLogin, { username, password });
      this.setSession(
        response.data.access_token,
        username,
        Boolean(response.data.is_default_admin)
      );
    }
  }
});
