<template>
  <div class="page">
    <el-page-header content="Checkout" />
    <el-card>
      <el-table :data="items" style="width: 100%">
        <el-table-column prop="name" label="Product" />
        <el-table-column prop="quantity" label="Qty" />
        <el-table-column label="Subtotal" :formatter="(_, __, row) => row.price * row.quantity" />
      </el-table>
      <div class="footer">
        <div>Total: {{ total }}</div>
        <el-button type="primary" :loading="loading" @click="pay">Pay</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useCartStore } from '@/store/cart';
import { callWechatPay, createWechatOrder } from '@/utils/wx';
import { ElMessage } from 'element-plus';

const cartStore = useCartStore();
const items = computed(() => cartStore.items);
const total = computed(() => cartStore.total);
const loading = ref(false);

const pollStatus = async (orderId: number) => {
  // placeholder polling logic
  console.log('polling order', orderId);
};

const pay = async () => {
  loading.value = true;
  try {
    const orderPayload = { items: cartStore.items.map(({ productId, quantity }) => ({ productId, quantity })) };
    const response = await createWechatOrder(orderPayload);
    await callWechatPay(response.prepayParams);
    ElMessage.success('Payment initiated, waiting for confirmation');
    await pollStatus(response.orderId);
  } catch (error) {
    console.error(error);
    ElMessage.error('Payment failed or cancelled');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.page {
  padding: 24px;
}
.footer {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
