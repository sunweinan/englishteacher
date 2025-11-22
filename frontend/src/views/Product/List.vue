<template>
  <div class="page">
    <el-page-header content="Products" />
    <el-table :data="products" style="width: 100%" @row-click="goDetail">
      <el-table-column prop="name" label="Name" />
      <el-table-column prop="price" label="Price" />
      <el-table-column prop="stock" label="Stock" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from '@/utils/http';

interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
}

const router = useRouter();
const products = ref<Product[]>([]);

const load = async () => {
  const { data } = await axios.get('/products');
  products.value = data.items || data;
};

const goDetail = (row: Product) => {
  router.push({ name: 'product-detail', params: { id: row.id } });
};

onMounted(load);
</script>

<style scoped>
.page {
  padding: 24px;
}
</style>
