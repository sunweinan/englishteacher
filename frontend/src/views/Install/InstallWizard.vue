<template>
  <div class="install-page">
    <el-card class="install-card" shadow="hover">
      <div class="install-header">
        <div>
          <h2>EnglishTeacher 系统安装向导</h2>
          <p class="subtitle">首次启动时完成数据库与管理员初始化，仅在未连接 MySQL 时出现。</p>
        </div>
        <el-tag :type="status.connected ? 'success' : 'danger'">
          {{ status.connected ? 'MySQL 链接成功' : '未连接 MySQL' }}
        </el-tag>
      </div>

      <el-alert
        v-if="!status.connected"
        type="warning"
        show-icon
        class="mb-16"
        title="请按照下方步骤完成安装，确保提供 MySQL root 密码和服务器信息。"
      />

      <el-steps :active="activeStep" finish-status="success" align-center class="mb-16">
        <el-step
          v-for="step in stepItems"
          :key="step.key"
          :title="step.title"
          :description="step.description"
          :status="stepStatuses[step.key]"
        />
      </el-steps>

      <el-form :model="form" label-width="160px" :disabled="loading">
        <el-divider>MySQL 连接</el-divider>
        <el-form-item label="MySQL URL (可选)">
          <el-input v-model="form.mysqlUrl" placeholder="不填则使用下方主机与端口" />
        </el-form-item>
        <el-form-item label="MySQL 主机">
          <el-input v-model="form.mysqlHost" placeholder="默认与服务器一致" />
          <p class="form-tip">
            如果通过 docker-compose 运行，请将主机填写为 <code>db</code>，或在宿主机暴露后使用
            <code>host.docker.internal</code>，避免在容器内使用 <code>127.0.0.1</code>。
          </p>
        </el-form-item>
        <el-form-item label="MySQL 端口">
          <el-input-number v-model="form.mysqlPort" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="MySQL root 密码" required>
          <div class="inline-input">
            <el-input v-model="form.mysqlRootPassword" type="password" show-password />
            <el-button type="primary" :loading="testingConnection" @click="handleTestConnection">测试连接</el-button>
          </div>
        </el-form-item>

        <el-divider>数据库实例</el-divider>
        <el-form-item label="数据库名称">
          <el-input v-model="form.databaseName" />
        </el-form-item>
        <el-form-item label="业务账号">
          <el-input v-model="form.databaseUser" />
        </el-form-item>
        <el-form-item label="业务密码">
          <el-input v-model="form.databasePassword" type="password" show-password />
        </el-form-item>

        <el-divider>服务器与后端配置</el-divider>
        <el-form-item label="服务器域名">
          <el-input v-model="form.serverDomain" placeholder="例如 api.example.com" />
        </el-form-item>
        <el-form-item label="服务器 IP 地址">
          <el-input v-model="form.serverIp" placeholder="例如 192.168.1.10" />
        </el-form-item>
        <el-form-item label="后端端口">
          <el-input-number v-model="form.backendPort" :min="1" :max="65535" />
        </el-form-item>

        <el-divider>后台管理员</el-divider>
        <el-form-item label="管理员用户名">
          <el-input v-model="form.adminUsername" />
        </el-form-item>
        <el-form-item label="管理员密码">
          <el-input v-model="form.adminPassword" type="password" show-password />
        </el-form-item>

        <el-divider>微信支付</el-divider>
        <el-form-item label="微信支付 AppID">
          <el-input v-model="form.wechatAppId" />
        </el-form-item>
        <el-form-item label="微信商户号">
          <el-input v-model="form.wechatMchId" />
        </el-form-item>
        <el-form-item label="微信 API Key">
          <el-input v-model="form.wechatApiKey" type="password" show-password />
        </el-form-item>

        <el-divider>短信服务</el-divider>
        <el-form-item label="短信服务商">
          <el-input v-model="form.smsProvider" />
        </el-form-item>
        <el-form-item label="短信 API Key">
          <el-input v-model="form.smsApiKey" type="password" show-password />
        </el-form-item>
        <el-form-item label="短信签名">
          <el-input v-model="form.smsSignName" />
        </el-form-item>

        <div class="actions">
          <el-button type="primary" size="large" :loading="loading" @click="handleSubmit">确定安装</el-button>
          <span class="progress-text" v-if="statusText">{{ statusText }}</span>
        </div>
        <el-progress v-if="progress > 0" :percentage="progress" :status="progressStatus" class="progress-bar" />
      </el-form>
    </el-card>

    <el-dialog v-model="resultDialog" title="安装结果" width="520px" :close-on-click-modal="false">
      <p>{{ resultMessage }}</p>
      <p class="mt-8">请妥善保存刚才填写的数据库与管理员账号信息。</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="goToAdmin">进入后台登录</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import router from '@/router';
