<template>
  <div class="admin-layout">
    <aside>
      <div class="brand">
        <div class="logo">English Admin</div>
        <p class="desc">课程/用户/支付 全量配置</p>
      </div>
      <el-menu
        router
        :default-active="activePath"
        background-color="#0f172a"
        text-color="#cbd5e1"
        active-text-color="#fff"
      >
        <el-menu-item index="/admin">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据概览</span>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><UserFilled /></el-icon>
          <span>用户列表</span>
        </el-menu-item>
        <el-menu-item index="/admin/courses">
          <el-icon><Collection /></el-icon>
          <span>课程列表</span>
        </el-menu-item>
        <el-menu-item index="/admin/payments">
          <el-icon><CreditCard /></el-icon>
          <span>支付记录</span>
        </el-menu-item>
        <el-menu-item index="/admin/settings">
          <el-icon><Setting /></el-icon>
          <span>服务器配置</span>
        </el-menu-item>
      </el-menu>
      <div class="footer">
        <p>后台账号：admin@english</p>
        <p class="muted">仅内部维护可见</p>
      </div>
    </aside>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { Collection, CreditCard, DataAnalysis, Setting, UserFilled } from '@element-plus/icons-vue';

const route = useRoute();
const activePath = computed(() => route.path);
</script>

<style scoped>
.admin-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
  background: #0b1223;
}

aside {
  background: #0f172a;
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 18px 12px 10px;
  border-right: 1px solid #111827;
}

.brand {
  padding: 8px 12px 16px;
}

.logo {
  font-weight: 800;
  font-size: 18px;
}

.desc {
  margin: 6px 0 0;
  color: #9ca3af;
  font-size: 12px;
}

.footer {
  margin-top: auto;
  padding: 12px;
  color: #9ca3af;
  font-size: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.footer .muted {
  color: #6b7280;
  margin-top: 4px;
}

main {
  padding: 18px;
  background: #f8fafc;
}
</style>
