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
          :style="blankStyle(word)"
        >
          <input
            v-model="inputs[index]"
            :class="statusClass(index)"
            :aria-label="`answer-${index}`"
            :ref="(el) => setInputRef(el, index)"
            @input="onInput(index)"
            @keydown="handleKeydown($event, index)"
            @focus="() => (activeIndex = index)"
          />
          <span class="underline" :style="{ width: `${underlineWidth(word)}px` }" />
        </div>
      </div>
      <div class="feedback">{{ feedback }}</div>

      <div class="quick">
        <el-button size="small" type="primary" plain round @click="() => speak(currentLesson.zh)">
          重读中文（键盘 1）
        </el-button>
        <el-button size="small" type="success" round @click="() => speak(currentLesson.en)">
          重读英文（键盘 2）
        </el-button>
        <el-button size="small" plain round @click="resetInputs">重置空格</el-button>
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
      <el-button type="primary" :disabled="!inputs.length" @click="evaluateSentence">评判 / 下一句</el-button>
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
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { useRoute } from 'vue-router';
import { courseCards } from '@/config/courses';
import { useUserStore } from '@/store/user';

const userStore = useUserStore();
const route = useRoute();
const courseId = computed(() => Number(route.query.courseId));
const lessons = computed(() => courseCards.find((c) => c.id === courseId.value)?.lessons || courseCards[0].lessons);

const currentIndex = ref(0);
const activeIndex = ref(0);
const inputs = ref<string[]>([]);
const feedback = ref('');
const confettiPieces = ref<Array<{ id: number; left: number; color: string; duration: number; delay: number }>>([]);
const showRecharge = ref(false);
const selectedPlan = ref('daily');
const inputRefs = ref<HTMLInputElement[]>([]);
const audioCtx = ref<AudioContext | null>(null);
const consecutiveCorrect = ref(0);

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
  activeIndex.value = 0;
  inputRefs.value = [];
};

const speak = (text: string) =>
  new Promise<void>((resolve) => {
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = /[a-zA-Z]/.test(text) ? 'en-US' : 'zh-CN';
    utter.onend = () => resolve();
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);
  });

const speakSequence = async () => {
  await speak(currentLesson.value.zh);
  await speak(currentLesson.value.en);
};

const statusClass = (index: number) => {
  if (!inputs.value[index]) return '';
  return inputs.value[index].trim().toLowerCase() === currentWords.value[index].toLowerCase() ? 'correct' : 'wrong';
};

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

const ensureAudioContext = () => {
  if (!audioCtx.value) audioCtx.value = new AudioContext();
  return audioCtx.value;
};

const playTypewriterSound = () => {
  const ctx = ensureAudioContext();
  const baseTime = ctx.currentTime;

  const createClick = (time: number, freq: number, gainValue: number, filterFreq: number) => {
    const osc = ctx.createOscillator();
    osc.type = 'square';
    osc.frequency.value = freq;

    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.value = filterFreq;
    filter.Q.value = 6;

    const gain = ctx.createGain();
    gain.gain.setValueAtTime(gainValue, time);
    gain.gain.exponentialRampToValueAtTime(0.0001, time + 0.09);

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);

    osc.start(time);
    osc.stop(time + 0.12);
  };

  const noiseBuffer = ctx.createBuffer(1, ctx.sampleRate * 0.03, ctx.sampleRate);
  const data = noiseBuffer.getChannelData(0);
  for (let i = 0; i < data.length; i += 1) {
    data[i] = (Math.random() * 2 - 1) * 0.35;
  }

  const noise = ctx.createBufferSource();
  noise.buffer = noiseBuffer;

  const noiseFilter = ctx.createBiquadFilter();
  noiseFilter.type = 'bandpass';
  noiseFilter.frequency.value = 1800;
  noiseFilter.Q.value = 5;

  const noiseGain = ctx.createGain();
  noiseGain.gain.setValueAtTime(0.12, baseTime);
  noiseGain.gain.exponentialRampToValueAtTime(0.0001, baseTime + 0.05);

  noise.connect(noiseFilter);
  noiseFilter.connect(noiseGain);
  noiseGain.connect(ctx.destination);

  createClick(baseTime, 170 + Math.random() * 20, 0.16, 900);
  createClick(baseTime + 0.05, 260 + Math.random() * 30, 0.12, 1400);

  const thunkOsc = ctx.createOscillator();
  thunkOsc.type = 'sine';
  thunkOsc.frequency.value = 120 + Math.random() * 15;

  const thunkGain = ctx.createGain();
  thunkGain.gain.setValueAtTime(0.1, baseTime + 0.02);
  thunkGain.gain.exponentialRampToValueAtTime(0.0001, baseTime + 0.15);

  thunkOsc.connect(thunkGain);
  thunkGain.connect(ctx.destination);

  noise.start(baseTime + 0.01);
  noise.stop(baseTime + 0.08);
  thunkOsc.start(baseTime + 0.02);
  thunkOsc.stop(baseTime + 0.17);
};

const playTone = (frequency: number, duration = 0.08, volume = 0.08) => {
  const ctx = ensureAudioContext();
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.frequency.value = frequency;
  gain.gain.value = volume;
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start();
  osc.stop(ctx.currentTime + duration);
};

const playKeySound = () => playTypewriterSound();
const playRewardSound = () => {
  playTone(660, 0.08, 0.06);
  setTimeout(() => playTone(880, 0.12, 0.07), 90);
};

