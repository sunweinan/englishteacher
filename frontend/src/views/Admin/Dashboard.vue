<template>
  <div>
    <h2>数据总览</h2>
    <div class="stats">
      <el-card v-for="stat in stats" :key="stat.label">
        <div class="label">{{ stat.label }}</div>
        <div class="value">{{ stat.value }}</div>
        <p class="note">{{ stat.note }}</p>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { adminPreloadData } from '@/config/adminPreload';

const stats = adminPreloadData.dashboardStats;
</script>

<style scoped>
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.label {
  color: #475569;
}

.value {
  font-size: 26px;
  font-weight: 800;
}

.note {
  color: #94a3b8;
  margin: 6px 0 0;
}
</style>
