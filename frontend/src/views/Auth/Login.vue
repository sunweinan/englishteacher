<template>
  <div class="login-page">
    <div class="backdrop">
      <div class="logo">英语学习馆</div>
      <p>随时随地，手机验证码一键登录。</p>
    </div>
    <div class="panel">
      <div class="panel-inner">
        <h2>手机号验证码登录</h2>
        <p class="hint">PC 端以弹窗形式居中，移动端自动撑满屏幕。</p>
        <el-form @submit.prevent>
          <el-form-item label="手机号">
            <el-input v-model="form.phone" maxlength="11" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item label="验证码">
            <div class="code-row">
              <el-input v-model="form.code" maxlength="6" placeholder="输入短信验证码" />
              <el-button @click="sendCode" :disabled="countdown > 0">{{ buttonText }}</el-button>
            </div>
          </el-form-item>
          <el-button type="primary" class="submit" :loading="loading" @click="onSubmit">登录</el-button>
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
const form = reactive({ phone: '', code: '' });

const buttonText = computed(() => (countdown.value > 0 ? `${countdown.value}s` : '发送验证码'));

const sendCode = () => {
  if (!/^\d{11}$/.test(form.phone)) {
    ElMessage.error('请输入11位手机号');
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
  if (!form.phone || !form.code) {
    ElMessage.error('请输入手机号和验证码');
    return;
  }
  loading.value = true;
  try {
    userStore.loginWithCode(form.phone);
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
  grid-template-columns: minmax(240px, 1fr) 420px;
  background: linear-gradient(135deg, #0b1021 0%, #141a38 50%, #f5f7fb 50%, #ffffff 100%);
}

.backdrop {
  padding: 40px;
  color: #fff;
}

.backdrop .logo {
  font-size: 28px;
  font-weight: 800;
  margin-bottom: 8px;
}

.panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
}

.panel-inner {
  width: 100%;
  max-width: 420px;
  background: #fff;
  padding: 28px 24px;
  border-radius: 16px;
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.1);
}

.hint {
  color: #94a3b8;
  margin-bottom: 12px;
}

.code-row {
  display: flex;
  gap: 8px;
}

.submit {
  width: 100%;
}

@media (max-width: 900px) {
  .login-page {
    grid-template-columns: 1fr;
    background: #fff;
  }
  .backdrop {
    display: none;
  }
  .panel {
    padding: 12px;
  }
  .panel-inner {
    box-shadow: none;
  }
}
</style>
