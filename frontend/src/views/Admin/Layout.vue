<template>
  <div class="admin-layout">
    <aside>
      <router-link :to="{ name: 'admin-home' }">Dashboard</router-link>
      <router-link :to="{ name: 'admin-users' }">Users</router-link>
      <router-link :to="{ name: 'admin-products' }">Products</router-link>
      <router-link :to="{ name: 'admin-orders' }">Orders</router-link>
    </aside>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.admin-layout {
  display: grid;
  grid-template-columns: 200px 1fr;
  min-height: 100vh;
}
aside {
  background: #1f2d3d;
  color: #fff;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
}
aside a {
  color: #fff;
}
main {
  padding: 16px;
}
</style>
