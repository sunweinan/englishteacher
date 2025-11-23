<template>
  <div>
    <h2>系统配置</h2>
    <el-form label-width="140px" class="form">
      <el-form-item label="系统域名 / IP">
        <el-input v-model="form.domain" placeholder="https://english.example.com" />
      </el-form-item>
      <el-form-item label="微信支付 Key">
        <el-input v-model="form.wechatKey" placeholder="填写微信支付商户 Key" />
      </el-form-item>
      <el-form-item label="回调地址">
        <el-input v-model="form.callback" placeholder="https://english.example.com/pay/callback" />
      </el-form-item>
      <el-button type="primary" @click="save">保存配置</el-button>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import { ElMessage } from 'element-plus';

const form = reactive({
  domain: 'https://english.example.com',
  wechatKey: '请在此粘贴真实微信支付Key',
  callback: 'https://english.example.com/pay/callback'
});

const save = () => {
  ElMessage.success('配置已保存（示例）');
};
</script>

<style scoped>
.form {
  max-width: 520px;
  margin-top: 12px;
}
</style>
