<template>
  <div class="home-page">
    <header class="hero">
      <div class="brand">enTeacher</div>
      <div class="search">
        <el-input v-model="keyword" placeholder="搜索课程、场景或标签" clearable @input="filterCourses">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="auth">
        <el-button
          class="admin-btn"
          plain
          size="large"
          :title="`进入后台：${adminEntry}`"
          :loading="adminNavigating"
          @click="goAdmin"
        >
          后台
        </el-button>
        <span v-if="adminTargetUrl" class="admin-url">{{ adminTargetUrl }}</span>
        <el-button
          v-if="!userStore.isAuthenticated"
          type="primary"
          class="login-btn"
          size="large"
          round
          @click="goLogin"
        >
          登录
        </el-button>
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

    <main class="content">
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

      <section class="status-panel">
        <div class="status-left">
          <span class="status-dot" :class="{ online: userStore.isAuthenticated }"></span>
          <div>
            <p class="status-title">{{ statusLabel }}</p>
            <p class="status-desc">{{ statusDescription }}</p>
          </div>
        </div>
        <div class="status-right">
          <span class="chip primary">{{ membershipLabel }}</span>
          <span class="chip" v-if="userStore.isAuthenticated">{{ userStore.maskedPhone }}</span>
          <el-button
            v-else
            class="guest-login"
            type="primary"
            plain
            round
            size="small"
            @click="goLogin"
          >
            游客模式 · 去登录
          </el-button>
        </div>
      </section>

      <section class="admin-entry">
        <div class="admin-text">
          <p class="eyebrow">ADMIN</p>
          <h2>后台管理入口</h2>
          <p class="desc">管理课程、会员、支付与系统设置，支持随时切换到运营后台。</p>
          <div class="admin-actions">
            <el-tag type="info" effect="dark">{{ adminEntry }}</el-tag>
            <el-button type="primary" size="large" :loading="adminNavigating" @click="goAdmin">
              <el-icon class="mr-6"><Setting /></el-icon>
              进入后台
            </el-button>
            <span v-if="adminTargetUrl" class="admin-url">{{ adminTargetUrl }}</span>
          </div>
        </div>
        <div class="admin-meta">
          <div class="meta-item">
            <el-icon><Monitor /></el-icon>
            <div>
              <p class="meta-title">控制台</p>
              <p class="meta-desc">仪表盘、用户、支付与课程管理</p>
            </div>
          </div>
          <div class="meta-item">
            <el-icon><Lock /></el-icon>
            <div>
              <p class="meta-title">权限校验</p>
              <p class="meta-desc">需要管理员身份访问</p>
            </div>
          </div>
        </div>
      </section>

      <section class="list" ref="listRef">
        <div
          v-for="course in visibleCourses"
          :key="course.id"
          class="card"
          role="button"
          tabindex="0"
          @click="goPlayground(course.id)"
          @keydown.enter.prevent="goPlayground(course.id)"
          @keydown.space.prevent="goPlayground(course.id)"
        >
          <div class="thumb">
            <img :src="course.image" :alt="course.title" />
            <span class="tag">{{ course.tag }}</span>
          </div>
          <div class="info">
            <h3>{{ course.title }}</h3>
            <p>{{ course.subtitle }}</p>
            <div class="card-actions">
              <el-button type="primary" @click.stop="goPlayground(course.id)">进入学习</el-button>
            </div>
          </div>
        </div>
      </section>
    </main>

    <div class="load-status">
      <el-icon v-if="loading"><Loading /></el-icon>
      <span v-else-if="!hasMore">没有更多内容</span>
      <span v-else>下滑加载更多</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { Lock, Monitor, Search, Setting, Loading } from '@element-plus/icons-vue';
import { useCoursesStore } from '@/store/courses';
import type { CourseCard } from '@/types/course';
import { useUserStore } from '@/store/user';

const router = useRouter();
const userStore = useUserStore();
const coursesStore = useCoursesStore();
const keyword = ref('');
const listRef = ref<HTMLElement | null>(null);
const loading = ref(false);
const page = ref(0);
const pageSize = 6;
const visibleCourses = ref<CourseCard[]>([]);
const filteredCourses = ref<CourseCard[]>([]);
const hasMore = ref(true);
const adminEntry = computed(() => '/admin');
const adminNavigating = ref(false);
const adminTargetUrl = ref('');

const statusLabel = computed(() => (userStore.isAuthenticated ? '已登录' : '未登录'));
const membershipLabel = computed(() => (userStore.isMember ? '会员用户' : '游客模式'));
const statusDescription = computed(() => {
  if (userStore.isAuthenticated) {
    const tag = userStore.isMember ? '会员权益已激活' : '登录中 · 暂未开通会员';
    return userStore.maskedPhone ? `${userStore.maskedPhone} · ${tag}` : tag;
  }
  return '登录后可同步学习记录与会员特权';
});

const goLogin = () => router.push({ name: 'login' });
const goPlayground = (courseId?: number) => router.push({ name: 'playground', query: courseId ? { courseId } : {} });
const goMember = () => router.push({ name: 'member-center' });
const goAdmin = async () => {
  if (adminNavigating.value) return;
  adminNavigating.value = true;
  const target = router.resolve({ name: 'admin-dashboard' });
  adminTargetUrl.value = target.href;
  try {
    await router.push(target);
  } finally {
    adminNavigating.value = false;
  }
};

const filterCourses = () => {
  const word = keyword.value.trim().toLowerCase();
  const source = coursesStore.courses;
  filteredCourses.value = !word
    ? source
    : source.filter(
        (item) =>
          item.title.toLowerCase().includes(word) ||
          item.subtitle.toLowerCase().includes(word) ||
          item.tag.toLowerCase().includes(word)
      );
  resetAndLoad();
};

