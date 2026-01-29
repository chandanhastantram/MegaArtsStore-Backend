import { Routes, Route } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import Layout from './components/layout/Layout'
import Home from './pages/Home'
import Products from './pages/Products'
import ProductDetail from './pages/ProductDetail'
import Cart from './pages/Cart'
import Checkout from './pages/Checkout'
import Login from './pages/Login'
import Register from './pages/Register'
import ForgotPassword from './pages/ForgotPassword'
import Account from './pages/Account'
import Wishlist from './pages/Wishlist'
import Search from './pages/Search'
import ARTryOn from './pages/ARTryOn'
import OrderConfirmation from './pages/OrderConfirmation'
import NotFound from './pages/NotFound'

// Admin imports
import AdminLogin from './admin/pages/AdminLogin'
import AdminLayout from './admin/components/AdminLayout'
import AdminRoute from './admin/components/AdminRoute'
import AdminDashboard from './admin/pages/AdminDashboard'
import ProductsManagement from './admin/pages/ProductsManagement'
import OrdersManagement from './admin/pages/OrdersManagement'
import UsersManagement from './admin/pages/UsersManagement'
import InventoryManagement from './admin/pages/InventoryManagement'
import CouponsManagement from './admin/pages/CouponsManagement'
import ReviewsModeration from './admin/pages/ReviewsModeration'
import Analytics from './admin/pages/Analytics'
import Settings from './admin/pages/Settings'

function App() {
  return (
    <AnimatePresence mode="wait">
      <Routes>
        {/* Customer Routes */}
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="products" element={<Products />} />
          <Route path="products/:category" element={<Products />} />
          <Route path="product/:id" element={<ProductDetail />} />
          <Route path="cart" element={<Cart />} />
          <Route path="checkout" element={<Checkout />} />
          <Route path="order-confirmation" element={<OrderConfirmation />} />
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
          <Route path="forgot-password" element={<ForgotPassword />} />
          <Route path="account" element={<Account />} />
          <Route path="wishlist" element={<Wishlist />} />
          <Route path="search" element={<Search />} />
          <Route path="ar-try-on/:id" element={<ARTryOn />} />
          <Route path="*" element={<NotFound />} />
        </Route>

        {/* Admin Routes */}
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin" element={<AdminRoute><AdminLayout /></AdminRoute>}>
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="products" element={<ProductsManagement />} />
          <Route path="orders" element={<OrdersManagement />} />
          <Route path="users" element={<UsersManagement />} />
          <Route path="inventory" element={<InventoryManagement />} />
          <Route path="coupons" element={<CouponsManagement />} />
          <Route path="reviews" element={<ReviewsModeration />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </AnimatePresence>
  )
}

export default App
