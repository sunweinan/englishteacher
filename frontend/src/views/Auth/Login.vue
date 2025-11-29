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
        <p class="hint">短信登录更安全，登录后自动同步会员权益。</p>
        <el-form :model="form" label-position="top" class="form" @submit.prevent="onSubmit">
          <el-form-item label="手机号" class="field-block" @click="focusPhone">
            <div class="field-label">手机号</div>
            <div class="code-row">
              <el-input
                id="phone-input"
                ref="phoneInputRef"
                v-model="form.phone"
                type="tel"
                inputmode="tel"
                maxlength="20"
                clearable
                autocomplete="tel"
                placeholder="请输入手机号"
                class="control"
                @keyup.enter="onSubmit"
              />
              <el-button type="primary" class="code-btn" @click.stop="sendCode" :disabled="countdown > 0">
                {{ buttonText }}
              </el-button>
            </div>
          </el-form-item>
          <el-form-item label="验证码" class="field-block" @click="focusCode">
            <div class="field-label">验证码</div>
            <el-input
              id="code-input"
              ref="codeInputRef"
              v-model="form.code"
              maxlength="6"
              clearable
              autocomplete="one-time-code"
              placeholder="输入短信验证码"
              class="control"
              @keyup.enter="onSubmit"
            />
          </el-form-item>
          <el-button
            type="primary"
            class="submit"
            size="large"
            native-type="submit"
            :loading="loading"
            @click="onSubmit"
          >
            登录
          </el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onBeforeUnmount } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import type { InputInstance } from 'element-plus';
import { useUserStore } from '@/store/user';
import http from '@/utils/http';
import { API_ENDPOINTS } from '@/config/api';

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();
const loading = ref(false);
const countdown = ref(0);
const timer = ref<number | null>(null);
const form = reactive({ countryCode: '+86', phone: '', code: '' });
const phoneInputRef = ref<InputInstance>();
const codeInputRef = ref<InputInstance>();

const fullPhone = computed(() => `${form.countryCode}${form.phone}`.replace(/\D+/g, ''));
const buttonText = computed(() => (countdown.value > 0 ? `${countdown.value}s` : '获取验证码'));

const validatePhone = () => {
  const normalizedPhone = fullPhone.value;
  if (!/^\d{4,20}$/.test(normalizedPhone)) {
    ElMessage.error('请输入正确的手机号');
    return null;
  }
  return normalizedPhone;
};

const sendCode = async () => {
  const normalizedPhone = validatePhone();
  if (!normalizedPhone) return;
  try {
    const { data } = await http.post(API_ENDPOINTS.authSendCode, { phone: normalizedPhone });
    countdown.value = 60;
    timer.value = window.setInterval(() => {
      countdown.value -= 1;
      if (countdown.value <= 0 && timer.value) {
        window.clearInterval(timer.value);
        timer.value = null;
      }
    }, 1000);
    ElMessage.success(`验证码已发送${data.code ? `（演示码：${data.code}）` : ''}`);
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || error.message || '发送验证码失败');
  }
};

const onSubmit = async () => {
  const normalizedPhone = validatePhone();
  if (!normalizedPhone || !form.code) {
    ElMessage.error('请输入手机号和验证码');
    return;
  }
  loading.value = true;
  try {
    const newlyRegistered = await userStore.loginWithCode(normalizedPhone, form.code);
    ElMessage.success(newlyRegistered ? '注册成功，已为您登录' : '登录成功');
    const redirect = route.query.redirect as string | undefined;
    router.push(redirect || { name: 'home' });
  } catch (error: any) {
    const detail = error.response?.data?.detail || error.message;
    ElMessage.error(detail || '登录失败');
  } finally {
    loading.value = false;
  }
};

const focusPhone = () => phoneInputRef.value?.focus();
const focusCode = () => codeInputRef.value?.focus();

onBeforeUnmount(() => {
  if (timer.value) window.clearInterval(timer.value);
});
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  background: radial-gradient(circle at 20% 20%, rgba(34, 197, 94, 0.08), transparent 25%),
    radial-gradient(circle at 80% 0%, rgba(16, 185, 129, 0.08), transparent 20%),
    linear-gradient(180deg, #ffffff 0%, #f7f9fb 100%);
  color: #0f172a;
  font-family: 'Inter', 'Noto Sans SC', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
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
  padding: 32px 24px;
}

.panel-inner {
  width: 100%;
  max-width: 440px;
  background: #ffffff;
  padding: 28px 24px 26px;
  border-radius: 18px;
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.08);
  border: 1px solid #eef2f7;
}

.welcome {
  margin: 0 0 8px;
  color: #16a34a;
  font-weight: 700;
  letter-spacing: 0.4px;
}

.panel-inner h2 {
  margin: 0 0 6px;
  font-size: 22px;
}

.hint {
  color: #94a3b8;
  margin-bottom: 14px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field-block {
  margin-bottom: 6px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid transparent;
  background: #f8fafc;
  transition: all 0.2s ease;
  cursor: text;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-block:focus-within {
  border-color: #c7d2fe;
  box-shadow: 0 12px 30px rgba(99, 102, 241, 0.12);
  background: #ffffff;
}

.field-block :deep(.el-form-item__label) {
  display: none;
}

.field-label {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: 0.2px;
}

.control {
  flex: 1;
}

.control :deep(.el-input__wrapper) {
  border-radius: 14px;
  border: 1px solid #dfe7ef;
  box-shadow: none;
  padding-inline: 12px;
}

.code-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.code-btn {
  height: 44px;
  font-weight: 800;
  border-radius: 14px;
  padding: 0 14px;
  letter-spacing: 0.2px;
  box-shadow: 0 10px 24px rgba(34, 197, 94, 0.28);
  min-width: 96px;
  flex-shrink: 0;
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
  --el-button-text-color: #ffffff;
  --el-button-border-color: #22c55e;
  --el-button-hover-border-color: #16a34a;
  --el-button-hover-bg-color: #16a34a;
  background: linear-gradient(120deg, #34d399, #22c55e);
  border: none;
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
