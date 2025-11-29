<template>
  <div class="install-page">
    <el-card class="status-card" :loading="statusLoading" shadow="never">
      <div class="status-header">
        <div>
          <h2>系统安装向导</h2>
          <p class="status-message">{{ status?.message || '填写数据库与站点信息，完成初始化安装。' }}</p>
        </div>
        <div class="status-tags">
          <el-tag :type="status?.connected ? 'success' : 'warning'" effect="light">
            {{ status?.connected ? '数据库已连接' : '数据库未连接' }}
          </el-tag>
          <el-tag v-if="status?.installed" type="success" effect="light">已完成安装</el-tag>
          <el-tag v-else type="info" effect="light">未安装</el-tag>
        </div>
      </div>
    </el-card>

    <div class="form-grid">
      <el-card class="form-card" shadow="never">
        <template #header>
          <div class="card-title">数据库连接测试</div>
        </template>
        <p class="card-help">步骤 1：仅使用 root 账号测试 MySQL 是否连通，确认后再继续后续步骤。</p>
        <el-form label-width="120px" label-position="left" class="install-form">
          <el-form-item label="MySQL 主机">
            <el-input v-model="form.mysql_host" placeholder="127.0.0.1" />
          </el-form-item>
          <el-form-item label="MySQL 端口">
            <el-input v-model.number="form.mysql_port" placeholder="3306" />
          </el-form-item>
          <el-form-item label="Root 密码">
            <el-input v-model="form.mysql_root_password" type="password" show-password placeholder="数据库 root 密码" />
          </el-form-item>
          <div class="form-actions">
            <el-button type="primary" :loading="testing" @click="testDatabase">
              测试数据库连接
            </el-button>
            <el-button text @click="resetProgress">清空进度</el-button>
          </div>
          <el-alert
            v-if="testResult"
            class="test-result"
            :closable="false"
            :type="testResult.root_connected ? 'success' : 'warning'"
            :title="testResult.message || '已完成 root 连接验证，已跳过业务数据库检查。'"
          >
            <div class="test-grid">
              <span>Root 连接：{{ testResult.root_connected ? '正常' : '失败' }}</span>
              <span class="muted">业务库及账号检查已跳过</span>
            </div>
          </el-alert>
        </el-form>
      </el-card>

      <el-card class="form-card" shadow="never">
        <template #header>
          <div class="card-title">数据库与站点配置</div>
        </template>
        <p class="card-help" :class="{ muted: !canConfigure }">
          步骤 2：在确认 root 可用后，设置服务器信息并创建业务数据库实例与账号，安装时将写入配置文件并初始化表结构。
        </p>
        <el-form label-width="120px" label-position="left" class="install-form">
          <el-form-item label="服务器域名">
            <el-input v-model="form.server_domain" :disabled="!canConfigure" placeholder="例如：example.com" />
          </el-form-item>
          <el-form-item label="服务器 IP">
            <el-input v-model="form.server_ip" :disabled="!canConfigure" placeholder="127.0.0.1" />
          </el-form-item>
          <el-form-item label="后端端口">
            <el-input v-model.number="form.backend_port" :disabled="!canConfigure" placeholder="8001" />
          </el-form-item>
          <el-divider />
          <el-form-item label="数据库名称">
            <el-input v-model="form.database_name" :disabled="!canConfigure" />
          </el-form-item>
          <el-form-item label="业务账号">
            <el-input v-model="form.database_user" :disabled="!canConfigure" />
          </el-form-item>
          <el-form-item label="业务密码">
            <el-input v-model="form.database_password" :disabled="!canConfigure" type="password" show-password />
          </el-form-item>
          <el-form-item label="MySQL URL (可选)">
            <el-input
              v-model="form.mysql_url"
              :disabled="!canConfigure"
              placeholder="mysql+pymysql://user:pwd@host:3306/db"
            />
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <el-card class="form-card" shadow="never">
      <template #header>
        <div class="card-title">管理员与集成</div>
      </template>
      <p class="card-help" :class="{ muted: !canConfigure }">
        步骤 3：配置后台管理员账号及第三方集成，系统会依次保存到数据库和预装配置文件，再导入预置数据。
      </p>
      <el-form label-width="120px" label-position="left" class="install-form">
        <el-form-item label="管理员账号">
          <el-input v-model="form.admin_username" :disabled="!canConfigure" />
        </el-form-item>
        <el-form-item label="管理员密码">
          <el-input v-model="form.admin_password" :disabled="!canConfigure" type="password" show-password />
        </el-form-item>
        <el-divider />
        <el-form-item label="微信 AppID">
          <el-input v-model="form.wechat_app_id" :disabled="!canConfigure" />
        </el-form-item>
        <el-form-item label="微信商户号">
          <el-input v-model="form.wechat_mch_id" :disabled="!canConfigure" />
        </el-form-item>
        <el-form-item label="微信 API Key">
          <el-input v-model="form.wechat_api_key" :disabled="!canConfigure" type="password" show-password />
        </el-form-item>
        <el-divider />
        <el-form-item label="短信服务商">
          <el-input v-model="form.sms_provider" :disabled="!canConfigure" />
        </el-form-item>
        <el-form-item label="短信 API Key">
          <el-input v-model="form.sms_api_key" :disabled="!canConfigure" type="password" show-password />
        </el-form-item>
        <el-form-item label="短信签名">
          <el-input v-model="form.sms_sign_name" :disabled="!canConfigure" />
        </el-form-item>
        <div class="form-actions">
          <el-button type="primary" :loading="installing" :disabled="!canConfigure" @click="runInstall">开始安装</el-button>
          <el-button :loading="statusLoading" @click="fetchStatus">刷新状态</el-button>
        </div>
        <p v-if="errorMessage" class="error-hint">{{ errorMessage }}</p>
      </el-form>
    </el-card>

    <el-card class="progress-card" shadow="never">
      <template #header>
        <div class="card-title">安装进度</div>
      </template>
      <p class="card-help">
        安装会严格按步骤验证 root、创建数据库和账号、生成管理员、保存配置并导入预置数据，任何一步出错都会给出清晰提示。
      </p>
      <el-empty v-if="!progress.length" description="尚未开始安装" />
      <el-timeline v-else>
        <el-timeline-item
          v-for="item in progress"
          :key="item.step"
          type="success"
          placement="top"
        >
          <div class="timeline-item">
            <strong>{{ item.label }}</strong>
            <span class="step">{{ item.step }}</span>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import http from '@/utils/http';
