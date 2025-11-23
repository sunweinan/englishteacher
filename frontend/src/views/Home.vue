<template>
  <div class="home-page">
    <header class="hero">
      <div class="brand">英语学习馆</div>
      <div class="search">
        <el-input v-model="keyword" placeholder="搜索课程、场景或标签" clearable @input="filterCourses">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="auth">
        <el-button v-if="!userStore.isAuthenticated" type="primary" @click="goLogin">登录</el-button>
        <el-dropdown v-else>
          <span class="user-chip">
            <el-tag type="success" size="small" effect="dark">{{ userStore.isMember ? '会员' : '游客' }}</el-tag>
            <span class="phone">{{ userStore.maskedPhone }}</span>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="goMember">会员中心</el-dropdown-item>
              <el-dropdown-item @click="userStore.logout">退出</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <section class="banner">
      <div class="text">
        <p class="eyebrow">LIST / PLAYGROUND / VIP</p>
        <h1>场景化英语 · 大图沉浸式体验</h1>
        <p class="desc">手机两列瀑布流、PC多列影院式海报，滑到底自动收住。</p>
        <div class="actions">
          <el-button type="primary" @click="goPlayground">立即开练</el-button>
          <el-button @click="goMember">会员特权</el-button>
        </div>
      </div>
      <div class="poster">
        <img src="https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=900&q=80" alt="learning" />
      </div>
    </section>

    <section class="list" ref="listRef">
      <div
        v-for="course in visibleCourses"
        :key="course.id"
        class="card"
      >
        <div class="thumb">
          <img :src="course.image" :alt="course.title" />
          <span class="tag">{{ course.tag }}</span>
        </div>
        <div class="info">
          <h3>{{ course.title }}</h3>
          <p>{{ course.subtitle }}</p>
          <div class="card-actions">
            <el-button type="primary" @click="goPlayground(course.id)">进入学习</el-button>
          </div>
        </div>
      </div>
    </section>

    <div class="load-status">
      <el-icon v-if="loading"><Loading /></el-icon>
      <span v-else-if="!hasMore">没有更多内容</span>
      <span v-else>下滑加载更多</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { Search, Loading } from '@element-plus/icons-vue';
import { courseCards, type CourseCard } from '@/config/courses';
import { useUserStore } from '@/store/user';

const router = useRouter();
const userStore = useUserStore();
const keyword = ref('');
const listRef = ref<HTMLElement | null>(null);
const loading = ref(false);
const page = ref(0);
const pageSize = 6;
const visibleCourses = ref<CourseCard[]>([]);
const filteredCourses = ref<CourseCard[]>(courseCards);
const hasMore = ref(true);

const goLogin = () => router.push({ name: 'login' });
const goPlayground = (courseId?: number) => router.push({ name: 'playground', query: courseId ? { courseId } : {} });
const goMember = () => router.push({ name: 'member-center' });

const filterCourses = () => {
  const word = keyword.value.trim().toLowerCase();
  if (!word) {
    filteredCourses.value = courseCards;
  } else {
    filteredCourses.value = courseCards.filter(
      (item) =>
        item.title.toLowerCase().includes(word) ||
        item.subtitle.toLowerCase().includes(word) ||
        item.tag.toLowerCase().includes(word)
    );
  }
  resetAndLoad();
};

const resetAndLoad = () => {
  page.value = 0;
  visibleCourses.value = [];
  hasMore.value = true;
  loadMore();
};

const loadMore = () => {
  if (loading.value || !hasMore.value) return;
  loading.value = true;
  const start = page.value * pageSize;
  const next = filteredCourses.value.slice(start, start + pageSize);
  visibleCourses.value = [...visibleCourses.value, ...next];
  page.value += 1;
  if (visibleCourses.value.length >= filteredCourses.value.length) {
    hasMore.value = false;
  }
  loading.value = false;
};

const handleScroll = () => {
  if (!listRef.value) return;
  const { bottom } = listRef.value.getBoundingClientRect();
  if (bottom < window.innerHeight + 200) {
    loadMore();
  }
};

onMounted(() => {
  resetAndLoad();
  window.addEventListener('scroll', handleScroll, { passive: true });
});

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f7f8fb 0%, #ffffff 45%, #f5f7fb 100%);
  color: #1c1f2b;
}

.hero {
  position: sticky;
  top: 0;
  z-index: 10;
  display: grid;
  grid-template-columns: 180px 1fr 200px;
  gap: 16px;
  align-items: center;
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid #eef0f5;
}

.brand {
  font-weight: 800;
  font-size: 20px;
}

.search :deep(.el-input__wrapper) {
  border-radius: 999px;
  box-shadow: none;
}

.auth {
  display: flex;
  justify-content: flex-end;
}

.user-chip {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  cursor: pointer;
  color: #1c1f2b;
}

.phone {
  font-weight: 600;
}

.banner {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  padding: 32px 24px 8px;
  align-items: center;
}

.banner .text h1 {
  margin: 6px 0 8px;
}

.banner .text .desc {
  color: #64748b;
  margin-bottom: 12px;
}

.banner .eyebrow {
  font-size: 12px;
  letter-spacing: 3px;
  color: #a855f7;
  font-weight: 700;
}

.banner .poster img {
  width: 100%;
  border-radius: 18px;
  object-fit: cover;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.08);
}

.actions {
  display: flex;
  gap: 12px;
}

.list {
  padding: 12px 16px 24px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.08);
}

.thumb {
  position: relative;
  height: 170px;
  overflow: hidden;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.tag {
  position: absolute;
  left: 12px;
  bottom: 12px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
}

.info {
  padding: 12px 14px 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info h3 {
  margin: 0;
}

.info p {
  margin: 0;
  color: #475569;
  min-height: 42px;
}

.card-actions {
  margin-top: auto;
}

.load-status {
  text-align: center;
  padding: 12px 0 24px;
  color: #94a3b8;
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(3, auto);
    gap: 10px;
  }
  .auth {
    justify-content: flex-start;
  }
  .list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }
  .thumb {
    height: 190px;
  }
}
</style>
