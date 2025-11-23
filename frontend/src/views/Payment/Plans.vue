<template>
  <div class="plans">
    <header class="headline">
      <div>
        <p class="eyebrow">订阅计划</p>
        <h1>无感续费，畅享全部课程</h1>
        <p class="sub">支付方式支持微信，Key 在后台配置即可生效。</p>
      </div>
      <el-button @click="goMember">返回会员中心</el-button>
    </header>

    <div class="plan-cards">
      <el-card
        v-for="plan in plans"
        :key="plan.id"
        class="plan-card"
        :class="{ active: selected === plan.id }"
        @click="selected = plan.id"
      >
        <div class="price">￥{{ plan.price }}</div>
        <div class="title">{{ plan.title }}</div>
        <p class="desc">{{ plan.desc }}</p>
        <ul>
          <li v-for="item in plan.features" :key="item">{{ item }}</li>
        </ul>
      </el-card>
    </div>

    <div class="actions">
      <el-button type="primary" size="large" @click="pay">使用微信支付</el-button>
      <p class="hint">支付时将调起微信支付，实际密钥请在后台「系统配置」中填写。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/store/user';

const router = useRouter();
const userStore = useUserStore();
const selected = ref('monthly');

const plans = [
  {
    id: 'daily',
    title: '日卡 · ¥1',
    price: 1,
    desc: '短期冲刺 / 面试前速成',
    features: ['1天无限练习', '语音播报', '所有练习句型']
  },
  {
    id: 'monthly',
    title: '月卡 · ¥10',
    price: 10,
    desc: '30日畅学，适合阶段性提升',
    features: ['全部课程', '学习进度记录', '手机+PC适配']
  },
  {
    id: 'yearly',
    title: '年卡 · ¥30',
    price: 30,
    desc: '全年伴学，超值无忧',
    features: ['全年课程更新', '线下材料下载', '会员专属客服']
  },
  {
    id: 'lifetime',
    title: '终身 · ¥40',
    price: 40,
    desc: '一劳永逸，全部内容永久解锁',
    features: ['终身更新', '不限设备', '活动优先体验']
  }
];

const goMember = () => router.push({ name: 'member-center' });

const pay = () => {
  userStore.upgradeMembership(selected.value as any, '2030-01-01');
  ElMessage.success('示例：已拉起微信支付并完成开通');
  goMember();
};
</script>

<style scoped>
.plans {
  padding: 24px;
}

.headline {
  background: #0b1021;
  color: #fff;
  padding: 18px 20px;
  border-radius: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.eyebrow {
  letter-spacing: 2px;
  color: #10b981;
}

.sub {
  color: #cbd5e1;
}

.plan-cards {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}

.plan-card {
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #e2e8f0;
}

.plan-card.active {
  border-color: #8b5cf6;
  box-shadow: 0 18px 32px rgba(139, 92, 246, 0.18);
}

.price {
  font-size: 28px;
  font-weight: 800;
}

.title {
  font-size: 18px;
  margin: 4px 0 6px;
}

.desc {
  color: #94a3b8;
  min-height: 40px;
}

ul {
  padding-left: 18px;
  color: #475569;
}

.actions {
  margin-top: 18px;
  text-align: center;
  color: #94a3b8;
}
</style>
