import { useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import Button from '../components/common/Button'
import { useCartStore } from '../store/cartStore'
import './OrderConfirmation.css'

export default function OrderConfirmation() {
  const [searchParams] = useSearchParams()
  const orderId = searchParams.get('order_id')
  const { clearCart } = useCartStore()

  useEffect(() => {
    // Clear cart on successful order
    clearCart()
  }, [clearCart])

  return (
    <div className="order-confirmation-page">
      <motion.div 
        className="confirmation-container"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <motion.div 
          className="success-animation"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
        >
          <div className="success-circle">
            <span className="success-icon">✓</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h1 className="font-display">Order Confirmed!</h1>
          <p className="confirmation-message">
            Thank you for your purchase. Your order has been placed successfully.
          </p>

          {orderId && (
            <div className="order-id-display">
              <span className="label">Order ID</span>
              <span className="value">#{orderId.slice(-8).toUpperCase()}</span>
            </div>
          )}

          <div className="confirmation-details">
            <div className="detail-item">
              <span className="detail-icon">📧</span>
              <p>You will receive an email confirmation shortly</p>
            </div>
            <div className="detail-item">
              <span className="detail-icon">📦</span>
              <p>Track your order from your account dashboard</p>
            </div>
            <div className="detail-item">
              <span className="detail-icon">🚚</span>
              <p>Estimated delivery: 5-7 business days</p>
            </div>
          </div>

          <div className="confirmation-actions">
            <Link to="/account?tab=orders">
              <Button variant="primary" size="large">
                View My Orders
              </Button>
            </Link>
            <Link to="/products">
              <Button variant="secondary" size="large">
                Continue Shopping
              </Button>
            </Link>
          </div>
        </motion.div>
      </motion.div>
    </div>
  )
}