const setInputRef = (el: HTMLInputElement | null, index: number) => {
  if (el) inputRefs.value[index] = el;
};

const blankStyle = (word: string) => ({ width: `${underlineWidth(word)}px` });
const underlineWidth = (word: string) => Math.max(24, word.length * 12 + 8);

const onInput = (index: number) => {
  if (!inputs.value[index]) return;
  const target = currentWords.value[index].toLowerCase();
  const value = inputs.value[index].trim().toLowerCase();
  if (value === target) {
    feedback.value = '✅ 正确';
  }
};

const focusIndex = (index: number) => {
  const target = inputRefs.value[index];
  if (target) {
    target.focus();
    target.select();
  }
};

const judgeWord = (index: number) => {
  playKeySound();
  const target = currentWords.value[index];
  const value = inputs.value[index]?.trim();
  if (!value) {
    feedback.value = '请输入这个单词';
    speak(target);
    return false;
  }
  if (value.toLowerCase() === target.toLowerCase()) {
    feedback.value = '✅ 正确，继续';
    return true;
  }
  feedback.value = `${target} 拼写不对`;
  speak(target);
  return false;
};

const evaluateSentence = async () => {
  const incorrectIndex = inputs.value.findIndex(
    (val, idx) => val.trim().toLowerCase() !== currentWords.value[idx].toLowerCase()
  );
  if (incorrectIndex !== -1) {
    activeIndex.value = incorrectIndex;
    focusIndex(incorrectIndex);
    feedback.value = '还有单词没对上，空格键可立即判定';
    await speak(currentWords.value[incorrectIndex]);
    consecutiveCorrect.value = 0;
    return;
  }
  feedback.value = '完美！即将进入下一句';
  userStore.markSentenceFinished();
  consecutiveCorrect.value += 1;
  shootConfetti();
  playRewardSound();
  await speak(currentLesson.value.en);
  setTimeout(() => {
    if (!userStore.isMembershipActive && consecutiveCorrect.value >= 3) {
      consecutiveCorrect.value = 0;
      showRecharge.value = true;
      return;
    }
    if (currentIndex.value < lessons.value.length - 1) {
      currentIndex.value += 1;
    } else {
      currentIndex.value = 0;
    }
    initInputs();
  }, 300);
};

const handleEnter = (index: number) => {
  const isCorrect = judgeWord(index);
  const isLast = index === currentWords.value.length - 1;
  if (isCorrect && !isLast) {
    focusIndex(index + 1);
    activeIndex.value = index + 1;
    return;
  }
  if (isLast) {
    evaluateSentence();
  }
};

const handleSpaceJudge = (index: number) => {
  const isCorrect = judgeWord(index);
  if (isCorrect) {
    const isLast = index === currentWords.value.length - 1;
    if (isLast) {
      evaluateSentence();
    } else {
      focusIndex(index + 1);
      activeIndex.value = index + 1;
    }
  }
};

const handleKeydown = (event: KeyboardEvent, index: number) => {
  if (event.key === 'Backspace' && !inputs.value[index]) {
    if (index > 0) {
      event.preventDefault();
      const prevIndex = index - 1;
      activeIndex.value = prevIndex;
      focusIndex(prevIndex);
    }
    return;
  }
  if (event.key === 'Enter') {
    event.preventDefault();
    handleEnter(index);
    return;
  }
  if (event.key === ' ') {
    event.preventDefault();
    handleSpaceJudge(index);
  } else {
    playKeySound();
  }
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
const handleGlobalShortcut = (event: KeyboardEvent) => {
  if (event.key === '1') {
    event.preventDefault();
    speak(currentLesson.value.zh);
  }
  if (event.key === '2') {
    event.preventDefault();
    speak(currentLesson.value.en);
  }
  if (event.key === ' ' && document.activeElement instanceof HTMLInputElement) {
    event.preventDefault();
    const focusedIndex = inputRefs.value.findIndex((el) => el === document.activeElement);
    if (focusedIndex !== -1) handleSpaceJudge(focusedIndex);
  }
};

watch(
  currentWords,
  async () => {
    initInputs();
    await nextTick();
    focusIndex(0);
    await speakSequence();
  },
  { immediate: true }
);

onMounted(() => {
  window.addEventListener('keydown', handleGlobalShortcut);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleGlobalShortcut);
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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.zh {
  font-size: 20px;
  margin-bottom: 6px;
  color: #0f172a;
}

.en-blanks {
  display: flex;
  justify-content: center;
  gap: 14px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}

.blank {
  position: relative;
  min-height: 62px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
}

.blank input {
  border: none;
  outline: none;
  font-size: 22px;
  text-align: center;
  background: transparent;
  padding: 8px 6px 12px;
  width: 100%;
  color: #0f172a;
  letter-spacing: 0.4px;
  border-radius: 0;
}

.blank input.correct {
  color: #16a34a;
  font-weight: 700;
}

.blank input.wrong {
  color: #5b2c6f;
}

.blank .underline {
  position: absolute;
  left: 50%;
  bottom: 6px;
  height: 2px;
  background: #cbd5e1;
  pointer-events: none;
  transform: translateX(-50%);
}

.feedback {
  min-height: 24px;
  color: #4338ca;
  margin-bottom: 8px;
  font-weight: 600;
}

.quick {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.quick :deep(.el-button) {
  padding: 10px 14px;
  font-weight: 700;
  box-shadow: 0 12px 26px rgba(79, 70, 229, 0.1);
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
