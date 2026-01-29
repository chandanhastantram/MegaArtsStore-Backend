import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authAPI } from '../services/api'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: async (email, password) => {
        try {
          const response = await authAPI.login({ email, password })
          const { user, token } = response.data
          
          set({
            user,
            token,
            isAuthenticated: true
          })
          
          // Set token in axios defaults
          if (typeof window !== 'undefined') {
            localStorage.setItem('token', token)
          }
          
          return response
        } catch (error) {
          throw error
        }
      },
      
      register: async (name, email, password) => {
        try {
          const response = await authAPI.register({ name, email, password })
          const { user, token } = response.data
          
          set({
            user,
            token,
            isAuthenticated: true
          })
          
          // Set token in axios defaults
          if (typeof window !== 'undefined') {
            localStorage.setItem('token', token)
          }
          
          return response
        } catch (error) {
          throw error
        }
      },
      
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false
        })
        
        // Remove token from storage
        if (typeof window !== 'undefined') {
          localStorage.removeItem('token')
        }
      },
      
      updateUser: (userData) => {
        set({ user: { ...get().user, ...userData } })
      }
    }),
    {
      name: 'auth-storage'
    }
  )
)