const resetAndLoad = () => {
  page.value = 0;
  visibleCourses.value = [];
  hasMore.value = filteredCourses.value.length > 0;
  loadMore();
};

const loadMore = () => {
  if (loading.value || !hasMore.value) return;
  if (!filteredCourses.value.length) {
    hasMore.value = false;
    return;
  }
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

watch(
  () => coursesStore.courses,
  () => {
    if (keyword.value.trim()) {
      filterCourses();
    } else {
      filteredCourses.value = coursesStore.courses;
      resetAndLoad();
    }
  }
);

onMounted(async () => {
  const ok = await userStore.ensureProfileLoaded();
  if (!ok) {
    router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } });
    return;
  }
  coursesStore.fetchCourses().then(() => {
    filteredCourses.value = coursesStore.courses;
    resetAndLoad();
  });
  window.addEventListener('scroll', handleScroll, { passive: true });
});

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: radial-gradient(circle at 20% 20%, #eef2ff, transparent 32%),
    radial-gradient(circle at 80% 0%, #ecfeff, transparent 30%),
    linear-gradient(180deg, #ffffff 0%, #f7f9fb 45%, #ffffff 100%);
  color: #0f172a;
  font-family: 'Inter', 'Noto Sans SC', 'PingFang SC', system-ui, -apple-system, BlinkMacSystemFont,
    'Segoe UI', sans-serif;
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
  gap: 10px;
}

.admin-url {
  color: #475569;
  font-size: 12px;
  align-self: center;
}

.admin-btn {
  border-radius: 999px;
  font-weight: 700;
}

.content {
  max-width: 1160px;
  margin: 0 auto;
  padding: 12px 20px 32px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.login-btn {
  padding: 12px 26px;
  border-radius: 999px;
  background: linear-gradient(120deg, #22c55e, #16a34a);
  border: 1px solid #16a34a;
  color: #fff;
  font-weight: 800;
  letter-spacing: 0.2px;
  box-shadow: 0 12px 28px rgba(34, 197, 94, 0.35);
}

.login-btn:hover,
.login-btn:focus {
  background: linear-gradient(120deg, #16a34a, #15803d);
  border-color: #15803d;
  box-shadow: 0 14px 32px rgba(34, 197, 94, 0.45);
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
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 28px;
  padding: 28px 18px 8px;
  align-items: center;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.06);
}

.banner .text h1 {
  margin: 6px 0 8px;
  font-size: 30px;
  letter-spacing: 0.4px;
}

.banner .text .desc {
  color: #64748b;
  margin-bottom: 14px;
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

.status-panel {
  background: linear-gradient(120deg, rgba(79, 70, 229, 0.1), rgba(16, 185, 129, 0.08));
  border: 1px solid #e0e7ff;
  border-radius: 16px;
  padding: 14px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #0f172a;
}

.status-title {
  margin: 0;
  font-weight: 700;
  font-size: 16px;
}

.status-desc {
  margin: 2px 0 0;
  color: #475569;
  font-size: 13px;
}

.status-right {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.guest-login {
  --el-button-text-color: #16a34a;
  --el-button-border-color: rgba(22, 163, 74, 0.35);
  --el-button-hover-text-color: #0f172a;
  --el-button-hover-bg-color: #dcfce7;
  --el-button-bg-color: #ffffff;
  font-weight: 700;
  letter-spacing: 0.2px;
  box-shadow: 0 10px 24px rgba(22, 163, 74, 0.18);
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #e2e8f0;
  box-shadow: 0 0 0 4px rgba(148, 163, 184, 0.2);
  transition: all 0.2s ease;
}

.status-dot.online {
  background: #22c55e;
  box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.22);
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: #f8fafc;
  color: #0f172a;
  font-weight: 600;
  font-size: 13px;
  border: 1px solid #e2e8f0;
}

.chip.primary {
  background: rgba(79, 70, 229, 0.08);
  color: #4338ca;
  border-color: rgba(79, 70, 229, 0.28);
}

.chip.muted {
  color: #64748b;
}

.admin-entry {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  align-items: center;
  gap: 18px;
  padding: 20px 20px 18px;
  background: radial-gradient(circle at 10% 10%, rgba(168, 85, 247, 0.08), transparent 30%),
    radial-gradient(circle at 90% 20%, rgba(16, 185, 129, 0.08), transparent 30%),
    #ffffff;
  border: 1px solid #e4e8f0;
  border-radius: 18px;
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
}

.admin-text h2 {
  margin: 8px 0 6px;
}

.admin-text .desc {
  color: #475569;
  margin: 0;
  max-width: 620px;
}

.admin-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.admin-actions .admin-url {
  font-weight: 600;
}

.admin-actions .mr-6 {
  margin-right: 6px;
}

.admin-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.meta-item {
  display: flex;
  gap: 10px;
  padding: 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e2e8f0;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

.meta-title {
  margin: 0;
  font-weight: 700;
  color: #0f172a;
}

.meta-desc {
  margin: 2px 0 0;
  color: #64748b;
  font-size: 13px;
}

.list {
  padding: 8px 0 12px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 18px;
}

.card {
  background: #fff;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.05);
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.card:hover {
  transform: translateY(-6px);
  box-shadow: 0 22px 48px rgba(15, 23, 42, 0.08);
  border-color: #cbd5e1;
}

.thumb {
  position: relative;
  height: 180px;
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
  .status-panel {
    flex-direction: column;
    align-items: flex-start;
  }
  .status-right {
    width: 100%;
  }
  .admin-entry {
    grid-template-columns: 1fr;
  }
}
</style>