import http from '@/utils/http';
import { API_ENDPOINTS } from '@/config/api';
import { fetchInstallStatus } from '@/utils/install';

const loading = ref(false);
const progress = ref(0);
const progressStatus = ref<'success' | 'exception' | ''>('');
const activeStep = ref(0);
const statusText = ref('');
const resultDialog = ref(false);
const resultMessage = ref('');
const status = reactive({ connected: false, installed: false });
const testingConnection = ref(false);

const stepItems = [
  { key: 'check_db', title: '检测数据库', description: '验证 MySQL 连接' },
  { key: 'fill_form', title: '填写信息', description: '输入服务器、数据库与管理员信息' },
  { key: 'initialize', title: '初始化数据库', description: '测试连接并初始化数据' },
  { key: 'finish', title: '完成', description: '准备进入后台登录' }
] as const;

type StepKey = (typeof stepItems)[number]['key'];
type StepStatus = 'wait' | 'process' | 'success' | 'error';

const stepStatuses = reactive<Record<StepKey, StepStatus>>(
  stepItems.reduce((acc, item, index) => {
    acc[item.key] = index === 0 ? 'process' : 'wait';
    return acc;
  }, {} as Record<StepKey, StepStatus>)
);

const form = reactive({
  serverDomain: window.location.hostname,
  serverIp: '',
  backendPort: 8001,
  mysqlUrl: '',
  mysqlHost: '',
  mysqlPort: 3306,
  mysqlRootPassword: '',
  databaseName: '',
  databaseUser: '',
  databasePassword: '',
  adminUsername: '',
  adminPassword: '',
  wechatAppId: '',
  wechatMchId: '',
  wechatApiKey: '',
  smsProvider: '',
  smsApiKey: '',
  smsSignName: ''
});

const resetSteps = () => {
  stepItems.forEach((item, index) => {
    stepStatuses[item.key] = index === 0 ? 'process' : 'wait';
  });
  activeStep.value = 0;
  progress.value = 0;
};

const syncProgressFromSteps = () => {
  const total = stepItems.length;
  const completed = stepItems.filter((step) => stepStatuses[step.key] === 'success').length;
  const hasProcessing = stepItems.some((step) => stepStatuses[step.key] === 'process');
  const percent = Math.min(100, Math.round(((completed + (hasProcessing ? 0.5 : 0)) / total) * 100));
  progress.value = Math.max(progress.value, percent);
};

const loadStatus = async () => {
  const { data } = await fetchInstallStatus();
  status.connected = data.connected;
  status.installed = data.installed;
  if (data.installed) {
    await router.push({ name: 'admin-login' });
  }
};

onMounted(() => {
  loadStatus().catch((error) => {
    statusText.value = error.message;
  });
});

const buildPayload = () => ({
  server_domain: form.serverDomain,
  server_ip: form.serverIp,
  backend_port: form.backendPort,
  mysql_url: form.mysqlUrl || null,
  mysql_host: form.mysqlHost || form.serverDomain || null,
  mysql_port: form.mysqlPort,
  mysql_root_password: form.mysqlRootPassword,
  database_name: form.databaseName,
  database_user: form.databaseUser,
  database_password: form.databasePassword,
  admin_username: form.adminUsername,
  admin_password: form.adminPassword,
  wechat_app_id: form.wechatAppId || null,
  wechat_mch_id: form.wechatMchId || null,
  wechat_api_key: form.wechatApiKey || null,
  sms_provider: form.smsProvider || null,
  sms_api_key: form.smsApiKey || null,
  sms_sign_name: form.smsSignName || null
});

