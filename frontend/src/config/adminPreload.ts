export interface DashboardStat {
  label: string;
  value: string;
  note: string;
}

export type MemberLevel = '游客' | '日卡' | '月卡' | '年卡' | '终身';

export interface PaymentRecord {
  time: string;
  user: string;
  amount: number;
  level: MemberLevel;
  channel: string;
  orderNo: string;
}

export interface UserProfile {
  id: number;
  nickname: string;
  phone: string;
  level: MemberLevel;
  registerAt: string;
  spend: number;
  tests: number;
  benefits: string;
  recharges: string[];
  note?: string;
}

export interface OrderItemInfo {
  name: string;
  quantity: number;
  price: number;
}

export type OrderStatus = '待支付' | '已支付' | '已退款';

export interface OrderInfo {
  id: string;
  user: string;
  createdAt: string;
  status: OrderStatus;
  channel: string;
  amount: number;
  items: OrderItemInfo[];
  remark?: string;
}

export const adminPreloadData = {
  dashboardStats: [
    { label: '会员总数', value: '1,254', note: '含日卡、月卡、年卡、终身' },
    { label: '今日支付额', value: '¥3,280', note: '最近24小时微信支付' },
    { label: '课程数量', value: '128 组', note: '列表页展示的全部系列' },
    { label: '分享返佣', value: '¥860', note: '已累计发放' }
  ] as DashboardStat[],
  users: [
    {
      id: 1,
      nickname: 'Ava',
      phone: '138****8888',
      level: '年卡',
      registerAt: '2024-03-12T08:36:00',
      spend: 320,
      tests: 128,
      benefits: '有效期 2025-03-11 · 每日10题权限',
      recharges: ['2024-03-12 年卡 ¥30', '2024-03-30 口语包 ¥15'],
      note: '近期刚续费，请关注转介绍意向。'
    },
    {
      id: 2,
      nickname: 'Leo',
      phone: '139****5566',
      level: '月卡',
      registerAt: '2024-04-01T20:10:00',
      spend: 120,
      tests: 52,
      benefits: '有效期 2024-05-01 · 每日5题',
      recharges: ['2024-04-01 月卡 ¥10', '2024-04-10 口语包 ¥20']
    },
    {
      id: 3,
      nickname: 'Nina',
      phone: '137****1020',
      level: '终身',
      registerAt: '2024-02-20T12:02:00',
      spend: 1280,
      tests: 482,
      benefits: '终身有效 · 全部题库开放',
      recharges: ['2024-02-20 终身卡 ¥40'],
      note: '高活跃度，常用移动端学习。'
    },
    {
      id: 4,
      nickname: 'Mia',
      phone: '136****8899',
      level: '游客',
      registerAt: '2024-04-08T09:01:00',
      spend: 0,
      tests: 8,
      benefits: '游客试用剩余 7 天 · 仅体验模式',
      recharges: []
    }
  ] as UserProfile[],
  payments: [
    {
      time: '2024-04-08T10:28:00',
      user: '138****8888',
      level: '年卡',
      amount: 30,
      channel: '微信支付',
      orderNo: '4200002184202404086620001'
    },
    {
      time: '2024-04-07T22:10:00',
      user: '139****5566',
      level: '月卡',
      amount: 10,
      channel: '微信支付',
      orderNo: '4200002184202404079988002'
    },
    {
      time: '2024-04-07T12:02:00',
      user: '137****1020',
      level: '终身',
      amount: 40,
      channel: '微信支付',
      orderNo: '4200002184202404073311888'
    }
  ] as PaymentRecord[],
  orders: [
    {
      id: '20240408001',
      user: '138****8888',
      createdAt: '2024-04-08T10:27:30',
      status: '已支付',
      channel: '微信支付',
      amount: 30,
      items: [
        { name: '英语口语进阶套餐', quantity: 1, price: 30 }
      ],
      remark: '年卡续费，移动端完成支付。'
    },
    {
      id: '20240407012',
      user: '139****5566',
      createdAt: '2024-04-07T22:08:12',
      status: '已支付',
      channel: '微信支付',
      amount: 10,
      items: [
        { name: '月卡', quantity: 1, price: 10 },
        { name: '口语提分包', quantity: 1, price: 20 }
      ],
      remark: '下单后 2 分钟内完成支付。'
    },
    {
      id: '20240407003',
      user: '137****1020',
      createdAt: '2024-04-07T11:58:00',
      status: '已支付',
      channel: '微信支付',
      amount: 40,
      items: [
        { name: '终身卡', quantity: 1, price: 40 }
      ],
      remark: '微信免密支付，已开通全部权限。'
    }
  ] as OrderInfo[]
};
