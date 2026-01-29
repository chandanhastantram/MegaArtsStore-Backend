import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance with admin token
const adminAPI = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
adminAPI.interceptors.request.use((config) => {
  const adminStorage = localStorage.getItem('admin-storage')
  if (adminStorage) {
    const { state } = JSON.parse(adminStorage)
    if (state?.token) {
      config.headers.Authorization = `Bearer ${state.token}`
    }
  }
  return config
})

// Admin endpoints
export const adminService = {
  // Dashboard
  getOverview: () => adminAPI.get('/admin/overview'),
  getSalesReport: (days = 30) => adminAPI.get(`/admin/sales-report?days=${days}`),
  getTopProducts: (limit = 10, days = 30) => 
    adminAPI.get(`/admin/top-products?limit=${limit}&days=${days}`),
  getInventoryAlerts: (threshold = 10) => 
    adminAPI.get(`/admin/inventory-alerts?threshold=${threshold}`),
  getUserStats: (days = 30) => adminAPI.get(`/admin/user-stats?days=${days}`),
  getARAnalytics: (days = 30) => adminAPI.get(`/admin/ar-analytics?days=${days}`),
  getOrderStatusBreakdown: (days = 30) => 
    adminAPI.get(`/admin/order-status-breakdown?days=${days}`),
}

export default adminService
