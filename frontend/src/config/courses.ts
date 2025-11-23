export interface Lesson {
  zh: string;
  en: string;
  phonetic: string;
  audio: string;
}

export interface CourseCard {
  id: number;
  title: string;
  subtitle: string;
  image: string;
  tag: string;
  lessons: Lesson[];
}

export const courseCards: CourseCard[] = [
  {
    id: 1,
    title: '幼儿园幼小衔接',
    subtitle: '自然拼读+礼貌表达，顺滑过渡小学',
    tag: '启蒙·语感',
    image: 'https://images.unsplash.com/photo-1472162072942-cd5147eb3902?auto=format&fit=crop&w=1200&q=80',
    lessons: [
      { zh: '我们一起读书', en: 'We read together', phonetic: 'wiː riːd təˈɡeðə', audio: 'We read together' },
      { zh: '请排好队', en: 'Please line up', phonetic: 'pliːz laɪn ʌp', audio: 'Please line up' },
      { zh: '要对老师说谢谢', en: 'Say thank you to the teacher', phonetic: 'seɪ ˈθæŋk juː tə ðə ˈtiːtʃə', audio: 'Say thank you to the teacher' }
    ]
  },
  {
    id: 2,
    title: '小学1-3年级',
    subtitle: '分级阅读+课本同步，先声夺人',
    tag: '小学·基础',
    image: 'https://images.unsplash.com/photo-1527980965255-d3b416303d12?auto=format&fit=crop&w=1200&q=80',
    lessons: [
      { zh: '我喜欢科学课', en: 'I like science class', phonetic: 'aɪ laɪk ˈsaɪəns klɑːs', audio: 'I like science class' },
      { zh: '今天是星期一', en: 'Today is Monday', phonetic: 'təˈdeɪ ɪz ˈmʌndeɪ', audio: 'Today is Monday' }
    ]
  },
  {
    id: 3,
    title: '小学4-6年级',
    subtitle: '语法巩固+写作句型，迎战小升初',
    tag: '小学·进阶',
    image: 'https://images.unsplash.com/photo-1523580846011-d3a5bc25702b?auto=format&fit=crop&w=1200&q=80',
    lessons: [
      { zh: '我正在完成作业', en: 'I am finishing my homework', phonetic: 'aɪ æm ˈfɪnɪʃɪŋ maɪ ˈhəʊmwɜːk', audio: 'I am finishing my homework' },
      { zh: '他将成为一名科学家', en: 'He will be a scientist', phonetic: 'hiː wɪl biː ə ˈsaɪəntɪst', audio: 'He will be a scientist' }
    ]
  },
  {
    id: 4,
    title: '初中精选句子',
    subtitle: '短语+从句+写作万能句，考试必背',
    tag: '初中·冲分',
    image: 'https://images.unsplash.com/photo-1523580846011-d3a5bc25702b?auto=format&fit=crop&w=1200&q=80&sat=-15',
    lessons: [
      { zh: '据说他昨天生病了', en: 'It is said that he was ill yesterday', phonetic: 'ɪt ɪz sed ðæt hi wəz ɪl ˈjɛstədeɪ', audio: 'It is said that he was ill yesterday' },
      { zh: '我们一完成就通知你', en: 'We will tell you once we finish', phonetic: 'wi wɪl tɛl ju wʌns wi ˈfɪnɪʃ', audio: 'We will tell you once we finish' }
    ]
  },
  {
    id: 5,
    title: '高中必会',
    subtitle: '长难句拆分+语篇写作，直击高考',
    tag: '高中·必备',
    image: 'https://images.unsplash.com/photo-1460518451285-97b6aa326961?auto=format&fit=crop&w=1200&q=80',
    lessons: [
      {
        zh: '努力的人不一定成功，但放弃的人注定失败',
        en: 'Hard work may not ensure success, but giving up guarantees failure',
        phonetic: 'hɑːd wɜːk meɪ nɒt ɪnˈʃʊə səkˈsɛs bət ˈɡɪvɪŋ ʌp ˌɡærənˈtiːz ˈfeɪljə',
        audio: 'Hard work may not ensure success, but giving up guarantees failure'
      }
    ]
  },
  {
    id: 6,
    title: '雅思口语冲刺',
    subtitle: '7+ 高频题库+逻辑连接词模板',
    tag: '留学·IELTS',
    image: 'https://images.unsplash.com/photo-1523580846011-d3a5bc25702b?auto=format&fit=crop&w=1200&q=80&sat=10',
    lessons: [
      { zh: '我喜欢能带来改变的书', en: 'I enjoy books that can make a difference', phonetic: 'aɪ ɪnˈdʒɔɪ bʊks ðæt kən meɪk ə ˈdɪfrəns', audio: 'I enjoy books that can make a difference' }
    ]
  },
  {
    id: 7,
    title: '托福口语模板',
    subtitle: '独立+综合口语黄金句型库',
    tag: '留学·TOEFL',
    image: 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1200&q=80',
    lessons: [
      { zh: '校园应该鼓励学生辩论', en: 'Campus should encourage student debates', phonetic: 'ˈkæmpəs ʃʊd ɪnˈkʌrɪdʒ ˈstjuːdənt dɪˈbeɪts', audio: 'Campus should encourage student debates' }
    ]
  },
  {
    id: 8,
    title: '日常英语旅游短句',
    subtitle: '机场、酒店、问路一键开口',
    tag: '旅行·口语',
    image: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80',
    lessons: [
      { zh: '最近的地铁站在哪里', en: 'Where is the nearest subway station', phonetic: 'wɛər ɪz ðə ˈnɪərəst ˈsʌbweɪ ˈsteɪʃən', audio: 'Where is the nearest subway station' }
    ]
  },
  {
    id: 9,
    title: '高薪商务英语',
    subtitle: '谈判、简报、薪资晋升表达全覆盖',
    tag: '商务·进阶',
    image: 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1200&q=80&sat=-5',
    lessons: [
      { zh: '我们需要更详细的报价', en: 'We need a more detailed quotation', phonetic: 'wiː niːd ə mɔː ˈdiːteɪld kwəʊˈteɪʃən', audio: 'We need a more detailed quotation' }
    ]
  },
  {
    id: 10,
    title: '日常生活流利说',
    subtitle: '美剧口语+常用词块，陪你开口',
    tag: '生活·畅聊',
    image: 'https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=1200&q=80',
    lessons: [
      { zh: '这事儿我包在身上', en: 'I have got this covered', phonetic: 'aɪ hæv ɡɒt ðɪs ˈkʌvəd', audio: 'I have got this covered' }
    ]
  }
];
