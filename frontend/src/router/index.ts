import { createRouter, createWebHistory, type NavigationGuardNext, type RouteLocationNormalized } from 'vue-router';
import { useUserStore } from '@/store/user';

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/Home.vue'),
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
    meta: { requiresAuth: true },
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

const checkAuth = (to: RouteLocationNormalized, next: NavigationGuardNext) => {
  const userStore = useUserStore();
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } });
    return false;
  }
  return true;
};

const checkRole = (to: RouteLocationNormalized, next: NavigationGuardNext) => {
  const userStore = useUserStore();
  // TODO: add role-based access control rules when backend roles are available
  return true;
};

router.beforeEach((to, _from, next) => {
  const authed = checkAuth(to, next);
  if (!authed) return;
  checkRole(to, next);
  next();
});

export default router;
