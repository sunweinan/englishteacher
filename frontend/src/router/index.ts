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
    path: '/auth/login',
    name: 'login',
    component: () => import('@/views/Auth/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/products',
    name: 'product-list',
    component: () => import('@/views/Product/List.vue')
  },
  {
    path: '/products/:id',
    name: 'product-detail',
    component: () => import('@/views/Product/Detail.vue')
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: () => import('@/views/Payment/Checkout.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    component: () => import('@/views/Admin/Layout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: '',
        name: 'admin-home',
        component: () => import('@/views/Admin/Dashboard.vue')
      },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('@/views/Admin/Users.vue')
      },
      {
        path: 'products',
        name: 'admin-products',
        component: () => import('@/views/Admin/Products.vue')
      },
      {
        path: 'orders',
        name: 'admin-orders',
        component: () => import('@/views/Admin/Orders.vue')
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
  if (to.meta.role && userStore.user?.role !== to.meta.role) {
    next({ name: 'home' });
    return false;
  }
  return true;
};

router.beforeEach((to, _from, next) => {
  const authed = checkAuth(to, next);
  if (!authed) return;
  const roleOk = checkRole(to, next);
  if (!roleOk) return;
  next();
});

export default router;
