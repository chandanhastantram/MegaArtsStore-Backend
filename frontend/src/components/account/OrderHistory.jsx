import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ordersAPI } from '../../services/api'
import { StatusBadge } from '../common/Badge'
import Modal from '../common/Modal'
import Button from '../common/Button'
import './OrderHistory.css'

export default function OrderHistory() {
  const [selectedOrder, setSelectedOrder] = useState(null)
  
  const { data, isLoading } = useQuery({
    queryKey: ['order-history'],
    queryFn: () => ordersAPI.getHistory()
  })

  const orders = data?.data || []

  if (isLoading) {
    return (
      <div className="orders-loading">
        <div className="spinner"></div>
        <p>Loading orders...</p>
      </div>
    )
  }

  if (orders.length === 0) {
    return (
      <div className="orders-empty">
        <div className="empty-icon">📦</div>
        <h3>No orders yet</h3>
        <p>Start shopping to see your orders here!</p>
        <Button variant="primary" onClick={() => window.location.href = '/products'}>
          Browse Products
        </Button>
      </div>
    )
  }

  return (
    <div className="order-history">
      <div className="orders-list">
        {orders.map((order, index) => (
          <motion.div
            key={order.id}
            className="order-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <div className="order-header">
              <div>
                <span className="order-id">Order #{order.id?.slice(-8)}</span>
                <span className="order-date">
                  {new Date(order.created_at).toLocaleDateString('en-IN', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </span>
              </div>
              <StatusBadge status={order.status} />
            </div>

            <div className="order-items-preview">
              {order.items?.slice(0, 3).map((item, i) => (
                <div key={i} className="preview-item">
                  <img src={item.image || '/placeholder.jpg'} alt={item.name} />
                </div>
              ))}
              {order.items?.length > 3 && (
                <div className="more-items">+{order.items.length - 3}</div>
              )}
            </div>

            <div className="order-summary">
              <div className="order-total">
                <span>Total</span>
                <strong className="gradient-text">₹{order.total?.toLocaleString()}</strong>
              </div>
              <div className="order-actions">
                <Button 
                  variant="secondary" 
                  size="small"
                  onClick={() => setSelectedOrder(order)}
                >
                  View Details
                </Button>
                {order.status === 'delivered' && (
                  <Button variant="primary" size="small">
                    Reorder
                  </Button>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Order Details Modal */}
      <Modal 
        isOpen={!!selectedOrder} 
        onClose={() => setSelectedOrder(null)}
        title={`Order #${selectedOrder?.id?.slice(-8)}`}
        size="large"
      >
        {selectedOrder && <OrderDetails order={selectedOrder} />}
      </Modal>
    </div>
  )
}

function OrderDetails({ order }) {
  return (
    <div className="order-details">
      {/* Status Timeline */}
      <div className="order-timeline">
        <TimelineStep 
          status="completed" 
          label="Order Placed" 
          date={order.created_at}
        />
        <TimelineStep 
          status={['processing', 'shipped', 'delivered'].includes(order.status) ? 'completed' : 'pending'} 
          label="Processing" 
        />
        <TimelineStep 
          status={['shipped', 'delivered'].includes(order.status) ? 'completed' : 'pending'} 
          label="Shipped" 
        />
        <TimelineStep 
          status={order.status === 'delivered' ? 'completed' : 'pending'} 
          label="Delivered" 
        />
      </div>

      {/* Items */}
      <div className="order-items-list">
        <h4>Items</h4>
        {order.items?.map((item, index) => (
          <div key={index} className="order-item">
            <img src={item.image || '/placeholder.jpg'} alt={item.name} />
            <div className="item-info">
              <span className="item-name">{item.name}</span>
              {item.size && <span className="item-size">Size: {item.size}</span>}
              <span className="item-qty">Qty: {item.quantity}</span>
            </div>
            <span className="item-price">₹{(item.price * item.quantity).toLocaleString()}</span>
          </div>
        ))}
      </div>

      {/* Shipping Address */}
      <div className="shipping-info">
        <h4>Shipping Address</h4>
        <p>
          {order.shipping_address?.fullName}<br />
          {order.shipping_address?.addressLine1}<br />
          {order.shipping_address?.city}, {order.shipping_address?.state} {order.shipping_address?.pincode}<br />
          Phone: {order.shipping_address?.phone}
        </p>
      </div>

      {/* Payment Info */}
      <div className="payment-info">
        <h4>Payment</h4>
        <div className="payment-row">
          <span>Subtotal</span>
          <span>₹{order.subtotal?.toLocaleString()}</span>
        </div>
        <div className="payment-row">
          <span>Tax</span>
          <span>₹{order.tax?.toLocaleString()}</span>
        </div>
        <div className="payment-row">
          <span>Shipping</span>
          <span>{order.shipping === 0 ? 'FREE' : `₹${order.shipping}`}</span>
        </div>
        {order.discount > 0 && (
          <div className="payment-row discount">
            <span>Discount</span>
            <span>-₹{order.discount?.toLocaleString()}</span>
          </div>
        )}
        <div className="payment-row total">
          <span>Total</span>
          <strong>₹{order.total?.toLocaleString()}</strong>
        </div>
      </div>
    </div>
  )
}

function TimelineStep({ status, label, date }) {
  return (
    <div className={`timeline-step ${status}`}>
      <div className="timeline-dot" />
      <div className="timeline-content">
        <span className="timeline-label">{label}</span>
        {date && (
          <span className="timeline-date">
            {new Date(date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })}
          </span>
        )}
      </div>
    </div>
  )
}