const markStepSuccess = (key: StepKey) => {
  stepStatuses[key] = 'success';
  const nextIndex = stepItems.findIndex((item) => stepStatuses[item.key] !== 'success');
  activeStep.value = nextIndex === -1 ? stepItems.length - 1 : Math.max(nextIndex, 0);
  syncProgressFromSteps();
};

const handleTestConnection = async () => {
  const host = form.mysqlHost?.trim();
  if (!host) {
    ElMessage.error('请填写 MySQL 主机或服务器域名');
    return;
  }

  if (!form.mysqlRootPassword) {
    ElMessage.error('请填写 MySQL root 密码后再测试连接');
    return;
  }

  testingConnection.value = true;
  statusText.value = '正在检测数据库连接...';
  stepStatuses.check_db = 'process';
  syncProgressFromSteps();

  try {
    const response = await http.post(API_ENDPOINTS.installDatabaseTest, {
      host,
      port: form.mysqlPort,
      root_password: form.mysqlRootPassword
    });

    const successMessage = response.data?.message || '数据库连接正常，请继续填写';
    ElMessage.success(successMessage);
    status.connected = true;
    statusText.value = successMessage;
    markStepSuccess('check_db');
    stepStatuses.fill_form = 'process';
    activeStep.value = 1;
  } catch (error: any) {
    const message = error?.response?.data?.detail || '数据库连接检测失败，请检查配置';
    statusText.value = message;
    status.connected = false;
    stepStatuses.check_db = 'error';
    progressStatus.value = 'exception';
    ElMessage.error(message);
  } finally {
    testingConnection.value = false;
    syncProgressFromSteps();
  }
};

const handleSubmit = async () => {
  if (stepStatuses.check_db !== 'success') {
    ElMessage.error('请先通过数据库连接测试');
    return;
  }

  if (!form.mysqlHost && !form.serverDomain) {
    ElMessage.error('请填写 MySQL 主机或服务器域名');
    return;
  }

  if (!form.databaseName || !form.databaseUser || !form.databasePassword) {
    ElMessage.error('请填写数据库名称、业务账号与密码');
    return;
  }

  if (!form.adminUsername || !form.adminPassword) {
    ElMessage.error('请填写管理员账号与密码');
    return;
  }

  loading.value = true;
  statusText.value = '开始初始化数据库...';
  stepStatuses.fill_form = 'success';
  stepStatuses.initialize = 'process';
  progressStatus.value = '';
  syncProgressFromSteps();

  try {
    await http.post(API_ENDPOINTS.installDatabaseTest, {
      host: form.mysqlHost || form.serverDomain,
      port: form.mysqlPort,
      db_name: form.databaseName,
      db_user: form.databaseUser,
      db_password: form.databasePassword,
      root_password: form.mysqlRootPassword
    });

    await http.post(API_ENDPOINTS.adminDatabaseSeed, buildPayload());

    statusText.value = '初始化成功，正在跳转到后台登录...';
    markStepSuccess('initialize');
    stepStatuses.finish = 'success';
    progressStatus.value = 'success';
    syncProgressFromSteps();
    await router.push({ name: 'admin-login' });
  } catch (error: any) {
    const detail = error?.response?.data?.detail;
    const message = (typeof detail === 'object' && detail?.message) || detail || '初始化失败，请稍后重试';
    statusText.value = message;
    stepStatuses.initialize = 'error';
    progressStatus.value = 'exception';
    ElMessage.error(message);
    await ElMessageBox.alert(message, '初始化失败', { type: 'error' });
  } finally {
    loading.value = false;
    syncProgressFromSteps();
  }
};

const goToAdmin = async () => {
  resultDialog.value = false;
  await router.push({ name: 'admin-login' });
};
</script>

<style scoped>
.install-page {
  display: flex;
  justify-content: center;
  padding: 32px;
  background: #f5f5f5;
}

.install-card {
  max-width: 960px;
  width: 100%;
}

.install-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.subtitle {
  color: #606266;
  margin: 4px 0 0;
}

.form-tip {
  margin-top: 6px;
  font-size: 13px;
  color: #909399;
}

.mb-16 {
  margin-bottom: 16px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.inline-input {
  display: flex;
  gap: 8px;
}

.progress-text {
  color: #606266;
}

.progress-bar {
  margin-top: 8px;
}

.mt-8 {
  margin-top: 8px;
}
</style>
