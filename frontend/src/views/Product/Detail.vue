<template>
  <div class="page" v-if="product">
    <el-page-header :content="product.name" @back="() => router.back()" />
    <el-card class="card">
      <p>{{ product.description }}</p>
      <p>Price: {{ product.price }}</p>
      <p>Stock: {{ product.stock }}</p>
      <el-button type="primary" @click="add">Add to cart</el-button>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from '@/utils/http';
import { API_ENDPOINTS } from '@/config/api';
import { useCartStore } from '@/store/cart';

interface ProductDetail {
  id: number;
  name: string;
  description: string;
  price: number;
  stock: number;
}

const route = useRoute();
const router = useRouter();
const cartStore = useCartStore();
const product = ref<ProductDetail | null>(null);

const load = async () => {
  const { data } = await axios.get(API_ENDPOINTS.productDetail(route.params.id as string));
  product.value = data;
};

const add = () => {
  if (!product.value) return;
  cartStore.addItem({
    productId: product.value.id,
    name: product.value.name,
    price: product.value.price,
    quantity: 1
  });
  router.push({ name: 'checkout' });
};

onMounted(load);
</script>

<style scoped>
.page {
  padding: 24px;
}
.card {
  margin-top: 12px;
}
</style>
