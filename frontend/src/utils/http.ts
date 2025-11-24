import axios from 'axios';
import router from '@/router';
import { API_ENDPOINTS, getApiBaseUrl } from '@/config/api';
import { useUserStore } from '@/store/user';
import { useAdminAuthStore } from '@/store/adminAuth';

const isAdminRequest = (url?: string) => {
  if (!url) return false;
  return url.startsWith('/admin') || url === API_ENDPOINTS.adminLogin;
};

const instance = axios.create({
  baseURL: getApiBaseUrl()
});

instance.interceptors.request.use((config) => {
  const adminStore = useAdminAuthStore();
  const userStore = useUserStore();
  if (isAdminRequest(config.url)) {
    if (adminStore.token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${adminStore.token}`;
    }
    return config;
  }
  if (userStore.token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${userStore.token}`;
  }
  return config;
});

instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const isAdmin = isAdminRequest(error.config?.url);
      if (isAdmin && error.config?.url !== API_ENDPOINTS.adminLogin) {
        const adminStore = useAdminAuthStore();
        adminStore.logout();
        await router.push({ name: 'admin-login' });
      } else if (!isAdmin && error.config?.url !== API_ENDPOINTS.authLogin) {
        const userStore = useUserStore();
        userStore.logout();
        await router.push({ name: 'login' });
      }
    }
    return Promise.reject(error);
  }
);

export default instance;
