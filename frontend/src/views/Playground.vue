<template>
  <div class="playground">
    <header class="play-header">
      <div class="crumb">学习Playground</div>
      <div class="timer">⌚ 00:00:27</div>
    </header>

    <main class="whiteboard">
      <p class="zh">{{ currentLesson.zh }}</p>
      <div class="en-blanks">
        <div
          v-for="(word, index) in currentWords"
          :key="word + index"
          class="blank"
          :style="{ minWidth: `${word.length * 14 + 24}px` }"
        >
          <input
            v-model="inputs[index]"
            :class="statusClass(index)"
            :aria-label="`answer-${index}`"
            @input="onInput(index)"
          />
          <span class="underline" />
        </div>
      </div>
      <div class="feedback">{{ feedback }}</div>

      <div class="quick">
        <el-button size="small" @click="speak(currentLesson.zh)">再次发声(中)</el-button>
        <el-button size="small" type="primary" @click="speak(currentLesson.en)">再次发声(英)</el-button>
        <el-button size="small" text @click="resetInputs">重置空格</el-button>
      </div>

      <transition-group name="confetti">
        <div
          v-for="piece in confettiPieces"
          :key="piece.id"
          class="confetti"
          :style="{
            left: `${piece.left}%`,
            background: piece.color,
            animationDuration: `${piece.duration}s`,
            animationDelay: `${piece.delay}s`
          }"
        />
      </transition-group>
    </main>

    <footer class="controls">
      <el-button text @click="prev">上一句</el-button>
      <div class="progress">{{ currentIndex + 1 }} / {{ lessons.length }}</div>
      <el-button type="primary" :disabled="!allCorrect" @click="next">下一句</el-button>
    </footer>

    <el-dialog v-model="showRecharge" width="520px" :show-close="false" class="recharge-dialog">
      <template #header>
        <div class="dialog-title">体验到期，开通会员继续练习</div>
      </template>
      <p>非会员可体验3句，开通即可无限练习并解锁所有图文课程。</p>
      <div class="plan-grid">
        <div
          v-for="plan in plans"
          :key="plan.id"
          class="plan"
          :class="{ active: selectedPlan === plan.id }"
          @click="selectedPlan = plan.id"
        >
          <div class="price">￥{{ plan.price }}</div>
          <div class="label">{{ plan.label }}</div>
          <div class="desc">{{ plan.desc }}</div>
        </div>
      </div>
      <p class="hint">充值使用微信支付，Key 可在后台配置。</p>
      <template #footer>
        <el-button @click="showRecharge = false">暂不购买</el-button>
        <el-button type="primary" @click="pay">微信支付</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { useRoute } from 'vue-router';
import { courseCards } from '@/config/courses';
import { useUserStore } from '@/store/user';

const userStore = useUserStore();
const route = useRoute();
const courseId = computed(() => Number(route.query.courseId));
const lessons = computed(() => courseCards.find((c) => c.id === courseId.value)?.lessons || courseCards[0].lessons);

const currentIndex = ref(0);
const inputs = ref<string[]>([]);
const feedback = ref('');
const confettiPieces = ref<Array<{ id: number; left: number; color: string; duration: number; delay: number }>>([]);
const showRecharge = ref(false);
const selectedPlan = ref('daily');

const plans = [
  { id: 'daily', label: '日卡', price: 1, desc: '￥1 / 日' },
  { id: 'monthly', label: '月卡', price: 10, desc: '￥10 / 30日' },
  { id: 'yearly', label: '年卡', price: 30, desc: '￥30 / 年' },
  { id: 'lifetime', label: '终身', price: 40, desc: '￥40 / 终身' }
];

const currentLesson = computed(() => lessons.value[currentIndex.value]);
const currentWords = computed(() => currentLesson.value.en.split(' '));

const initInputs = () => {
  inputs.value = currentWords.value.map(() => '');
  feedback.value = '';
};

const speak = (text: string) => {
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = /[a-zA-Z]/.test(text) ? 'en-US' : 'zh-CN';
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utter);
};

const statusClass = (index: number) => {
  if (!inputs.value[index]) return '';
  return inputs.value[index].trim().toLowerCase() === currentWords.value[index].toLowerCase() ? 'correct' : 'wrong';
};

const allCorrect = computed(() =>
  inputs.value.length === currentWords.value.length &&
  inputs.value.every((val, idx) => val.trim().toLowerCase() === currentWords.value[idx].toLowerCase())
);

