import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (data) => api.post('/auth/register', data),
  getProfile: () => api.get('/auth/me'),
}

// Products API
export const productsAPI = {
  getAll: (params) => api.get('/product/list', { params }),
  getById: (id) => api.get(`/product/${id}`),
  getCategories: () => api.get('/product/categories'),
  search: (query) => api.get('/search/products', { params: { q: query } }),
}

// Cart API
export const cartAPI = {
  get: () => api.get('/cart/'),
  add: (data) => api.post('/cart/add', data),
  update: (productId, size, data) => api.put(`/cart/update/${productId}/${size}`, data),
  remove: (productId, size) => api.delete(`/cart/remove/${productId}/${size}`),
  clear: () => api.delete('/cart/clear'),
  getCount: () => api.get('/cart/count'),
}

// Wishlist API
export const wishlistAPI = {
  get: () => api.get('/wishlist/'),
  add: (productId) => api.post(`/wishlist/add/${productId}`),
  remove: (productId) => api.delete(`/wishlist/remove/${productId}`),
  check: (productId) => api.get(`/wishlist/check/${productId}`),
  share: () => api.post('/wishlist/share'),
}

// Orders API
export const ordersAPI = {
  create: (data) => api.post('/order/create', data),
  getHistory: () => api.get('/order/history'),
  getById: (orderId) => api.get(`/order/${orderId}`),
}

// Payment API
export const paymentAPI = {
  create: (orderId) => api.post('/payment/create', { order_id: orderId }),
  verify: (data) => api.post('/payment/verify', data),
  getStatus: (orderId) => api.get(`/payment/status/${orderId}`),
}

// Search API
export const searchAPI = {
  products: (query, params) => api.get('/search/products', { params: { q: query, ...params } }),
  suggestions: (query) => api.get('/search/suggestions', { params: { q: query } }),
  trending: () => api.get('/search/trending'),
}

// Recommendations API
export const recommendationsAPI = {
  forYou: (params) => api.get('/recommendations/for-you', { params }),
  similar: (productId) => api.get(`/recommendations/similar/${productId}`),
  frequentlyBought: (productId) => api.get(`/recommendations/frequently-bought-together/${productId}`),
  trending: () => api.get('/recommendations/trending'),
}

// Reviews API
export const reviewsAPI = {
  getByProduct: (productId) => api.get(`/reviews/${productId}`),
  get: (productId) => api.get(`/reviews/${productId}`),
  add: (productId, data) => api.post(`/reviews/${productId}`, data),
}

// AR API
export const arAPI = {
  logTryOn: (data) => api.post('/ar/try-on/log', data),
  getSizeChart: () => api.get('/ar/size-chart'),
  getSizeRecommendation: (data) => api.post('/ar/size-recommendation', data),
  saveWristMeasurement: (data) => api.post('/ar/wrist-measurement', data),
}

// Admin - Users API
export const usersAPI = {
  getAll: (params) => api.get('/admin/users', { params }),
  getById: (userId) => api.get(`/admin/users/${userId}`),
  updateRole: (userId, role) => api.patch(`/admin/users/${userId}/role`, { role }),
  toggleStatus: (userId, isActive) => api.patch(`/admin/users/${userId}/status`, { is_active: isActive }),
}

// Admin - Coupons API
export const couponsAPI = {
  getAll: () => api.get('/admin/coupons'),
  create: (data) => api.post('/admin/coupons', data),
  update: (couponId, data) => api.put(`/admin/coupons/${couponId}`, data),
  delete: (couponId) => api.delete(`/admin/coupons/${couponId}`),
  toggle: (couponId, isActive) => api.patch(`/admin/coupons/${couponId}/toggle`, { is_active: isActive }),
  validate: (code) => api.post('/coupons/validate', { code }),
}

// Admin - Analytics API
export const analyticsAPI = {
  getStats: () => api.get('/admin/analytics/stats'),
  getSalesData: (period) => api.get('/admin/analytics/sales', { params: { period } }),
  getARMetrics: () => api.get('/admin/analytics/ar'),
  getTopProducts: () => api.get('/admin/analytics/top-products'),
}

// Admin - Settings API
export const settingsAPI = {
  get: () => api.get('/admin/settings'),
  update: (data) => api.put('/admin/settings', data),
  getPayment: () => api.get('/admin/settings/payment'),
  updatePayment: (data) => api.put('/admin/settings/payment', data),
  getShipping: () => api.get('/admin/settings/shipping'),
  updateShipping: (data) => api.put('/admin/settings/shipping', data),
}

// Extended Orders API for admin
Object.assign(ordersAPI, {
  getAll: (params) => api.get('/admin/orders', { params }),
  updateStatus: (orderId, status) => api.patch(`/admin/orders/${orderId}/status`, { status }),
})

// Extended Reviews API for admin
Object.assign(reviewsAPI, {
  getAll: (params) => api.get('/admin/reviews', { params }),
  moderate: (reviewId, action) => api.patch(`/admin/reviews/${reviewId}/moderate`, { action }),
})

// Extended Products API for admin
Object.assign(productsAPI, {
  create: (data) => api.post('/admin/products', data),
  update: (productId, data) => api.put(`/admin/products/${productId}`, data),
  delete: (productId) => api.delete(`/admin/products/${productId}`),
  updateStock: (productId, stock) => api.patch(`/admin/products/${productId}/stock`, { stock }),
})

export default api

