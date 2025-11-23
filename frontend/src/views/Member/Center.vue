<template>
  <div class="member-center">
    <section class="hero">
      <div>
        <p class="eyebrow">会员中心</p>
        <h1>管理手机号、续费、分享返佣</h1>
        <p class="sub">登录后即可同步会员权益，分享给好友还能拿30%返佣。</p>
      </div>
      <el-button type="primary" @click="goRecharge">立即充值</el-button>
    </section>

    <div class="grid">
      <el-card class="panel">
        <template #header>
          <div class="panel-title">账户信息</div>
        </template>
        <div class="row">
          <span>手机号</span>
          <div class="right">
            <el-input v-model="form.phone" placeholder="输入手机号" maxlength="11" />
            <el-button type="primary" @click="savePhone">保存</el-button>
          </div>
        </div>
        <div class="row">
          <span>会员等级</span>
          <el-tag type="success">{{ levelLabel }}</el-tag>
        </div>
        <div class="row">
          <span>有效期</span>
          <span>{{ userStore.memberUntil || '未开通 / 体验中' }}</span>
        </div>
      </el-card>

      <el-card class="panel">
        <template #header>
          <div class="panel-title">分享赚钱</div>
        </template>
        <p>分享链接发给朋友，TA 付费你得 30% 返佣。</p>
        <el-input v-model="shareLink" readonly />
        <el-button type="primary" @click="copyLink">复制链接</el-button>
        <p class="tips">当前已邀请 {{ userStore.referrals }} 人</p>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/store/user';

const userStore = useUserStore();
const router = useRouter();
const form = reactive({ phone: userStore.phone || '' });
const shareLink = ref('https://english.example.com/invite?code=VIP2024');

const levelLabel = computed(() => {
  switch (userStore.membership) {
    case 'daily':
      return '日卡会员';
    case 'monthly':
      return '月卡会员';
    case 'yearly':
      return '年卡会员';
    case 'lifetime':
      return '终身会员';
    default:
      return '体验/免费';
  }
});

const savePhone = () => {
  if (!/^\d{11}$/.test(form.phone)) {
    ElMessage.error('请输入11位手机号');
    return;
  }
  userStore.updatePhone(form.phone);
  ElMessage.success('手机号已更新');
};

const copyLink = async () => {
  await navigator.clipboard.writeText(shareLink.value);
  userStore.recordReferral();
  ElMessage.success('分享链接已复制，快去赚钱吧！');
};

const goRecharge = () => router.push({ name: 'recharge' });
</script>

<style scoped>
.member-center {
  padding: 24px;
}

.hero {
  background: #0f172a;
  color: #fff;
  padding: 18px 20px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.eyebrow {
  letter-spacing: 2px;
  color: #a855f7;
  margin: 0;
}

.sub {
  color: #cbd5e1;
}

.grid {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.panel-title {
  font-weight: 700;
}

.panel .row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
}

.panel .right {
  display: flex;
  gap: 6px;
  flex: 1;
}

.tips {
  color: #94a3b8;
  margin-top: 6px;
}
</style>
