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
const stats = [
  { label: '会员总数', value: '1,254', note: '含日卡、月卡、年卡、终身' },
  { label: '今日支付额', value: '¥3,280', note: '最近24小时微信支付' },
  { label: '课程数量', value: '128 组', note: '列表页展示的全部系列' },
  { label: '分享返佣', value: '¥860', note: '已累计发放' }
];
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
