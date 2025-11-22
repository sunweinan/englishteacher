import { defineStore } from 'pinia';

export interface CartItem {
  productId: number;
  name: string;
  price: number;
  quantity: number;
}

interface CartState {
  items: CartItem[];
}

export const useCartStore = defineStore('cart', {
  state: (): CartState => ({
    items: []
  }),
  getters: {
    total: (state) => state.items.reduce((sum, item) => sum + item.price * item.quantity, 0)
  },
  actions: {
    addItem(item: CartItem) {
      const existing = this.items.find((i) => i.productId === item.productId);
      if (existing) {
        existing.quantity += item.quantity;
      } else {
        this.items.push(item);
      }
    },
    removeItem(productId: number) {
      this.items = this.items.filter((i) => i.productId !== productId);
    },
    clear() {
      this.items = [];
    }
  }
});
