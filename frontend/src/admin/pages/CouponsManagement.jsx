import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { couponsAPI } from '../../services/api'
import { StatusBadge } from '../../components/common/Badge'
import Modal from '../../components/common/Modal'
import Button from '../../components/common/Button'
import useToast from '../../hooks/useToast'
import './CouponsManagement.css'

export default function CouponsManagement() {
  const [showForm, setShowForm] = useState(false)
  const [editingCoupon, setEditingCoupon] = useState(null)
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['admin-coupons'],
    queryFn: () => couponsAPI.getAll?.()
  })

  const createMutation = useMutation({
    mutationFn: (data) => couponsAPI.create?.(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-coupons'])
      toast.success('Coupon created successfully')
      setShowForm(false)
    },
    onError: () => toast.error('Failed to create coupon')
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => couponsAPI.update?.(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-coupons'])
      toast.success('Coupon updated')
      setShowForm(false)
      setEditingCoupon(null)
    },
    onError: () => toast.error('Failed to update coupon')
  })

  const toggleMutation = useMutation({
    mutationFn: ({ id, isActive }) => couponsAPI.toggle?.(id, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-coupons'])
      toast.success('Coupon status updated')
    }
  })

  const coupons = data?.data || []

  const handleEdit = (coupon) => {
    setEditingCoupon(coupon)
    setShowForm(true)
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setEditingCoupon(null)
  }

  return (
    <div className="coupons-management">
      <div className="page-header">
        <div>
          <h1>Coupons Management</h1>
          <p>Create and manage discount codes</p>
        </div>
        <Button variant="primary" onClick={() => setShowForm(true)}>
          + Create Coupon
        </Button>
      </div>

      {/* Stats */}
      <div className="coupons-stats">
        <div className="stat-card">
          <span className="stat-icon">🎟️</span>
          <div>
            <span className="stat-value">{coupons.length}</span>
            <span className="stat-label">Total Coupons</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">✅</span>
          <div>
            <span className="stat-value">{coupons.filter(c => c.is_active).length}</span>
            <span className="stat-label">Active</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">📊</span>
          <div>
            <span className="stat-value">{coupons.reduce((sum, c) => sum + (c.usage_count || 0), 0)}</span>
            <span className="stat-label">Total Uses</span>
          </div>
        </div>
      </div>

      {/* Coupons Grid */}
      {isLoading ? (
        <div className="loading-state">Loading coupons...</div>
      ) : coupons.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🎟️</div>
          <h3>No coupons yet</h3>
          <p>Create your first discount coupon</p>
          <Button variant="primary" onClick={() => setShowForm(true)}>
            Create Coupon
          </Button>
        </div>
      ) : (
        <div className="coupons-grid">
          {coupons.map((coupon, index) => (
            <motion.div
              key={coupon.id}
              className={`coupon-card ${!coupon.is_active ? 'inactive' : ''}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <div className="coupon-header">
                <span className="coupon-code">{coupon.code}</span>
                <StatusBadge status={coupon.is_active ? 'active' : 'inactive'} />
              </div>

              <div className="coupon-discount">
                {coupon.discount_type === 'percentage' 
                  ? `${coupon.discount_value}% OFF`
                  : `₹${coupon.discount_value} OFF`
                }
              </div>

              <div className="coupon-details">
                <div className="detail">
                  <span className="label">Min Order</span>
                  <span className="value">₹{coupon.min_order_value || 0}</span>
                </div>
                <div className="detail">
                  <span className="label">Uses</span>
                  <span className="value">{coupon.usage_count || 0}/{coupon.max_uses || '∞'}</span>
                </div>
                <div className="detail">
                  <span className="label">Expires</span>
                  <span className="value">
                    {coupon.expires_at 
                      ? new Date(coupon.expires_at).toLocaleDateString('en-IN') 
                      : 'Never'
                    }
                  </span>
                </div>
              </div>

              <div className="coupon-actions">
                <button className="action-btn edit" onClick={() => handleEdit(coupon)}>
                  Edit
                </button>
                <button 
                  className={`action-btn ${coupon.is_active ? 'disable' : 'enable'}`}
                  onClick={() => toggleMutation.mutate({ 
                    id: coupon.id, 
                    isActive: !coupon.is_active 
                  })}
                >
                  {coupon.is_active ? 'Disable' : 'Enable'}
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showForm}
        onClose={handleCloseForm}
        title={editingCoupon ? 'Edit Coupon' : 'Create Coupon'}
        size="medium"
      >
        <CouponForm
          initialValues={editingCoupon}
          onSubmit={(data) => {
            if (editingCoupon) {
              updateMutation.mutate({ id: editingCoupon.id, data })
            } else {
              createMutation.mutate(data)
            }
          }}
          onCancel={handleCloseForm}
          loading={createMutation.isPending || updateMutation.isPending}
        />
      </Modal>
    </div>
  )
}

function CouponForm({ initialValues, onSubmit, onCancel, loading }) {
  const [formData, setFormData] = useState({
    code: initialValues?.code || '',
    discount_type: initialValues?.discount_type || 'percentage',
    discount_value: initialValues?.discount_value || '',
    min_order_value: initialValues?.min_order_value || '',
    max_uses: initialValues?.max_uses || '',
    expires_at: initialValues?.expires_at?.split('T')[0] || ''
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      ...formData,
      code: formData.code.toUpperCase(),
      discount_value: parseFloat(formData.discount_value),
      min_order_value: formData.min_order_value ? parseFloat(formData.min_order_value) : null,
      max_uses: formData.max_uses ? parseInt(formData.max_uses) : null,
      expires_at: formData.expires_at || null
    })
  }

  return (
    <form className="coupon-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="code">Coupon Code</label>
        <input
          id="code"
          name="code"
          type="text"
          value={formData.code}
          onChange={handleChange}
          placeholder="e.g., SUMMER20"
          className="form-input"
          required
          style={{ textTransform: 'uppercase' }}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="discount_type">Discount Type</label>
          <select
            id="discount_type"
            name="discount_type"
            value={formData.discount_type}
            onChange={handleChange}
            className="form-select"
          >
            <option value="percentage">Percentage (%)</option>
            <option value="fixed">Fixed Amount (₹)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="discount_value">Discount Value</label>
          <input
            id="discount_value"
            name="discount_value"
            type="number"
            value={formData.discount_value}
            onChange={handleChange}
            placeholder={formData.discount_type === 'percentage' ? '20' : '500'}
            className="form-input"
            required
            min={1}
            max={formData.discount_type === 'percentage' ? 100 : undefined}
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="min_order_value">Min Order Value (₹)</label>
          <input
            id="min_order_value"
            name="min_order_value"
            type="number"
            value={formData.min_order_value}
            onChange={handleChange}
            placeholder="Optional"
            className="form-input"
            min={0}
          />
        </div>

        <div className="form-group">
          <label htmlFor="max_uses">Max Uses</label>
          <input
            id="max_uses"
            name="max_uses"
            type="number"
            value={formData.max_uses}
            onChange={handleChange}
            placeholder="Unlimited"
            className="form-input"
            min={1}
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="expires_at">Expiry Date</label>
        <input
          id="expires_at"
          name="expires_at"
          type="date"
          value={formData.expires_at}
          onChange={handleChange}
          className="form-input"
          min={new Date().toISOString().split('T')[0]}
        />
      </div>

      <div className="form-actions">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" variant="primary" loading={loading}>
          {initialValues ? 'Update Coupon' : 'Create Coupon'}
        </Button>
      </div>
    </form>
  )
}
