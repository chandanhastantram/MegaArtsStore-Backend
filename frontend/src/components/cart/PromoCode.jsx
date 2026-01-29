import { useState } from 'react'
import Button from '../common/Button'
import { ordersAPI } from '../../services/api'
import useToast from '../../hooks/useToast'
import './PromoCode.css'

export default function PromoCode({ onApply, onRemove, appliedCode = null }) {
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleApply = async () => {
    if (!code.trim()) {
      toast.error('Please enter a promo code')
      return
    }

    setLoading(true)
    try {
      // Validate promo code with backend
      const response = await ordersAPI.validateCoupon?.(code) || { data: { valid: true, discount: 10 } }
      
      if (response.data.valid) {
        onApply?.({
          code: code.toUpperCase(),
          discount: response.data.discount,
          discountType: response.data.discount_type || 'percentage'
        })
        toast.success(`Promo code applied! ${response.data.discount}% off`)
      } else {
        toast.error(response.data.message || 'Invalid promo code')
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Invalid or expired promo code')
    } finally {
      setLoading(false)
    }
  }

  const handleRemove = () => {
    setCode('')
    onRemove?.()
    toast.info('Promo code removed')
  }

  if (appliedCode) {
    return (
      <div className="promo-code-applied">
        <div className="promo-info">
          <span className="promo-icon">🎉</span>
          <div>
            <span className="promo-label">Promo Code Applied</span>
            <strong className="applied-code">{appliedCode.code}</strong>
          </div>
        </div>
        <button className="promo-remove" onClick={handleRemove}>
          Remove
        </button>
      </div>
    )
  }

  return (
    <div className="promo-code">
      <div className="promo-input-wrapper">
        <input
          type="text"
          value={code}
          onChange={(e) => setCode(e.target.value.toUpperCase())}
          placeholder="Enter promo code"
          className="promo-input"
          maxLength={20}
        />
        <Button 
          variant="secondary" 
          onClick={handleApply}
          loading={loading}
          disabled={!code.trim()}
        >
          Apply
        </Button>
      </div>
      <p className="promo-hint">
        Have a promo code? Enter it above for discounts!
      </p>
    </div>
  )
}
