<template>
  <div class="page">
    <h2>服务器配置</h2>
    <p class="muted">联动数据库内容，可修改服务器连接、域名、数据库以及后台密码。</p>

    <el-card class="card">
      <h4>基础信息</h4>
      <el-form label-width="140px" class="form">
        <el-form-item label="服务器 IP">
          <el-input v-model="config.serverIp" placeholder="10.0.0.2" />
        </el-form-item>
        <el-form-item label="域名">
          <el-input v-model="config.domain" placeholder="english.example.com" />
        </el-form-item>
        <el-form-item label="登录用户名">
          <el-input v-model="config.loginUser" placeholder="root" />
        </el-form-item>
        <el-form-item label="登录密码">
          <el-input v-model="passwordForm.old" type="password" placeholder="请输入原密码以修改" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.new1" type="password" placeholder="输入新密码" />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="passwordForm.new2" type="password" placeholder="再次输入新密码" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="card">
      <h4>数据库配置</h4>
      <el-form label-width="140px" class="form">
        <el-form-item label="数据库地址">
          <el-input v-model="config.dbHost" placeholder="127.0.0.1" />
        </el-form-item>
        <el-form-item label="数据库端口">
          <el-input v-model.number="config.dbPort" type="number" placeholder="3306" />
        </el-form-item>
        <el-form-item label="数据库名称">
          <el-input v-model="config.dbName" placeholder="english_db" />
        </el-form-item>
        <el-form-item label="数据库账号">
          <el-input v-model="config.dbUser" placeholder="db_user" />
        </el-form-item>
        <el-form-item label="数据库密码">
          <el-input v-model="config.dbPassword" type="password" placeholder="请输入数据库密码" />
        </el-form-item>
        <el-form-item label="默认 root 密码">
          <el-input v-model="config.rootPassword" type="password" placeholder="用于校验数据库 root 连接" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="testing" @click="testDatabase">检测数据库连接</el-button>
          <el-button type="primary" plain :loading="seeding" style="margin-left: 12px" @click="initializeDatabase">初始化数据库</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="card">
      <h4>微信支付配置</h4>
      <el-form label-width="140px" class="form">
        <el-form-item label="微信支付 AppID">
          <el-input v-model="config.wechatAppId" placeholder="wx1234567890" />
        </el-form-item>
        <el-form-item label="微信商户号">
          <el-input v-model="config.wechatMchId" placeholder="1234567890" />
        </el-form-item>
        <el-form-item label="微信 API Key">
          <el-input v-model="config.wechatApiKey" placeholder="填写商户平台设置的 Key" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="card">
      <h4>短信服务配置</h4>
      <el-form label-width="140px" class="form">
        <el-form-item label="短信服务商">
          <el-input v-model="config.smsProvider" placeholder="如 aliyun、tencent" />
        </el-form-item>
        <el-form-item label="短信 API Key">
          <el-input v-model="config.smsApiKey" placeholder="短信平台 Access Key" />
        </el-form-item>
        <el-form-item label="短信签名">
          <el-input v-model="config.smsSignName" placeholder="短信签名内容" />
        </el-form-item>
      </el-form>
    </el-card>

    <div class="actions">
      <el-button type="primary" @click="save">保存配置</el-button>
      <el-button plain @click="reset">重置未保存更改</el-button>
    </div>

    <el-dialog v-model="permissionDialog.visible" title="缺少写入权限" width="520px">
      <p>{{ permissionDialog.message }}</p>
      <p class="mt-8">请在服务器终端执行以下命令后重试：</p>
      <el-alert
        type="info"
        :closable="false"
        show-icon
        class="mt-8"
        :title="permissionDialog.command"
      />
      <p v-if="permissionDialog.path" class="mt-8">受影响的路径：{{ permissionDialog.path }}</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="permissionDialog.visible = false">知道了</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import http from '@/utils/http';
import { API_ENDPOINTS } from '@/config/api';

const defaultConfig = {
  serverIp: '',
  domain: '',
  loginUser: '',
  loginPassword: '',
  dbHost: '',
  dbPort: 3306,
  dbName: '',
  dbUser: '',
  dbPassword: '',
  rootPassword: '',
  wechatAppId: '',
  wechatMchId: '',
  wechatApiKey: '',
  smsProvider: '',
  smsApiKey: '',
  smsSignName: ''
};

const config = reactive({ ...defaultConfig });
const passwordForm = reactive({ old: '', new1: '', new2: '' });
const testing = ref(false);
const seeding = ref(false);
const loading = ref(false);
const permissionDialog = reactive({
  visible: false,
  message: '',
  command: 'chmod -R 775 backend/app/install',
  path: ''
});

const showPermissionDialog = (detail: any) => {
  permissionDialog.message = detail?.message || '写入配置文件失败，请检查文件权限。';
  permissionDialog.command = detail?.command || permissionDialog.command;
  permissionDialog.path = detail?.path || '';
  permissionDialog.visible = true;
};

