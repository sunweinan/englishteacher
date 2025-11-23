<template>
  <div>
    <h2>支付记录</h2>
    <p class="tip">按时间倒序，最近支付在上方。</p>
    <el-table :data="payments" style="width: 100%" stripe>
      <el-table-column prop="time" label="时间" width="180" />
      <el-table-column prop="user" label="用户" />
      <el-table-column prop="plan" label="会员类型" />
      <el-table-column prop="amount" label="金额" />
      <el-table-column prop="channel" label="渠道" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
const payments = [
  { time: '2024-04-08 10:28', user: '138****8888', plan: '年卡', amount: '¥30', channel: '微信支付' },
  { time: '2024-04-07 22:10', user: '139****5566', plan: '月卡', amount: '¥10', channel: '微信支付' },
  { time: '2024-04-07 12:02', user: '137****1020', plan: '终身', amount: '¥40', channel: '微信支付' }
];
</script>

<style scoped>
.tip {
  color: #94a3b8;
  margin-bottom: 8px;
}
</style>
