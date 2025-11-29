export interface InstallStatus {
  connected: boolean;
  installed: boolean;
  message?: string | null;
}

export interface DatabaseTestResult {
  root_connected: boolean;
  database_exists: boolean;
  database_authenticated: boolean;
  message: string;
}

export interface InstallProgressStep {
  step: string;
  label: string;
}

export interface InstallResult {
  success: boolean;
  message: string;
  next_url: string;
  progress?: InstallProgressStep[];
}

export interface InstallForm {
  server_domain: string;
  server_ip: string;
  backend_port: number;
  mysql_url?: string;
  mysql_host: string;
  mysql_port: number;
  mysql_root_password: string;
  database_name: string;
  database_user: string;
  database_password: string;
  admin_username: string;
  admin_password: string;
  wechat_app_id?: string;
  wechat_mch_id?: string;
  wechat_api_key?: string;
  sms_provider?: string;
  sms_api_key?: string;
  sms_sign_name?: string;
}
