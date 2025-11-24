<template>
  <div class="page">
    <header class="page-head">
      <div>
        <h2>用户列表</h2>
        <p class="muted">支持按注册时间、等级、消费金额排序，点击可查看完整用户档案。</p>
      </div>
      <el-button type="primary" :icon="Sort" plain @click="resetSort">重置排序</el-button>
    </header>

    <el-card class="filters">
      <div class="left">
        <el-input v-model="keyword" placeholder="搜索手机号 / 昵称" clearable class="search" @input="handleSearch">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <div class="chips">
          <el-tag :type="sortKey === 'register_at' ? 'success' : 'info'" @click="setSort('register_at')">注册时间</el-tag>
          <el-tag :type="sortKey === 'level' ? 'success' : 'info'" @click="setSort('level')">用户等级</el-tag>
          <el-tag :type="sortKey === 'spend' ? 'success' : 'info'" @click="setSort('spend')">消费金额</el-tag>
        </div>
      </div>
      <div class="right">
        <span class="meta">共 {{ filteredUsers.length }} 人</span>
        <el-switch v-model="descending" active-text="倒序" inactive-text="正序" />
      </div>
    </el-card>

    <el-table
      :data="sortedUsers"
      style="width: 100%"
      stripe
      highlight-current-row
      v-loading="loading"
      :default-sort="{ prop: sortKey, order: descending ? 'descending' : 'ascending' }"
    >
      <el-table-column type="index" width="60" label="#" />
      <el-table-column prop="nickname" label="昵称" min-width="120" />
      <el-table-column prop="phone" label="手机号" min-width="140" />
      <el-table-column prop="level" label="等级" min-width="120" :sort-by="levelOrder" sortable>
        <template #default="{ row }">
          <el-tag :type="levelColor[row.level]">{{ row.level }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="register_at" label="注册时间" sortable min-width="180">
        <template #default="{ row }">
          <span>{{ formatDate(row.register_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="spend" label="消费金额" sortable min-width="120">
        <template #default="{ row }">
          <strong>¥{{ row.spend.toFixed(2) }}</strong>
        </template>
      </el-table-column>
      <el-table-column prop="tests" label="练习完成" min-width="120" />
      <el-table-column label="操作" width="140">
        <template #default="{ row }">
          <el-button type="primary" link @click="viewDetail(row)">查看详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-drawer v-model="detailVisible" size="520px" :title="activeUser?.nickname || '用户详情'">
      <el-descriptions v-if="activeUser" :column="1" border>
        <el-descriptions-item label="手机号">{{ activeUser.phone }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ formatDate(activeUser.register_at, true) }}</el-descriptions-item>
        <el-descriptions-item label="会员级别">
          <el-tag :type="levelColor[activeUser.level]">{{ activeUser.level }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="累计消费">¥{{ activeUser.spend.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="已完成练习">{{ activeUser.tests }}</el-descriptions-item>
        <el-descriptions-item label="剩余权益">{{ activeUser.benefits }}</el-descriptions-item>
        <el-descriptions-item label="充值记录">
          <ul class="recharge-list">
            <li v-for="(item, idx) in activeUser.recharges" :key="idx">{{ item }}</li>
          </ul>
        </el-descriptions-item>
        <el-descriptions-item label="备注">{{ activeUser.note }}</el-descriptions-item>
      </el-descriptions>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { Search, Sort } from '@element-plus/icons-vue';
import http from '@/utils/http';
import { API_ENDPOINTS } from '@/config/api';
import type { MemberLevel, UserProfile } from '@/types/admin';

const levelOrder: Record<MemberLevel, number> = {
  游客: 1,
  日卡: 2,
  月卡: 2,
  年卡: 3,
  终身: 4
};

const levelColor: Record<MemberLevel, 'info' | 'warning' | 'success' | 'danger'> = {
  游客: 'info',
  日卡: 'info',
  月卡: 'warning',
  年卡: 'success',
  终身: 'danger'
};

const users = ref<UserProfile[]>([]);
const loading = ref(false);

const keyword = ref('');
const sortKey = ref<'register_at' | 'level' | 'spend'>('register_at');
const descending = ref(true);
const detailVisible = ref(false);
const activeUser = ref<UserProfile | null>(null);

const filteredUsers = computed(() => {
  if (!keyword.value.trim()) return users.value;
  const word = keyword.value.trim();
  return users.value.filter((u) => u.phone.includes(word) || u.nickname.includes(word));
});

const sortedUsers = computed(() => {
  const list = [...filteredUsers.value];
  list.sort((a, b) => {
    if (sortKey.value === 'level') {
      return levelOrder[a.level] - levelOrder[b.level];
    }
    if (sortKey.value === 'spend') {
      return a.spend - b.spend;
    }
    return new Date(a.register_at).getTime() - new Date(b.register_at).getTime();
  });
  return descending.value ? list.reverse() : list;
});

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

const viewDetail = (row: UserProfile) => {
  activeUser.value = row;
  detailVisible.value = true;
};

const setSort = (key: typeof sortKey.value) => {
  if (sortKey.value === key) {
    descending.value = !descending.value;
  } else {
    sortKey.value = key;
    descending.value = true;
  }
};

const resetSort = () => {
  sortKey.value = 'register_at';
  descending.value = true;
};

const handleSearch = () => {
  // computed handles filtering, this exists to keep template event clean
};

const fetchUsers = async () => {
  loading.value = true;
  try {
    const { data } = await http.get<UserProfile[]>(API_ENDPOINTS.adminUsers);
    users.value = data;
  } finally {
    loading.value = false;
  }
};

onMounted(fetchUsers);
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

.filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters .left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.search {
  width: 260px;
}

.chips {
  display: flex;
  gap: 10px;
  align-items: center;
}

.right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.meta {
  color: #94a3b8;
}

.recharge-list {
  padding-left: 18px;
  margin: 0;
  display: grid;
  gap: 4px;
}
</style>
