import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      setAuth: (user, token) => set({ user, token, isAuthenticated: true }),
      logout: () => set({ user: null, token: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
    }
  )
)

export const useCartStore = create((set) => ({
  items: [],
  count: 0,
  
  setCart: (items) => set({ items, count: items.length }),
  addItem: (item) => set((state) => ({
    items: [...state.items, item],
    count: state.count + 1,
  })),
  removeItem: (productId, size) => set((state) => ({
    items: state.items.filter(item => !(item.product_id === productId && item.size === size)),
    count: state.count - 1,
  })),
  clearCart: () => set({ items: [], count: 0 }),
}))

export const useWishlistStore = create((set) => ({
  items: [],
  
  setWishlist: (items) => set({ items }),
  addItem: (item) => set((state) => ({ items: [...state.items, item] })),
  removeItem: (productId) => set((state) => ({
    items: state.items.filter(item => item.id !== productId),
  })),
  isInWishlist: (productId) => (state) => state.items.some(item => item.id === productId),
}))

export const useUIStore = create((set) => ({
  isMenuOpen: false,
  isCartOpen: false,
  isSearchOpen: false,
  
  toggleMenu: () => set((state) => ({ isMenuOpen: !state.isMenuOpen })),
  toggleCart: () => set((state) => ({ isCartOpen: !state.isCartOpen })),
  toggleSearch: () => set((state) => ({ isSearchOpen: !state.isSearchOpen })),
  closeAll: () => set({ isMenuOpen: false, isCartOpen: false, isSearchOpen: false }),
}))
