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
        </el-form-item>
      </el-form>
    </el-card>

    <div class="actions">
      <el-button type="primary" @click="save">保存配置</el-button>
      <el-button plain @click="reset">重置未保存更改</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import http from '@/utils/http';
import { API_ENDPOINTS } from '@/config/api';

const defaultConfig = {
  serverIp: '10.10.10.8',
  domain: 'english.example.com',
  loginUser: 'root',
  loginPassword: 'Admin@123',
  dbHost: '127.0.0.1',
  dbPort: 3306,
  dbName: 'english_db',
  dbUser: 'english_user',
  dbPassword: 'db_pass_123',
  rootPassword: 'Ad123456'
};

const config = reactive({ ...defaultConfig });
const passwordForm = reactive({ old: '', new1: '', new2: '' });
const testing = ref(false);

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

  ElMessage.success('配置已同步到数据库（示例保存）');
  passwordForm.old = '';
  passwordForm.new1 = '';
  passwordForm.new2 = '';
};

const reset = () => {
  Object.assign(config, defaultConfig);
  passwordForm.old = '';
  passwordForm.new1 = '';
  passwordForm.new2 = '';
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
