<template>
  <div class="page">
    <el-page-header content="Home" />
    <el-card class="card">
      <h2>Welcome to the store</h2>
      <router-link :to="{ name: 'product-list' }">Browse products</router-link>
    </el-card>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.page {
  padding: 24px;
}
.card {
  margin-top: 12px;
}
</style>
