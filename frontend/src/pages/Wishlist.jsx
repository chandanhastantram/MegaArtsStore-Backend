import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { useWishlistStore } from '../store/wishlistStore'
import { useCartStore } from '../store/cartStore'
import ProductCard from '../components/products/ProductCard'
import Button from '../components/common/Button'
import useToast from '../hooks/useToast'
import './Wishlist.css'

export default function Wishlist() {
  const { items, clearWishlist } = useWishlistStore()
  const { addItem } = useCartStore()
  const { toast } = useToast()

  const handleMoveToCart = (product) => {
    addItem(product)
    toast.success(`${product.name} added to cart!`)
  }

  const handleClearWishlist = () => {
    if (window.confirm('Are you sure you want to clear your wishlist?')) {
      clearWishlist()
      toast.info('Wishlist cleared')
    }
  }

  if (items.length === 0) {
    return (
      <div className="wishlist-empty">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="empty-icon">💝</div>
          <h2>Your wishlist is empty</h2>
          <p>Save your favorite items for later!</p>
          <Link to="/products">
            <Button variant="primary" size="large">
              Browse Products
            </Button>
          </Link>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="wishlist-page">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="wishlist-header">
            <div>
              <h1 className="font-display">My Wishlist</h1>
              <p className="wishlist-count">{items.length} items saved</p>
            </div>
            <button className="clear-wishlist-btn" onClick={handleClearWishlist}>
              Clear All
            </button>
          </div>

          <div className="wishlist-grid">
            {items.map((product, index) => (
              <div key={product.id} className="wishlist-item-wrapper">
                <ProductCard product={product} index={index} />
                <Button
                  variant="primary"
                  size="small"
                  onClick={() => handleMoveToCart(product)}
                  className="move-to-cart-btn"
                >
                  Add to Cart
                </Button>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
