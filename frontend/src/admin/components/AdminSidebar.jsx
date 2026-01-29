import { Link, useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import useAdminStore from '../../store/adminStore'
import useToast from '../../hooks/useToast'
import './AdminSidebar.css'

export default function AdminSidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const { toast } = useToast()
  const { admin, logout } = useAdminStore()

  const menuItems = [
    { path: '/admin/dashboard', icon: '📊', label: 'Dashboard' },
    { path: '/admin/products', icon: '📦', label: 'Products' },
    { path: '/admin/orders', icon: '🛒', label: 'Orders' },
    { path: '/admin/users', icon: '👥', label: 'Users' },
    { path: '/admin/inventory', icon: '📋', label: 'Inventory' },
    { path: '/admin/coupons', icon: '🎟️', label: 'Coupons' },
    { path: '/admin/reviews', icon: '⭐', label: 'Reviews' },
    { path: '/admin/analytics', icon: '📈', label: 'Analytics' },
    { path: '/admin/settings', icon: '⚙️', label: 'Settings' },
  ]

  const handleLogout = () => {
    logout()
    toast.success('Logged out successfully')
    navigate('/admin/login')
  }

  return (
    <div className="admin-sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <span className="logo-icon">👑</span>
          <h2>MegaArts Admin</h2>
        </div>
        <div className="admin-info">
          <div className="admin-avatar">
            {admin?.name?.charAt(0).toUpperCase() || 'A'}
          </div>
          <div className="admin-details">
            <p className="admin-name">{admin?.name || 'Admin'}</p>
            <p className="admin-role">{admin?.role || 'Administrator'}</p>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </Link>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button onClick={handleLogout} className="logout-btn">
          <span>🚪</span>
          <span>Logout</span>
        </button>
      </div>
    </div>
  )
}
