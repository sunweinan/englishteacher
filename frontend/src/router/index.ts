import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/store/user';
import { useAdminAuthStore } from '@/store/adminAuth';
import { fetchInstallStatus } from '@/utils/install';

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/install',
    name: 'install',
    component: () => import('@/views/Install/InstallWizard.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/playground',
    name: 'playground',
    component: () => import('@/views/Playground.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/auth/login',
    name: 'login',
    component: () => import('@/views/Auth/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/admin/login',
    name: 'admin-login',
    component: () => import('@/views/Admin/AdminLogin.vue'),
    meta: { requiresAdmin: false }
  },
  {
    path: '/member',
    name: 'member-center',
    component: () => import('@/views/Member/Center.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/recharge',
    name: 'recharge',
    component: () => import('@/views/Payment/Plans.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    component: () => import('@/views/Admin/Layout.vue'),
    meta: { requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'admin-dashboard',
        component: () => import('@/views/Admin/Dashboard.vue')
      },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('@/views/Admin/Users.vue')
      },
      {
        path: 'payments',
        name: 'admin-payments',
        component: () => import('@/views/Admin/Payments.vue')
      },
      {
        path: 'settings',
        name: 'admin-settings',
        component: () => import('@/views/Admin/SystemConfig.vue')
      },
      {
        path: 'courses',
        name: 'admin-courses',
        component: () => import('@/views/Admin/Courses.vue')
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

let installChecked = false;
let installRequired = false;

const ensureInstallReady = async () => {
  if (installChecked) return installRequired;
  try {
    const { data } = await fetchInstallStatus();
    installRequired = !data.connected || !data.installed;
  } catch (error) {
    console.error('Install status check failed', error);
    installRequired = false;
  }
  installChecked = true;
  return installRequired;
};

router.beforeEach(async (to, _from, next) => {
  if (to.name !== 'install') {
    const needsInstall = await ensureInstallReady();
    if (needsInstall) {
      next({ name: 'install', query: { redirect: to.fullPath } });
      return;
    }
  }

  const userStore = useUserStore();
  const adminStore = useAdminAuthStore();

  if (to.meta.requiresAdmin && !adminStore.isAuthenticated) {
    next({ name: 'admin-login', query: { redirect: to.fullPath } });
    return;
  }

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } });
    return;
  }

  next();
});

export default router;
