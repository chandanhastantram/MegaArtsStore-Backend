import { motion } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import { useCartStore } from '../store/cartStore'
import Button from '../components/common/Button'
import useToast from '../hooks/useToast'
import './Cart.css'

export default function Cart() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { items, updateQuantity, removeItem, clearCart, getTotal, getItemCount } = useCartStore()

  const handleUpdateQuantity = (id, quantity) => {
    if (quantity < 1) return
    updateQuantity(id, quantity)
  }

  const handleRemoveItem = (item) => {
    removeItem(item.id)
    toast.info(`${item.name} removed from cart`)
  }

  const handleClearCart = () => {
    if (window.confirm('Are you sure you want to clear your cart?')) {
      clearCart()
      toast.success('Cart cleared')
    }
  }

  const subtotal = getTotal()
  const tax = subtotal * 0.18 // 18% GST
  const shipping = subtotal > 5000 ? 0 : 200
  const total = subtotal + tax + shipping

  if (items.length === 0) {
    return (
      <div className="cart-empty">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="empty-icon">🛒</div>
          <h2>Your cart is empty</h2>
          <p>Add some beautiful jewellery to get started!</p>
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
    <div className="cart-page">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="cart-header">
            <h1 className="font-display">Shopping Cart</h1>
            <p className="cart-count">{getItemCount()} items</p>
          </div>

          <div className="cart-layout">
            {/* Cart Items */}
            <div className="cart-items">
              <div className="cart-actions-top">
                <button className="clear-cart-btn" onClick={handleClearCart}>
                  Clear Cart
                </button>
              </div>

              {items.map((item, index) => (
                <motion.div
                  key={item.id}
                  className="cart-item"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Link to={`/product/${item.id}`} className="item-image">
                    <img src={item.images?.[0] || '/placeholder.jpg'} alt={item.name} />
                  </Link>

                  <div className="item-details">
                    <Link to={`/product/${item.id}`}>
                      <h3 className="item-name">{item.name}</h3>
                    </Link>
                    <p className="item-category">{item.category}</p>
                    {item.size && (
                      <p className="item-size">Size: {item.size}</p>
                    )}
                    <p className="item-price gradient-text">₹{item.price.toLocaleString()}</p>
                  </div>

                  <div className="item-quantity">
                    <button
                      className="qty-btn"
                      onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                    >
                      −
                    </button>
                    <span className="qty-value">{item.quantity}</span>
                    <button
                      className="qty-btn"
                      onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                    >
                      +
                    </button>
                  </div>

                  <div className="item-total">
                    <p className="total-price gradient-text">
                      ₹{(item.price * item.quantity).toLocaleString()}
                    </p>
                  </div>

                  <button
                    className="item-remove"
                    onClick={() => handleRemoveItem(item)}
                  >
                    ✕
                  </button>
                </motion.div>
              ))}
            </div>

            {/* Order Summary */}
            <motion.div
              className="order-summary"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <h3>Order Summary</h3>

              <div className="summary-row">
                <span>Subtotal</span>
                <span>₹{subtotal.toLocaleString()}</span>
              </div>

              <div className="summary-row">
                <span>Tax (GST 18%)</span>
                <span>₹{tax.toLocaleString()}</span>
              </div>

              <div className="summary-row">
                <span>Shipping</span>
                <span>{shipping === 0 ? 'FREE' : `₹${shipping}`}</span>
              </div>

              {shipping > 0 && (
                <p className="free-shipping-note">
                  Add ₹{(5000 - subtotal).toLocaleString()} more for FREE shipping!
                </p>
              )}

              <div className="summary-divider"></div>

              <div className="summary-row summary-total">
                <span>Total</span>
                <span className="gradient-text">₹{total.toLocaleString()}</span>
              </div>

              <Button
                variant="primary"
                size="large"
                onClick={() => navigate('/checkout')}
                className="checkout-btn"
              >
                Proceed to Checkout
              </Button>

              <Link to="/products" className="continue-shopping">
                ← Continue Shopping
              </Link>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
