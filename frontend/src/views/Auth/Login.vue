<template>
  <div class="login-page">
    <div class="backdrop">
      <div class="logo">enTeacher</div>
      <p>随时随地，手机验证码一键登录。</p>
    </div>
    <div class="panel">
      <div class="panel-inner">
        <p class="welcome">欢迎使用 enTeacher</p>
        <h2>手机号验证码登录</h2>
        <p class="hint">PC 端以弹窗形式居中，移动端自动撑满屏幕。</p>
        <el-form :model="form" label-position="top" class="form" @submit.prevent>
          <el-form-item label="手机号" class="field-block">
            <el-input
              v-model="form.phone"
              type="tel"
              maxlength="20"
              clearable
              placeholder="请输入手机号"
              class="control"
            >
              <template #prepend>
                <el-select v-model="form.countryCode" class="code-select">
                  <el-option label="中国 +86" value="+86" />
                  <el-option label="美国 +1" value="+1" />
                  <el-option label="日本 +81" value="+81" />
                </el-select>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="验证码" class="field-block">
            <div class="code-row">
              <el-input
                v-model="form.code"
                maxlength="6"
                clearable
                placeholder="输入短信验证码"
                class="control"
              />
              <el-button type="success" plain class="code-btn" @click="sendCode" :disabled="countdown > 0">
                {{ buttonText }}
              </el-button>
            </div>
          </el-form-item>
          <el-button type="primary" class="submit" size="large" :loading="loading" @click="onSubmit">登录</el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onBeforeUnmount } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/store/user';

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();
const loading = ref(false);
const countdown = ref(0);
const timer = ref<number | null>(null);
const form = reactive({ countryCode: '+86', phone: '', code: '' });

const buttonText = computed(() => (countdown.value > 0 ? `${countdown.value}s` : '发送验证码'));

const sendCode = () => {
  const normalizedPhone = form.phone.replace(/\s+/g, '');
  if (!/^\d{4,20}$/.test(normalizedPhone)) {
    ElMessage.error('请输入正确的手机号');
    return;
  }
  countdown.value = 60;
  timer.value = window.setInterval(() => {
    countdown.value -= 1;
    if (countdown.value <= 0 && timer.value) {
      window.clearInterval(timer.value);
    }
  }, 1000);
  ElMessage.success('验证码已发送（示例）');
};

const onSubmit = async () => {
  const normalizedPhone = form.phone.replace(/\s+/g, '');
  if (!normalizedPhone || !form.code) {
    ElMessage.error('请输入手机号和验证码');
    return;
  }
  loading.value = true;
  try {
    userStore.loginWithCode(`${form.countryCode}-${normalizedPhone}`);
    ElMessage.success('登录成功');
    const redirect = route.query.redirect as string | undefined;
    router.push(redirect || { name: 'home' });
  } catch (error: any) {
    ElMessage.error(error.message || '登录失败');
  } finally {
    loading.value = false;
  }
};

onBeforeUnmount(() => {
  if (timer.value) window.clearInterval(timer.value);
});
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  background: radial-gradient(circle at 20% 20%, rgba(34, 197, 94, 0.08), transparent 25%),
    radial-gradient(circle at 80% 0%, rgba(16, 185, 129, 0.08), transparent 20%),
    linear-gradient(180deg, #ffffff 0%, #f7f9fb 100%);
  color: #0f172a;
}

.backdrop {
  padding: 72px 56px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  justify-content: center;
}

.backdrop .logo {
  font-size: 32px;
  font-weight: 800;
  color: #0f172a;
}

.backdrop p {
  color: #475569;
  margin: 0;
}

.panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 32px;
}

.panel-inner {
  width: 100%;
  max-width: 440px;
  background: #ffffff;
  padding: 32px 28px;
  border-radius: 18px;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.1);
  border: 1px solid #eef2f7;
}

.welcome {
  margin: 0 0 8px;
  color: #16a34a;
  font-weight: 700;
  letter-spacing: 0.4px;
}

.hint {
  color: #94a3b8;
  margin-bottom: 12px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-block {
  margin-bottom: 4px;
}

.control :deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: none;
  padding-inline: 10px;
}

.code-row {
  display: flex;
  gap: 8px;
}

.code-select {
  width: 120px;
}

.code-btn {
  height: 40px;
  font-weight: 700;
  border-radius: 12px;
}

.submit {
  width: 100%;
  --el-button-bg-color: #22c55e;
  --el-button-border-color: #22c55e;
  --el-button-hover-bg-color: #16a34a;
  --el-button-hover-border-color: #16a34a;
  color: #fff;
  font-weight: 700;
  box-shadow: 0 12px 28px rgba(34, 197, 94, 0.24);
}

.code-row :deep(.el-button) {
  --el-button-text-color: #16a34a;
  --el-button-border-color: #a7f3d0;
  --el-button-hover-border-color: #22c55e;
  color: #16a34a;
}

@media (max-width: 900px) {
  .login-page {
    grid-template-columns: 1fr;
    background: #ffffff;
  }
  .backdrop {
    display: none;
  }
  .panel {
    padding: 16px 12px 28px;
  }
  .panel-inner {
    box-shadow: none;
    border: 1px solid #e2e8f0;
  }
}
</style>
