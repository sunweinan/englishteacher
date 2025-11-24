import http from '@/utils/http';
import { API_ENDPOINTS } from '@/config/api';

export function fetchInstallStatus() {
  return http.get(API_ENDPOINTS.installStatus);
}

export function runInstallation(payload: Record<string, any>) {
  return http.post(API_ENDPOINTS.installRun, payload);
}
