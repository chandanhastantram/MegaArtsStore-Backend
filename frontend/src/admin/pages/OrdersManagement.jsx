import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ordersAPI } from '../../services/api'
import { StatusBadge } from '../../components/common/Badge'
import Modal from '../../components/common/Modal'
import Button from '../../components/common/Button'
import { TableRowSkeleton } from '../../components/common/Skeleton'
import useToast from '../../hooks/useToast'
import './OrdersManagement.css'

export default function OrdersManagement() {
  const [selectedOrder, setSelectedOrder] = useState(null)
  const [filterStatus, setFilterStatus] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['admin-orders', filterStatus],
    queryFn: () => ordersAPI.getAll?.({ status: filterStatus !== 'all' ? filterStatus : undefined })
  })

  const updateStatusMutation = useMutation({
    mutationFn: ({ orderId, status }) => ordersAPI.updateStatus?.(orderId, status),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-orders'])
      toast.success('Order status updated')
      setSelectedOrder(null)
    },
    onError: () => toast.error('Failed to update order status')
  })

  const orders = data?.data || []
  const filteredOrders = orders.filter(order => 
    order.id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    order.customer_name?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const statusOptions = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']

  return (
    <div className="orders-management">
      <div className="page-header">
        <h1>Orders Management</h1>
        <p>Manage and track customer orders</p>
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search orders..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-tabs">
          {['all', ...statusOptions].map(status => (
            <button
              key={status}
              className={filterStatus === status ? 'active' : ''}
              onClick={() => setFilterStatus(status)}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Orders Table */}
      <div className="table-container">
        <table className="orders-table">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Customer</th>
              <th>Items</th>
              <th>Total</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRowSkeleton key={i} columns={7} />
              ))
            ) : filteredOrders.length === 0 ? (
              <tr>
                <td colSpan={7} className="empty-row">
                  No orders found
                </td>
              </tr>
            ) : (
              filteredOrders.map((order, index) => (
                <motion.tr
                  key={order.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.03 }}
                >
                  <td className="order-id">#{order.id?.slice(-8).toUpperCase()}</td>
                  <td>
                    <div className="customer-info">
                      <span className="customer-name">{order.customer_name || 'N/A'}</span>
                      <span className="customer-email">{order.customer_email}</span>
                    </div>
                  </td>
                  <td>{order.items?.length || 0} items</td>
                  <td className="order-total">₹{order.total?.toLocaleString()}</td>
                  <td><StatusBadge status={order.status} /></td>
                  <td className="order-date">
                    {new Date(order.created_at).toLocaleDateString('en-IN', {
                      day: 'numeric',
                      month: 'short',
                      year: 'numeric'
                    })}
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="action-btn view"
                        onClick={() => setSelectedOrder(order)}
                      >
                        View
                      </button>
                    </div>
                  </td>
                </motion.tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Order Details Modal */}
      <Modal
        isOpen={!!selectedOrder}
        onClose={() => setSelectedOrder(null)}
        title={`Order #${selectedOrder?.id?.slice(-8).toUpperCase()}`}
        size="large"
      >
        {selectedOrder && (
          <div className="order-details-modal">
            {/* Status Update */}
            <div className="status-update-section">
              <label>Update Status:</label>
              <div className="status-buttons">
                {statusOptions.map(status => (
                  <button
                    key={status}
                    className={`status-btn ${selectedOrder.status === status ? 'active' : ''}`}
                    onClick={() => updateStatusMutation.mutate({ 
                      orderId: selectedOrder.id, 
                      status 
                    })}
                    disabled={updateStatusMutation.isPending}
                  >
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Customer Info */}
            <div className="detail-section">
              <h4>Customer Information</h4>
              <p><strong>Name:</strong> {selectedOrder.customer_name}</p>
              <p><strong>Email:</strong> {selectedOrder.customer_email}</p>
              <p><strong>Phone:</strong> {selectedOrder.shipping_address?.phone}</p>
            </div>

            {/* Shipping Address */}
            <div className="detail-section">
              <h4>Shipping Address</h4>
              <p>
                {selectedOrder.shipping_address?.addressLine1}<br />
                {selectedOrder.shipping_address?.city}, {selectedOrder.shipping_address?.state} {selectedOrder.shipping_address?.pincode}
              </p>
            </div>

            {/* Order Items */}
            <div className="detail-section">
              <h4>Order Items</h4>
              <div className="order-items-list">
                {selectedOrder.items?.map((item, index) => (
                  <div key={index} className="order-item">
                    <img src={item.image || '/placeholder.jpg'} alt={item.name} />
                    <div className="item-details">
                      <span className="item-name">{item.name}</span>
                      <span className="item-meta">
                        Qty: {item.quantity} {item.size && `• Size: ${item.size}`}
                      </span>
                    </div>
                    <span className="item-price">₹{(item.price * item.quantity).toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Order Summary */}
            <div className="order-summary-section">
              <div className="summary-row">
                <span>Subtotal</span>
                <span>₹{selectedOrder.subtotal?.toLocaleString()}</span>
              </div>
              <div className="summary-row">
                <span>Shipping</span>
                <span>{selectedOrder.shipping === 0 ? 'FREE' : `₹${selectedOrder.shipping}`}</span>
              </div>
              {selectedOrder.discount > 0 && (
                <div className="summary-row discount">
                  <span>Discount</span>
                  <span>-₹{selectedOrder.discount?.toLocaleString()}</span>
                </div>
              )}
              <div className="summary-row total">
                <span>Total</span>
                <strong>₹{selectedOrder.total?.toLocaleString()}</strong>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
