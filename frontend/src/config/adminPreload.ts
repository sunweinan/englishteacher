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
  dashboardStats: [] as DashboardStat[],
  users: [] as UserProfile[],
  payments: [] as PaymentRecord[],
  orders: [] as OrderInfo[]
};
