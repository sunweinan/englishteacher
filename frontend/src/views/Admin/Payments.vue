<template>
  <div class="page">
    <header class="page-head">
      <div>
        <h2>支付记录</h2>
        <p class="tip">按时间倒序展示，覆盖时间、用户名、金额、升级等级、微信支付单号。</p>
      </div>
      <el-tag type="info">最近 {{ payments.length }} 条</el-tag>
    </header>

    <el-table :data="sortedPayments" style="width: 100%" stripe row-key="orderNo">
      <el-table-column prop="time" label="时间" min-width="180" sortable>
        <template #default="{ row }">{{ formatDate(row.time) }}</template>
      </el-table-column>
      <el-table-column prop="user" label="用户名" min-width="140" />
      <el-table-column prop="amount" label="支付金额" min-width="120">
        <template #default="{ row }">¥{{ row.amount.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="level" label="取得等级" min-width="120">
        <template #default="{ row }">
          <el-tag :type="levelColor[row.level]">{{ row.level }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="channel" label="渠道" min-width="120" />
      <el-table-column prop="orderNo" label="微信支付单号" min-width="200" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { adminPreloadData, type MemberLevel, type PaymentRecord } from '@/config/adminPreload';

const levelColor: Record<MemberLevel, 'success' | 'warning' | 'info' | 'danger'> = {
  游客: 'info',
  日卡: 'info',
  月卡: 'warning',
  年卡: 'success',
  终身: 'danger'
};

const payments: PaymentRecord[] = adminPreloadData.payments;

const sortedPayments = computed(() => [...payments].sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime()));

const formatDate = (val: string) => {
  const date = new Date(val);
  const yyyy = date.getFullYear();
  const mm = `${date.getMonth() + 1}`.padStart(2, '0');
  const dd = `${date.getDate()}`.padStart(2, '0');
  const hh = `${date.getHours()}`.padStart(2, '0');
  const mi = `${date.getMinutes()}`.padStart(2, '0');
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}`;
};
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.page-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tip {
  color: #94a3b8;
  margin: 4px 0 0;
}
</style>
