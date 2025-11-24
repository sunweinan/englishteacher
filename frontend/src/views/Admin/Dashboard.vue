<template>
  <div>
    <h2>数据总览</h2>
    <div class="stats" v-loading="loading">
      <el-card v-for="stat in stats" :key="stat.label">
        <div class="label">{{ stat.label }}</div>
        <div class="value">{{ stat.value }}</div>
        <p class="note">{{ stat.note }}</p>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import http from '@/utils/http';
import { API_ENDPOINTS } from '@/config/api';
import type { DashboardStat } from '@/types/admin';

const stats = ref<DashboardStat[]>([]);
const loading = ref(false);

const fetchStats = async () => {
  loading.value = true;
  try {
    const { data } = await http.get<DashboardStat[]>(API_ENDPOINTS.adminDashboard);
    stats.value = data;
  } finally {
    loading.value = false;
  }
};

onMounted(fetchStats);
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
