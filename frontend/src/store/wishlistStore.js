import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useWishlistStore = create(
  persist(
    (set, get) => ({
      items: [],
      
      addItem: (product) => {
        const items = get().items
        const exists = items.find(item => item.id === product.id)
        
        if (!exists) {
          set({ items: [...items, product] })
        }
      },
      
      removeItem: (productId) => {
        set({ items: get().items.filter(item => item.id !== productId) })
      },
      
      clearWishlist: () => {
        set({ items: [] })
      },
      
      isInWishlist: (productId) => {
        return get().items.some(item => item.id === productId)
      }
    }),
    {
      name: 'wishlist-storage'
    }
  )
)
