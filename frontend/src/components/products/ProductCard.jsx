import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { useState } from 'react'
import Modal from '../common/Modal'
import Button from '../common/Button'
import useToast from '../../hooks/useToast'
import { useCartStore } from '../../store/cartStore'
import { useWishlistStore } from '../../store/wishlistStore'
import './ProductCard.css'

export default function ProductCard({ product, index = 0 }) {
  const [showQuickView, setShowQuickView] = useState(false)
  const { toast } = useToast()
  const { addItem } = useCartStore()
  const { items: wishlistItems, addItem: addToWishlist, removeItem: removeFromWishlist } = useWishlistStore()
  
  const isInWishlist = wishlistItems.some(item => item.id === product.id)

  const handleAddToCart = (e) => {
    e.preventDefault()
    addItem(product)
    toast.success(`${product.name} added to cart!`)
  }

  const handleToggleWishlist = (e) => {
    e.preventDefault()
    if (isInWishlist) {
      removeFromWishlist(product.id)
      toast.info('Removed from wishlist')
    } else {
      addToWishlist(product)
      toast.success('Added to wishlist!')
    }
  }

  return (
    <>
      <motion.div
        className="product-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.05 }}
        whileHover={{ y: -8 }}
      >
        <Link to={`/product/${product.id}`} className="product-card-link">
          <div className="product-card-image">
            {product.ar_enabled && (
              <span className="badge badge-gold ar-badge">AR</span>
            )}
            {product.discount > 0 && (
              <span className="badge badge-sale discount-badge">-{product.discount}%</span>
            )}
            <motion.button
              className={`wishlist-btn ${isInWishlist ? 'active' : ''}`}
              onClick={handleToggleWishlist}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              {isInWishlist ? '❤️' : '🤍'}
            </motion.button>
            <img 
              src={product.images?.[0] || '/placeholder.jpg'} 
              alt={product.name}
              loading="lazy"
            />
            <div className="product-card-overlay">
              <Button 
                variant="dark" 
                size="small"
                onClick={(e) => {
                  e.preventDefault()
                  setShowQuickView(true)
                }}
              >
                Quick View
              </Button>
            </div>
          </div>
          
          <div className="product-card-info">
            <h3 className="product-card-name">{product.name}</h3>
            <p className="product-card-category">{product.category}</p>
            
            <div className="product-card-footer">
              <div className="product-card-price">
                {product.discount > 0 ? (
                  <>
                    <span className="price-original">₹{product.price.toLocaleString()}</span>
                    <span className="price-discounted gradient-text">
                      ₹{(product.price * (1 - product.discount / 100)).toLocaleString()}
                    </span>
                  </>
                ) : (
                  <span className="price gradient-text">₹{product.price.toLocaleString()}</span>
                )}
              </div>
              
              {product.avg_rating > 0 && (
                <div className="product-card-rating">
                  <span className="rating-stars">⭐</span>
                  <span className="rating-value">{product.avg_rating.toFixed(1)}</span>
                </div>
              )}
            </div>
          </div>
        </Link>
      </motion.div>

      {/* Quick View Modal */}
      <Modal 
        isOpen={showQuickView} 
        onClose={() => setShowQuickView(false)}
        size="large"
      >
        <div className="quick-view">
          <div className="quick-view-image">
            <img src={product.images?.[0] || '/placeholder.jpg'} alt={product.name} />
          </div>
          <div className="quick-view-details">
            <h2 className="font-display">{product.name}</h2>
            <p className="quick-view-category">{product.category}</p>
            
            <div className="quick-view-price">
              {product.discount > 0 ? (
                <>
                  <span className="price-original">₹{product.price.toLocaleString()}</span>
                  <span className="price-discounted gradient-text">
                    ₹{(product.price * (1 - product.discount / 100)).toLocaleString()}
                  </span>
                </>
              ) : (
                <span className="price gradient-text">₹{product.price.toLocaleString()}</span>
              )}
            </div>

            <p className="quick-view-description">{product.description}</p>

            <div className="quick-view-actions">
              <Button variant="primary" onClick={handleAddToCart}>
                Add to Cart
              </Button>
              <Link to={`/product/${product.id}`}>
                <Button variant="secondary">View Details</Button>
              </Link>
            </div>
          </div>
        </div>
      </Modal>
    </>
  )
}
