<template>
  <div class="auth">
    <el-card class="box-card">
      <h2>Login</h2>
      <el-form :model="form" @submit.prevent>
        <el-form-item label="Username">
          <el-input v-model="form.username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="form.password" type="password" autocomplete="current-password" />
        </el-form-item>
        <el-button type="primary" :loading="loading" @click="onSubmit">Login</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/store/user';

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();
const loading = ref(false);
const form = reactive({ username: '', password: '' });

const onSubmit = async () => {
  loading.value = true;
  try {
    await userStore.login(form.username, form.password);
    ElMessage.success('Logged in');
    const redirect = route.query.redirect as string | undefined;
    router.push(redirect || { name: 'home' });
  } catch (error) {
    console.error(error);
    ElMessage.error('Login failed');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth {
  max-width: 400px;
  margin: 80px auto;
}
</style>
