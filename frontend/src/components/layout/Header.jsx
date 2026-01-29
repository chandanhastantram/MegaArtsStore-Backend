import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore, useCartStore, useUIStore } from '../../store'
import './Header.css'

export default function Header() {
  const { isAuthenticated, user } = useAuthStore()
  const { count } = useCartStore()
  const { isMenuOpen, toggleMenu, toggleCart, toggleSearch } = useUIStore()

  return (
    <motion.header 
      className="header glass"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="container">
        <div className="header-content">
          {/* Logo */}
          <Link to="/" className="logo">
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="logo-icon">💎</span>
              <span className="logo-text gradient-text">MegaArts</span>
            </motion.div>
          </Link>

          {/* Navigation */}
          <nav className={`nav ${isMenuOpen ? 'nav-open' : ''}`}>
            <Link to="/products" className="nav-link">Shop All</Link>
            <Link to="/products/bangles" className="nav-link">Bangles</Link>
            <Link to="/products/rings" className="nav-link">Rings</Link>
            <Link to="/products/necklaces" className="nav-link">Necklaces</Link>
            <Link to="/products/earrings" className="nav-link">Earrings</Link>
          </nav>

          {/* Actions */}
          <div className="header-actions">
            <button 
              className="icon-btn" 
              onClick={toggleSearch}
              aria-label="Search"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16zM19 19l-4.35-4.35" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </button>

            <Link to="/wishlist" className="icon-btn" aria-label="Wishlist">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 18.35l-1.45-1.32C3.4 12.36 0 9.28 0 5.5 0 2.42 2.42 0 5.5 0 7.24 0 8.91 0.81 10 2.09 11.09 0.81 12.76 0 14.5 0 17.58 0 20 2.42 20 5.5c0 3.78-3.4 6.86-8.55 11.54L10 18.35z" fill="currentColor"/>
              </svg>
            </Link>

            <button 
              className="icon-btn cart-btn" 
              onClick={toggleCart}
              aria-label="Cart"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M6 2L3 6v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V6l-3-4H6zM3 6h14M14 10a4 4 0 1 1-8 0" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              {count > 0 && <span className="cart-count">{count}</span>}
            </button>

            {isAuthenticated ? (
              <Link to="/account" className="icon-btn" aria-label="Account">
                <div className="avatar">
                  {user?.name?.[0] || 'U'}
                </div>
              </Link>
            ) : (
              <Link to="/login" className="btn btn-primary btn-sm">
                Login
              </Link>
            )}

            <button 
              className="menu-toggle" 
              onClick={toggleMenu}
              aria-label="Menu"
            >
              <span></span>
              <span></span>
              <span></span>
            </button>
          </div>
        </div>
      </div>
    </motion.header>
  )
}
