import axios from 'axios';
import router from '@/router';
import { useUserStore } from '@/store/user';

const instance = axios.create({
  baseURL: '/api'
});

instance.interceptors.request.use((config) => {
  const userStore = useUserStore();
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
      const userStore = useUserStore();
      userStore.logout();
      await router.push({ name: 'login' });
    }
    return Promise.reject(error);
  }
);

export default instance;