import { API_ENDPOINTS } from '@/config/api';
import type { DatabaseTestResult, InstallForm, InstallProgressStep, InstallResult, InstallStatus } from '@/types/install';

const status = ref<InstallStatus | null>(null);
const statusLoading = ref(false);
const testing = ref(false);
const installing = ref(false);
const testResult = ref<DatabaseTestResult | null>(null);
const progress = ref<InstallProgressStep[]>([]);
const errorMessage = ref<string | null>(null);
const router = useRouter();

const STEP_LABELS: Record<string, string> = {
  connect_root: '验证 root 账号密码',
  provision_db: '创建数据库实例和业务账号',
  init_schema: '初始化表结构',
  save_admin: '创建后台管理员并同步基础配置',
  seed_data: '导入预装数据',
  write_config: '保存安装配置文件'
};

const form = reactive<InstallForm>({
  server_domain: window.location.hostname || 'localhost',
  server_ip: '127.0.0.1',
  backend_port: 8001,
  mysql_host: '127.0.0.1',
  mysql_port: 3306,
  mysql_root_password: '',
  database_name: 'enTeacher',
  database_user: 'admin',
  database_password: '123456',
  admin_username: 'root',
  admin_password: '123456',
  mysql_url: ''
});

const resetProgress = () => {
  progress.value = [];
  errorMessage.value = null;
};

const canConfigure = computed(() => Boolean(testResult.value?.root_connected || status.value?.connected));

const fetchStatus = async () => {
  statusLoading.value = true;
  try {
    const { data } = await http.get<InstallStatus>(API_ENDPOINTS.installStatus);
    status.value = data;
  } catch (error) {
    console.error('Failed to load install status', error);
  } finally {
    statusLoading.value = false;
  }
};

