<template>
  <div class="admin-layout">
    <aside>
      <div class="logo">后台控制台</div>
      <router-link :to="{ name: 'admin-dashboard' }">仪表盘</router-link>
      <router-link :to="{ name: 'admin-members' }">会员列表</router-link>
      <router-link :to="{ name: 'admin-payments' }">支付记录</router-link>
      <router-link :to="{ name: 'admin-settings' }">系统配置</router-link>
      <router-link :to="{ name: 'admin-courses' }">课程列表</router-link>
    </aside>
    <main>
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  min-height: 100vh;
}

aside {
  background: #0f172a;
  color: #fff;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 18px;
}

aside a {
  color: #cbd5e1;
  padding: 10px 12px;
  border-radius: 10px;
}

aside a.router-link-active {
  background: #1d293f;
  color: #fff;
}

.logo {
  font-weight: 800;
  margin-bottom: 10px;
}

main {
  padding: 18px;
  background: #f8fafc;
}
</style>
