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
    title: '第1课 基础语序课',
    subtitle: '吃饭、问候、日常情景的开口训练',
    tag: '基础·高频',
    image: 'https://images.unsplash.com/photo-1584697964156-1231a6c5b551?auto=format&fit=crop&w=900&q=80',
    lessons: [
      { zh: '我很开心', en: 'I am happy', phonetic: "aɪ æm 'hæpi", audio: 'I am happy' },
      { zh: '我喜欢这个食物', en: 'I like this food', phonetic: "aɪ laɪk ðɪs fuːd", audio: 'I like this food' },
      { zh: '请慢慢说', en: 'Please speak slowly', phonetic: "pliːz spiːk 'sləʊli", audio: 'Please speak slowly' }
    ]
  },
  {
    id: 2,
    title: '40图景秒记单词',
    subtitle: '图像化记忆+拼写练习',
    tag: '词汇·图景',
    image: 'https://images.unsplash.com/photo-1513258496099-48168024aec0?auto=format&fit=crop&w=900&q=80',
    lessons: [
      { zh: '那只猫很安静', en: 'The cat is quiet', phonetic: 'ðə kæt ɪz ˈkwaɪɪt', audio: 'The cat is quiet' },
      { zh: '阳光很温暖', en: 'The sunlight is warm', phonetic: 'ðə ˈsʌnˌlaɪt ɪz wɔːm', audio: 'The sunlight is warm' }
    ]
  },
  {
    id: 3,
    title: '高频对话625场景',
    subtitle: '地铁、咖啡厅、酒店、面试全覆盖',
    tag: '场景·对话',
    image: 'https://images.unsplash.com/photo-1497493292307-31c376b6e479?auto=format&fit=crop&w=900&q=80',
    lessons: [
      { zh: '我要一杯拿铁', en: 'I would like a latte', phonetic: 'aɪ wʊd laɪk ə ˈlɑːteɪ', audio: 'I would like a latte' },
      { zh: '可以帮我叫一辆车吗', en: 'Could you call me a car', phonetic: 'kʊd ju kɔːl miː ə kɑː', audio: 'Could you call me a car' }
    ]
  },
  {
    id: 4,
    title: '出国考试精读',
    subtitle: 'IELTS / TOEFL / PTE 高频句型',
    tag: '考试·精品',
    image: 'https://images.unsplash.com/photo-1518552718880-5c9d95a7a0c0?auto=format&fit=crop&w=900&q=80',
    lessons: [
      { zh: '准备一场新的旅程', en: 'Prepare for a new journey', phonetic: 'prɪˈpeə fə ə njuː ˈdʒɜːni', audio: 'Prepare for a new journey' }
    ]
  },
  {
    id: 5,
    title: '外贸口语特训',
    subtitle: '下单、物流、付款全流程表达',
    tag: '商务·外贸',
    image: 'https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?auto=format&fit=crop&w=900&q=80',
    lessons: [
      { zh: '我们今天发货', en: 'We ship today', phonetic: 'wiː ʃɪp təˈdeɪ', audio: 'We ship today' }
    ]
  },
  {
    id: 6,
    title: '旅行口语72句',
    subtitle: '机场酒店问路全包',
    tag: '旅行·轻松',
    image: 'https://images.unsplash.com/photo-1502920514313-52581002a659?auto=format&fit=crop&w=900&q=80',
    lessons: [
      { zh: '最近的地铁站在哪里', en: 'Where is the nearest subway station', phonetic: 'wɛər ɪz ðə ˈnɪərəst ˈsʌbweɪ ˈsteɪʃən', audio: 'Where is the nearest subway station' }
    ]
  },
  {
    id: 7,
    title: '宠物英语陪练',
    subtitle: '和毛孩子的日常对话',
    tag: '生活·萌宠',
    image: 'https://images.unsplash.com/photo-1518791841217-8f162f1e1131?auto=format&fit=crop&w=900&q=80',
    lessons: [
      { zh: '坐下，等一下', en: 'Sit down and wait', phonetic: 'sɪt daʊn ænd weɪt', audio: 'Sit down and wait' }
    ]
  },
  {
    id: 8,
    title: '母婴家庭场景',
    subtitle: '陪伴孩子的英语环境',
    tag: '家庭·陪伴',
    image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=900&q=80',
    lessons: [
      { zh: '睡觉时间到了', en: 'It is time to sleep', phonetic: 'ɪt ɪz taɪm tə sliːp', audio: 'It is time to sleep' }
    ]
  }
];