const buildDatabaseTestPayload = () => ({
  host: form.mysql_host,
  port: form.mysql_port,
  root_password: form.mysql_root_password
});

const normalizeOptional = (value?: string | null) => {
  if (!value) return undefined;
  const trimmed = value.trim();
  return trimmed ? trimmed : undefined;
};

const formatErrorDetail = (detail: any) => {
  if (typeof detail === 'object' && detail) {
    const label = detail.step ? STEP_LABELS[detail.step] || detail.step : '';
    const stepHint = label ? `（步骤：${label}）` : '';
    return `${detail.message || '安装失败'}${stepHint}`;
  }
  return typeof detail === 'string' ? detail : '安装失败';
};

const testDatabase = async () => {
  testing.value = true;
  testResult.value = null;
  try {
    const { data } = await http.post<DatabaseTestResult>(API_ENDPOINTS.installTestDb, buildDatabaseTestPayload());
    testResult.value = data;
    ElMessage.success(data.message || '数据库连接成功');
  } catch (error: any) {
    const detail = error?.response?.data?.detail;
    const message = typeof detail === 'string' ? detail : detail?.message || '数据库连接失败';
    errorMessage.value = message;
    ElMessage.error(message);
  } finally {
    testing.value = false;
  }
};

const buildInstallPayload = (): InstallForm => ({
  server_domain: form.server_domain,
  server_ip: form.server_ip,
  backend_port: form.backend_port,
  mysql_url: normalizeOptional(form.mysql_url),
  mysql_host: form.mysql_host,
  mysql_port: form.mysql_port,
  mysql_root_password: form.mysql_root_password,
  database_name: form.database_name,
  database_user: form.database_user,
  database_password: form.database_password,
  admin_username: form.admin_username,
  admin_password: form.admin_password,
  wechat_app_id: normalizeOptional(form.wechat_app_id),
  wechat_mch_id: normalizeOptional(form.wechat_mch_id),
  wechat_api_key: normalizeOptional(form.wechat_api_key),
  sms_provider: normalizeOptional(form.sms_provider),
  sms_api_key: normalizeOptional(form.sms_api_key),
  sms_sign_name: normalizeOptional(form.sms_sign_name)
});

const runInstall = async () => {
  installing.value = true;
  errorMessage.value = null;
  try {
    const { data } = await http.post<InstallResult>(API_ENDPOINTS.installRun, buildInstallPayload());
    progress.value = data.progress || [];
    ElMessage.success(data.message);
    await fetchStatus();
    if (data.next_url) {
      await router.push(data.next_url);
    }
  } catch (error: any) {
    const detail = error?.response?.data?.detail;
    if (detail) {
      progress.value = detail.progress || progress.value;
      errorMessage.value = formatErrorDetail(detail);
    } else {
      errorMessage.value = '安装失败';
    }
    ElMessage.error(errorMessage.value || '安装失败');
  } finally {
    installing.value = false;
  }
};

onMounted(fetchStatus);
</script>

<style scoped>
.install-page {
  max-width: 1200px;
  margin: 24px auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-card {
  border-radius: 8px;
}

.card-help {
  margin: 0 0 8px;
  color: #909399;
  line-height: 1.5;
  font-size: 13px;
}

.card-help.muted {
  color: #c0c4cc;
}

.status-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.status-header h2 {
  margin: 0 0 4px;
}

.status-message {
  margin: 0;
  color: #606266;
}

.status-tags {
  display: flex;
  gap: 8px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.form-card {
  border-radius: 8px;
}

.card-title {
  font-weight: 600;
}

.install-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.test-result {
  margin-top: 8px;
}

.test-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 4px;
  margin-top: 6px;
}

.muted {
  color: #a0a0a0;
}

.progress-card {
  border-radius: 8px;
}

.timeline-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timeline-item .step {
  color: #909399;
  font-size: 12px;
}

.error-hint {
  color: #f56c6c;
  margin: 8px 0 0;
}
</style>