const applyConfig = (data: Record<string, any>) => {
  const merged = { ...defaultConfig };
  merged.serverIp = data.server_ip ?? data.serverIp ?? merged.serverIp;
  merged.domain = data.domain ?? merged.domain;
  merged.loginUser = data.login_user ?? data.loginUser ?? merged.loginUser;
  merged.loginPassword = data.login_password ?? data.loginPassword ?? merged.loginPassword;
  merged.dbHost = data.db_host ?? data.dbHost ?? merged.dbHost;
  merged.dbPort = data.db_port ?? data.dbPort ?? merged.dbPort;
  merged.dbName = data.db_name ?? data.dbName ?? merged.dbName;
  merged.dbUser = data.db_user ?? data.dbUser ?? merged.dbUser;
  merged.dbPassword = data.db_password ?? data.dbPassword ?? merged.dbPassword;
  merged.rootPassword = data.root_password ?? data.rootPassword ?? merged.rootPassword;
  merged.wechatAppId = data.wechat_app_id ?? data.wechatAppId ?? merged.wechatAppId;
  merged.wechatMchId = data.wechat_mch_id ?? data.wechatMchId ?? merged.wechatMchId;
  merged.wechatApiKey = data.wechat_api_key ?? data.wechatApiKey ?? merged.wechatApiKey;
  merged.smsProvider = data.sms_provider ?? data.smsProvider ?? merged.smsProvider;
  merged.smsApiKey = data.sms_api_key ?? data.smsApiKey ?? merged.smsApiKey;
  merged.smsSignName = data.sms_sign_name ?? data.smsSignName ?? merged.smsSignName;
  Object.assign(config, merged);
};

const fetchConfig = async () => {
  loading.value = true;
  try {
    const response = await http.get(API_ENDPOINTS.adminConfig);
    applyConfig(response.data || {});
  } catch (error) {
    console.warn('Failed to load config, using defaults', error);
    applyConfig(defaultConfig);
  } finally {
    loading.value = false;
    passwordForm.old = '';
    passwordForm.new1 = '';
    passwordForm.new2 = '';
  }
};

const save = () => {
  if (passwordForm.new1 || passwordForm.new2 || passwordForm.old) {
    if (passwordForm.old !== config.loginPassword) {
      ElMessage.error('原密码校验失败，无法更新登录密码');
      return;
    }
    if (passwordForm.new1 !== passwordForm.new2) {
      ElMessage.error('两次输入的新密码不一致');
      return;
    }
    if (passwordForm.new1) {
      config.loginPassword = passwordForm.new1;
    }
  }

  loading.value = true;
  http
    .put(API_ENDPOINTS.adminConfig, {
      server_ip: config.serverIp,
      domain: config.domain,
      login_user: config.loginUser,
      login_password: config.loginPassword,
      db_host: config.dbHost,
      db_port: config.dbPort,
      db_name: config.dbName,
      db_user: config.dbUser,
      db_password: config.dbPassword,
      root_password: config.rootPassword,
      wechat_app_id: config.wechatAppId,
      wechat_mch_id: config.wechatMchId,
      wechat_api_key: config.wechatApiKey,
      sms_provider: config.smsProvider,
      sms_api_key: config.smsApiKey,
      sms_sign_name: config.smsSignName
    })
    .then((response) => {
      applyConfig(response.data || {});
      ElMessage.success('配置已同步到数据库');
    })
    .catch((error) => {
      console.error(error);
      const detail = error?.response?.data?.detail;
      if (detail?.code === 'SEED_DATA_PERMISSION_DENIED' || detail?.code === 'INSTALL_STATE_PERMISSION_DENIED') {
        showPermissionDialog(detail);
        return;
      }
      ElMessage.error(detail?.message || '保存配置失败，请稍后重试');
    })
    .finally(() => {
      loading.value = false;
      passwordForm.old = '';
      passwordForm.new1 = '';
      passwordForm.new2 = '';
    });
};

const reset = () => {
  fetchConfig();
};

const testDatabase = async () => {
  if (!config.dbHost || !config.dbUser || !config.dbName || !config.dbPassword) {
    ElMessage.error('请先填写数据库的地址、账号、名称和密码');
    return;
  }
  if (!config.rootPassword) {
    ElMessage.error('请填写默认 root 密码');
    return;
  }

  testing.value = true;
  try {
    const response = await http.post(API_ENDPOINTS.adminDatabaseTest, {
      host: config.dbHost,
      port: config.dbPort,
      db_name: config.dbName,
      db_user: config.dbUser,
      db_password: config.dbPassword,
      root_password: config.rootPassword
    });
    ElMessage.success(response.data?.message || '数据库连接成功');
  } catch (error: any) {
    const message = error?.response?.data?.detail || '数据库连接检测失败，请检查配置';
    ElMessage.error(message);
  } finally {
    testing.value = false;
  }
};

const initializeDatabase = async () => {
  seeding.value = true;
  try {
    const response = await http.post(API_ENDPOINTS.adminDatabaseSeed);
    ElMessage.success(response.data?.message || '数据库初始化成功');
  } catch (error: any) {
    const message = error?.response?.data?.detail || '数据库初始化失败，请检查配置';
    ElMessage.error(message);
  } finally {
    seeding.value = false;
  }
};

onMounted(() => {
  fetchConfig();
});
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.muted {
  color: #94a3b8;
  margin: 4px 0 0;
}

.card {
  padding: 12px;
}

.form {
  max-width: 620px;
  margin-top: 10px;
}

.actions {
  display: flex;
  gap: 10px;
}
</style>
