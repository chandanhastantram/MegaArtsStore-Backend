import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore } from '../store/authStore'
import { useWishlistStore } from '../store/wishlistStore'
import Button from '../components/common/Button'
import OrderHistory from '../components/account/OrderHistory'
import AddressBook from '../components/account/AddressBook'
import ProfileForm from '../components/account/ProfileForm'
import ProductCard from '../components/products/ProductCard'
import useToast from '../hooks/useToast'
import './Account.css'

export default function Account() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const { toast } = useToast()
  const { user, logout, isAuthenticated } = useAuthStore()
  const { items: wishlistItems, removeItem: removeFromWishlist } = useWishlistStore()
  
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'profile')
  const [addresses, setAddresses] = useState([])

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    }
  }, [isAuthenticated, navigate])

  useEffect(() => {
    const tab = searchParams.get('tab')
    if (tab) setActiveTab(tab)
  }, [searchParams])

  const handleTabChange = (tab) => {
    setActiveTab(tab)
    setSearchParams({ tab })
  }

  const handleLogout = () => {
    logout()
    toast.success('Logged out successfully')
    navigate('/')
  }

  // Address handlers
  const handleAddAddress = (address) => {
    setAddresses(prev => [...prev, { ...address, id: Date.now().toString() }])
  }

  const handleEditAddress = (id, address) => {
    setAddresses(prev => prev.map(a => a.id === id ? { ...a, ...address } : a))
  }

  const handleDeleteAddress = (id) => {
    setAddresses(prev => prev.filter(a => a.id !== id))
  }

  const handleSetDefaultAddress = (id) => {
    setAddresses(prev => prev.map(a => ({ ...a, isDefault: a.id === id })))
    toast.success('Default address updated')
  }

  if (!user) return null

  const tabs = [
    { id: 'profile', label: 'Profile', icon: '👤' },
    { id: 'orders', label: 'Orders', icon: '📦' },
    { id: 'wishlist', label: 'Wishlist', icon: '❤️', count: wishlistItems.length },
    { id: 'addresses', label: 'Addresses', icon: '📍' },
  ]

  return (
    <div className="account-page">
      <div className="account-container">
        {/* Sidebar */}
        <motion.div 
          className="account-sidebar"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <div className="user-info">
            <div className="user-avatar">
              {user.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <h3>{user.name}</h3>
            <p>{user.email}</p>
          </div>

          <nav className="account-nav">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={activeTab === tab.id ? 'active' : ''}
                onClick={() => handleTabChange(tab.id)}
              >
                <span className="tab-icon">{tab.icon}</span>
                <span>{tab.label}</span>
                {tab.count > 0 && (
                  <span className="tab-count">{tab.count}</span>
                )}
              </button>
            ))}
          </nav>

          <Button onClick={handleLogout} variant="secondary" className="logout-btn">
            Logout
          </Button>
        </motion.div>

        {/* Content */}
        <motion.div 
          className="account-content"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {activeTab === 'profile' && (
            <div className="tab-content">
              <h2 className="tab-title font-display">My Profile</h2>
              <ProfileForm />
            </div>
          )}

          {activeTab === 'orders' && (
            <div className="tab-content">
              <h2 className="tab-title font-display">Order History</h2>
              <OrderHistory />
            </div>
          )}

          {activeTab === 'wishlist' && (
            <div className="tab-content">
              <h2 className="tab-title font-display">My Wishlist</h2>
              {wishlistItems.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">❤️</div>
                  <h3>Your wishlist is empty</h3>
                  <p>Save items you love by clicking the heart icon</p>
                  <Link to="/products">
                    <Button variant="primary">Browse Products</Button>
                  </Link>
                </div>
              ) : (
                <div className="wishlist-grid">
                  {wishlistItems.map((product, index) => (
                    <ProductCard key={product.id} product={product} index={index} />
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'addresses' && (
            <div className="tab-content">
              <h2 className="tab-title font-display">My Addresses</h2>
              <AddressBook
                addresses={addresses}
                onAdd={handleAddAddress}
                onEdit={handleEditAddress}
                onDelete={handleDeleteAddress}
                onSetDefault={handleSetDefaultAddress}
              />
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}
