import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import useCartStore from '../store/cartStore'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import useToast from '../hooks/useToast'
import './Checkout.css'

export default function Checkout() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { items, getTotal, clearCart } = useCartStore()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)

  const [shippingData, setShippingData] = useState({
    fullName: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    pincode: ''
  })

  const handleInputChange = (e) => {
    setShippingData({
      ...shippingData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Simulate order creation
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      clearCart()
      toast.success('Order placed successfully!')
      navigate('/account?tab=orders')
    } catch (error) {
      toast.error('Failed to place order')
    } finally {
      setLoading(false)
    }
  }

  const subtotal = getTotal()
  const tax = subtotal * 0.18
  const shipping = subtotal > 5000 ? 0 : 100
  const total = subtotal + tax + shipping

  if (items.length === 0) {
    return (
      <div className="checkout-empty">
        <h2>Your cart is empty</h2>
        <Button onClick={() => navigate('/products')}>Continue Shopping</Button>
      </div>
    )
  }

  return (
    <div className="checkout-page">
      <div className="checkout-container">
        <div className="checkout-steps">
          <div className={`step ${step >= 1 ? 'active' : ''}`}>
            <span>1</span> Shipping
          </div>
          <div className={`step ${step >= 2 ? 'active' : ''}`}>
            <span>2</span> Payment
          </div>
          <div className={`step ${step >= 3 ? 'active' : ''}`}>
            <span>3</span> Review
          </div>
        </div>

        <form onSubmit={handleSubmit} className="checkout-form">
          <h2>Shipping Information</h2>
          
          <Input
            label="Full Name"
            name="fullName"
            value={shippingData.fullName}
            onChange={handleInputChange}
            required
          />

          <div className="form-row">
            <Input
              label="Email"
              type="email"
              name="email"
              value={shippingData.email}
              onChange={handleInputChange}
              required
            />
            <Input
              label="Phone"
              type="tel"
              name="phone"
              value={shippingData.phone}
              onChange={handleInputChange}
              required
            />
          </div>

          <Input
            label="Address"
            name="address"
            value={shippingData.address}
            onChange={handleInputChange}
            required
          />

          <div className="form-row">
            <Input
              label="City"
              name="city"
              value={shippingData.city}
              onChange={handleInputChange}
              required
            />
            <Input
              label="State"
              name="state"
              value={shippingData.state}
              onChange={handleInputChange}
              required
            />
            <Input
              label="Pincode"
              name="pincode"
              value={shippingData.pincode}
              onChange={handleInputChange}
              required
            />
          </div>

          <Button type="submit" variant="primary" loading={loading} size="large">
            Place Order
          </Button>
        </form>

        <div className="order-summary">
          <h3>Order Summary</h3>
          <div className="summary-items">
            {items.map(item => (
              <div key={`${item.id}-${item.size}`} className="summary-item">
                <span>{item.name} x {item.quantity}</span>
                <span>₹{(item.price * item.quantity).toLocaleString()}</span>
              </div>
            ))}
          </div>
          <div className="summary-totals">
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
            <div className="summary-row total">
              <span>Total</span>
              <span>₹{total.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
