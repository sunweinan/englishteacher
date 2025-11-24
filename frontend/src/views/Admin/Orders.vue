<template>
  <div class="page">
    <header class="page-head">
      <div>
        <h2>订单列表</h2>
        <p class="muted">展示预加载的示例订单，支持查看商品明细。</p>
      </div>
      <el-tag type="info">共 {{ orders.length }} 笔</el-tag>
    </header>

    <el-table :data="sortedOrders" style="width: 100%" stripe row-key="id">
      <el-table-column prop="id" label="订单号" min-width="160" />
      <el-table-column prop="user" label="用户" min-width="140" />
      <el-table-column prop="amount" label="订单金额" min-width="120">
        <template #default="{ row }">¥{{ row.amount.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="110">
        <template #default="{ row }">
          <el-tag :type="statusColor[row.status]">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="channel" label="渠道" min-width="120" />
      <el-table-column prop="createdAt" label="创建时间" min-width="180" sortable>
        <template #default="{ row }">{{ formatDate(row.createdAt) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" link @click="openDetail(row)">查看详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-drawer v-model="detailVisible" size="520px" :title="activeOrder ? `订单 ${activeOrder.id}` : '订单详情'">
      <template v-if="activeOrder">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户">{{ activeOrder.user }}</el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="statusColor[activeOrder.status]">{{ activeOrder.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="渠道">{{ activeOrder.channel }}</el-descriptions-item>
          <el-descriptions-item label="下单时间">{{ formatDate(activeOrder.createdAt, true) }}</el-descriptions-item>
          <el-descriptions-item label="订单金额">¥{{ activeOrder.amount.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="备注" v-if="activeOrder.remark">{{ activeOrder.remark }}</el-descriptions-item>
        </el-descriptions>

        <h4 class="mt-12">商品明细</h4>
        <el-table :data="activeOrder.items" border size="small" class="item-table">
          <el-table-column prop="name" label="名称" min-width="180" />
          <el-table-column prop="quantity" label="数量" width="120" />
          <el-table-column prop="price" label="单价" width="120">
            <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="小计" width="120">
            <template #default="{ row }">¥{{ (row.price * row.quantity).toFixed(2) }}</template>
          </el-table-column>
        </el-table>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { adminPreloadData, type OrderInfo, type OrderStatus } from '@/config/adminPreload';

const statusColor: Record<OrderStatus, 'info' | 'success' | 'danger'> = {
  待支付: 'info',
  已支付: 'success',
  已退款: 'danger'
};

const orders = ref<OrderInfo[]>([...adminPreloadData.orders]);
const detailVisible = ref(false);
const activeOrder = ref<OrderInfo | null>(null);

const sortedOrders = computed(() =>
  [...orders.value].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
);

const formatDate = (val: string, includeTime = false) => {
  const date = new Date(val);
  const yyyy = date.getFullYear();
  const mm = `${date.getMonth() + 1}`.padStart(2, '0');
  const dd = `${date.getDate()}`.padStart(2, '0');
  const base = `${yyyy}-${mm}-${dd}`;
  if (!includeTime) return base;
  const hh = `${date.getHours()}`.padStart(2, '0');
  const mi = `${date.getMinutes()}`.padStart(2, '0');
  return `${base} ${hh}:${mi}`;
};

const openDetail = (order: OrderInfo) => {
  activeOrder.value = order;
  detailVisible.value = true;
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

.page-head h2 {
  margin: 0 0 4px;
}

.muted {
  color: #94a3b8;
  margin: 0;
}

.mt-12 {
  margin-top: 12px;
}

.item-table {
  margin-top: 8px;
}
</style>
