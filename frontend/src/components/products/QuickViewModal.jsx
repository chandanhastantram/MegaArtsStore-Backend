import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Modal from '../common/Modal'
import Button from '../common/Button'
import { useCartStore } from '../../store/cartStore'
import { useWishlistStore } from '../../store/wishlistStore'
import useToast from '../../hooks/useToast'
import './QuickViewModal.css'

export default function QuickViewModal({ product, isOpen, onClose }) {
  const [selectedImage, setSelectedImage] = useState(0)
  const [selectedSize, setSelectedSize] = useState('')
  const [quantity, setQuantity] = useState(1)
  
  const { addItem } = useCartStore()
  const { items: wishlistItems, addItem: addToWishlist, removeItem: removeFromWishlist } = useWishlistStore()
  const { toast } = useToast()

  const isInWishlist = wishlistItems.some(item => item.id === product?.id)
  const images = product?.images || ['/placeholder.jpg']
  const sizes = product?.sizes || []

  const handleAddToCart = () => {
    if (sizes.length > 0 && !selectedSize) {
      toast.error('Please select a size')
      return
    }
    addItem({ ...product, quantity, size: selectedSize })
    toast.success(`${product.name} added to cart!`)
    onClose()
  }

  const handleToggleWishlist = () => {
    if (isInWishlist) {
      removeFromWishlist(product.id)
      toast.info('Removed from wishlist')
    } else {
      addToWishlist(product)
      toast.success('Added to wishlist!')
    }
  }

  if (!product) return null

  const finalPrice = product.discount 
    ? product.price * (1 - product.discount / 100) 
    : product.price

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="large">
      <div className="quick-view-content">
        {/* Images */}
        <div className="quick-view-gallery">
          <motion.img 
            key={selectedImage}
            src={images[selectedImage]} 
            alt={product.name}
            className="quick-view-main-image"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          />
          {product.ar_enabled && (
            <span className="badge badge-gold quick-view-ar-badge">AR Available</span>
          )}
          {images.length > 1 && (
            <div className="quick-view-thumbnails">
              {images.map((img, index) => (
                <button
                  key={index}
                  className={`quick-view-thumb ${selectedImage === index ? 'active' : ''}`}
                  onClick={() => setSelectedImage(index)}
                >
                  <img src={img} alt="" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="quick-view-info">
          <h2 className="quick-view-title font-display">{product.name}</h2>
          <p className="quick-view-category">{product.category}</p>

          {/* Rating */}
          {product.avg_rating > 0 && (
            <div className="quick-view-rating">
              {'⭐'.repeat(Math.round(product.avg_rating))}
              <span>({product.avg_rating.toFixed(1)})</span>
            </div>
          )}

          {/* Price */}
          <div className="quick-view-price">
            {product.discount > 0 ? (
              <>
                <span className="price-original">₹{product.price.toLocaleString()}</span>
                <span className="price-current gradient-text">₹{finalPrice.toLocaleString()}</span>
                <span className="badge badge-sale">-{product.discount}%</span>
              </>
            ) : (
              <span className="price-current gradient-text">₹{product.price.toLocaleString()}</span>
            )}
          </div>

          {/* Description */}
          <p className="quick-view-description">{product.description}</p>

          {/* Size Selector */}
          {sizes.length > 0 && (
            <div className="quick-view-sizes">
              <label>Size:</label>
              <div className="size-options">
                {sizes.map(size => (
                  <button
                    key={size}
                    className={`size-btn ${selectedSize === size ? 'active' : ''}`}
                    onClick={() => setSelectedSize(size)}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Quantity */}
          <div className="quick-view-quantity">
            <label>Quantity:</label>
            <div className="quantity-controls">
              <button onClick={() => setQuantity(Math.max(1, quantity - 1))}>−</button>
              <span>{quantity}</span>
              <button onClick={() => setQuantity(quantity + 1)}>+</button>
            </div>
          </div>

          {/* Actions */}
          <div className="quick-view-actions">
            <Button variant="primary" onClick={handleAddToCart}>
              Add to Cart
            </Button>
            <Button variant="secondary" onClick={handleToggleWishlist}>
              {isInWishlist ? '❤️' : '🤍'}
            </Button>
          </div>

          {/* View Full Details */}
          <Link to={`/product/${product.id}`} className="view-full-link" onClick={onClose}>
            View Full Details →
          </Link>
        </div>
      </div>
    </Modal>
  )
}
