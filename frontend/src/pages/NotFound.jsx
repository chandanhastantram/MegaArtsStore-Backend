import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Button from '../components/common/Button'
import './NotFound.css'

export default function NotFound() {
  return (
    <div className="not-found-page">
      <motion.div
        className="not-found-content"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <motion.h1
          className="not-found-title font-display gradient-text"
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          404
        </motion.h1>
        <h2>Page Not Found</h2>
        <p>The page you're looking for doesn't exist or has been moved.</p>
        
        <div className="not-found-actions">
          <Link to="/">
            <Button variant="primary" size="large">
              Go Home
            </Button>
          </Link>
          <Link to="/products">
            <Button variant="secondary" size="large">
              Browse Products
            </Button>
          </Link>
        </div>

        <div className="popular-links">
          <h3>Popular Pages</h3>
          <div className="links-grid">
            <Link to="/products/bangles">Bangles</Link>
            <Link to="/products/rings">Rings</Link>
            <Link to="/products/necklaces">Necklaces</Link>
            <Link to="/products/earrings">Earrings</Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
