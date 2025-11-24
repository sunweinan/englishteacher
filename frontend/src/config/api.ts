export type ApiEnvironment = 'local' | 'production';

export const API_BASE_URLS: Record<ApiEnvironment, string> = {
  local: 'http://127.0.0.1:8001',
  production: 'https://api.example.com'
};

export const DEFAULT_API_ENV: ApiEnvironment = 'local';

export const API_ENDPOINTS = {
  authLogin: '/auth/login',
  adminLogin: '/auth/admin/login',
  authMe: '/auth/me',
  products: '/products',
  productDetail: (id: number | string) => `/products/${id}`,
  wechatConfig: '/payments/wechat/config',
  wechatOrder: '/payments/wechat',
  adminDatabaseTest: '/admin/database/test',
  adminConfig: '/admin/config',
  installStatus: '/install/status',
  installRun: '/install/run'
};

export function getApiEnvironment(): ApiEnvironment {
  const env = import.meta.env.VITE_API_ENV as ApiEnvironment | undefined;
  if (env && env in API_BASE_URLS) {
    return env;
  }
  return DEFAULT_API_ENV;
}

export function getApiBaseUrl(): string {
  return API_BASE_URLS[getApiEnvironment()];
}
