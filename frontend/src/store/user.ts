import { defineStore } from 'pinia';

export type MembershipLevel = 'free' | 'daily' | 'monthly' | 'yearly' | 'lifetime';

interface AuthState {
  token: string | null;
  phone: string | null;
  membership: MembershipLevel;
  memberUntil: string | null;
  referrals: number;
  testsCompleted: number;
  role: 'user' | 'admin';
}

const maskPhone = (phone: string) => {
  if (!phone || phone.length < 7) return phone;
  return `${phone.slice(0, 3)}****${phone.slice(-4)}`;
};

export const useUserStore = defineStore('user', {
  state: (): AuthState => ({
    token: localStorage.getItem('token'),
    phone: localStorage.getItem('phone'),
    membership: (localStorage.getItem('membership') as MembershipLevel) || 'free',
    memberUntil: localStorage.getItem('memberUntil'),
    referrals: Number(localStorage.getItem('referrals') || 0),
    testsCompleted: 0,
    role: (localStorage.getItem('role') as 'user' | 'admin') || 'user'
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    maskedPhone(state) {
      return state.phone ? maskPhone(state.phone) : '';
    },
    isMember(state) {
      return state.membership !== 'free';
    },
    isMembershipActive(state) {
      if (state.membership === 'free') return false;
      if (!state.memberUntil) return true;
      return new Date(state.memberUntil).getTime() >= Date.now();
    },
    isAdmin(state) {
      return state.role === 'admin';
    }
  },
  actions: {
    setToken(token: string | null) {
      this.token = token;
      if (token) {
        localStorage.setItem('token', token);
      } else {
        localStorage.removeItem('token');
      }
    },
    persistProfile() {
      if (this.phone) localStorage.setItem('phone', this.phone);
      if (this.membership) localStorage.setItem('membership', this.membership);
      if (this.memberUntil) localStorage.setItem('memberUntil', this.memberUntil);
      localStorage.setItem('referrals', String(this.referrals));
      localStorage.setItem('role', this.role);
    },
    loginWithCode(phone: string) {
      if (!/^[0-9]{4,20}$/.test(phone)) {
        throw new Error('请输入合法的手机号');
      }
      this.phone = phone;
      this.setToken(`token-${phone}-${Date.now()}`);
      this.role = phone.endsWith('0000') ? 'admin' : 'user';
      this.persistProfile();
    },
    logout() {
      this.phone = null;
      this.membership = 'free';
      this.memberUntil = null;
      this.referrals = 0;
      this.testsCompleted = 0;
      this.role = 'user';
      this.setToken(null);
      localStorage.removeItem('phone');
      localStorage.removeItem('membership');
      localStorage.removeItem('memberUntil');
      localStorage.removeItem('referrals');
      localStorage.removeItem('role');
    },
    upgradeMembership(level: MembershipLevel, until: string | null = null) {
      this.membership = level;
      this.memberUntil = until;
      this.persistProfile();
    },
    updatePhone(phone: string) {
      this.phone = phone;
      this.persistProfile();
    },
    recordReferral() {
      this.referrals += 1;
      this.persistProfile();
    },
    markSentenceFinished() {
      this.testsCompleted += 1;
    },
    resetProgressCounter() {
      this.testsCompleted = 0;
    }
  }
});
