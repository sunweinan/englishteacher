export interface DashboardStat {
  label: string;
  value: string;
  note: string;
}

export type MemberLevel = '游客' | '日卡' | '月卡' | '年卡' | '终身';

export interface PaymentRecord {
  id: number;
  user_display: string;
  amount: number;
  level: MemberLevel;
  channel: string;
  order_no: string;
  paid_at: string;
}

export interface UserProfile {
  id: number;
  nickname: string;
  phone: string;
  level: MemberLevel;
  register_at: string;
  spend: number;
  tests: number;
  benefits: string;
  recharges: string[];
  note?: string;
}

export interface OrderItemInfo {
  id: number;
  name: string;
  quantity: number;
  price: number;
}

export type OrderStatus = '待支付' | '已支付' | '已退款';

export interface OrderInfo {
  id: string;
  user: string;
  created_at: string;
  status: OrderStatus;
  channel: string;
  amount: number;
  items: OrderItemInfo[];
  remark?: string;
}
