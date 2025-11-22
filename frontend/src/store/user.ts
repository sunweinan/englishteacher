import { defineStore } from 'pinia';
import axios from '@/utils/http';

export interface UserProfile {
  id: number;
  username: string;
  role: 'user' | 'admin';
}

interface AuthState {
  token: string | null;
  user: UserProfile | null;
}

export const useUserStore = defineStore('user', {
  state: (): AuthState => ({
    token: localStorage.getItem('token'),
    user: null
  }),
  getters: {
    isAuthenticated: (state) => !!state.token
  },
  actions: {
    setToken(token: string | null) {
      this.token = token;
      if (token) {
        localStorage.setItem('token', token);
      } else {
        localStorage.removeItem('token');
      }
    },
    async login(username: string, password: string) {
      const res = await axios.post('/auth/login', { username, password });
      this.setToken(res.data.access_token);
      await this.fetchProfile();
    },
    async fetchProfile() {
      if (!this.token) return;
      const res = await axios.get('/auth/me');
      this.user = res.data;
    },
    logout() {
      this.setToken(null);
      this.user = null;
    }
  }
});