const shootConfetti = () => {
  confettiPieces.value = Array.from({ length: 28 }).map((_, idx) => ({
    id: Date.now() + idx,
    left: Math.random() * 100,
    color: ['#10b981', '#8b5cf6', '#f59e0b', '#3b82f6'][idx % 4],
    duration: 1.2 + Math.random() * 0.8,
    delay: Math.random() * 0.3
  }));
  setTimeout(() => {
    confettiPieces.value = [];
  }, 1600);
};

const onInput = (index: number) => {
  if (!inputs.value[index]) return;
  const target = currentWords.value[index].toLowerCase();
  const value = inputs.value[index].trim().toLowerCase();
  if (value === target) {
    feedback.value = '√ 正确';
  } else if (value.length >= target.length) {
    feedback.value = '× 暗紫提示：单词不对';
    speak('try again');
  }
};

const next = () => {
  if (!allCorrect.value) return;
  userStore.markSentenceFinished();
  shootConfetti();
  setTimeout(() => {
    if (!userStore.isMember && userStore.testsCompleted >= 3) {
      showRecharge.value = true;
      return;
    }
    if (currentIndex.value < lessons.value.length - 1) {
      currentIndex.value += 1;
    } else {
      currentIndex.value = 0;
    }
    initInputs();
  }, 500);
};

const prev = () => {
  currentIndex.value = Math.max(0, currentIndex.value - 1);
  initInputs();
};

const resetInputs = () => initInputs();

const pay = () => {
  userStore.upgradeMembership(selectedPlan.value as any, '2030-01-01');
  userStore.resetProgressCounter();
  ElMessage.success('已调用微信支付，会员开通成功（示例）');
  showRecharge.value = false;
};

watch(currentWords, initInputs, { immediate: true });

onMounted(() => {
  speak(currentLesson.value.zh);
});
</script>

<style scoped>
.playground {
  min-height: 100vh;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
}

.play-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  color: #475569;
}

.whiteboard {
  background: #fff;
  margin: 0 auto;
  padding: 48px 24px 24px;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
  width: min(960px, 90vw);
  text-align: center;
  position: relative;
}

.zh {
  font-size: 28px;
  margin-bottom: 24px;
}

.en-blanks {
  display: flex;
  justify-content: center;
  gap: 18px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.blank {
  position: relative;
  min-height: 60px;
}

.blank input {
  border: none;
  border-bottom: 2px solid #e2e8f0;
  outline: none;
  font-size: 24px;
  text-align: center;
  background: transparent;
  padding: 8px 4px;
  min-width: 100%;
}

.blank input.correct {
  color: #16a34a;
  border-color: #16a34a;
}

.blank input.wrong {
  color: #5b2c6f;
  border-color: #5b2c6f;
}

.blank .underline {
  position: absolute;
  left: 0;
  bottom: 8px;
  right: 0;
  height: 2px;
  background: #cbd5e1;
  pointer-events: none;
}

.feedback {
  min-height: 24px;
  color: #6366f1;
  margin-bottom: 10px;
}

.quick {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 12px;
}

.controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px 24px;
  width: min(960px, 90vw);
  margin: 0 auto;
}

.progress {
  color: #94a3b8;
}

.confetti {
  position: absolute;
  top: 20%;
  width: 10px;
  height: 16px;
  opacity: 0.9;
  border-radius: 3px;
  animation: fall linear forwards;
}

@keyframes fall {
  from {
    transform: translateY(0) rotate(0deg);
    opacity: 1;
  }
  to {
    transform: translateY(320px) rotate(320deg);
    opacity: 0;
  }
}

.recharge-dialog .plan-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  margin: 16px 0 12px;
}

.recharge-dialog .plan {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.recharge-dialog .plan.active {
  border-color: #a855f7;
  box-shadow: 0 10px 24px rgba(168, 85, 247, 0.15);
}

.recharge-dialog .price {
  font-size: 24px;
  font-weight: 700;
}

.recharge-dialog .desc {
  color: #94a3b8;
  font-size: 12px;
}

.recharge-dialog .hint {
  color: #64748b;
}

@media (max-width: 768px) {
  .whiteboard {
    padding: 36px 18px 16px;
  }
  .zh {
    font-size: 22px;
  }
  .blank input {
    font-size: 20px;
  }
}
</style>
