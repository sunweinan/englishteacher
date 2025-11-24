<template>
  <div class="admin-login">
    <div class="panel">
      <div class="title">enTeacher管理后台</div>
      <p class="subtitle">请输入后台账号和密码</p>
      <el-form label-position="top" :model="form" class="form" @submit.prevent="onSubmit">
        <el-form-item label="账号">
          <el-input
            v-model="form.username"
            placeholder="root"
            autocomplete="username"
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            autocomplete="current-password"
            show-password
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-button type="primary" class="submit" size="large" :loading="loading" @click="onSubmit">
          确定
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useAdminAuthStore } from '@/store/adminAuth';

const form = reactive({ username: 'root', password: '' });
const loading = ref(false);
const router = useRouter();
const route = useRoute();
const adminStore = useAdminAuthStore();

const onSubmit = async () => {
  if (!form.username || !form.password) {
    ElMessage.error('请输入账号和密码');
    return;
  }
  loading.value = true;
  try {
    await adminStore.login(form.username, form.password);
    ElMessage.success('登录成功');
    const redirect = route.query.redirect as string | undefined;
    router.push(redirect || '/admin');
  } catch (error: any) {
    const message = error?.response?.data?.detail || error.message || '登录失败，请稍后重试';
    ElMessage.error(message);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.admin-login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0ea5e9 0%, #10b981 100%);
  padding: 20px;
}

.panel {
  width: 100%;
  max-width: 420px;
  background: #ffffff;
  padding: 28px 26px 30px;
  border-radius: 16px;
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.title {
  font-size: 22px;
  font-weight: 800;
  color: #0f172a;
}

.subtitle {
  margin: 8px 0 20px;
  color: #64748b;
}

.form {
  text-align: left;
}

.submit {
  width: 100%;
  margin-top: 6px;
}
</style>
