import { useState } from 'react'
import Button from '../common/Button'
import { ordersAPI, paymentAPI } from '../../services/api'
import useToast from '../../hooks/useToast'
import './PaymentSection.css'

export default function PaymentSection({ 
  orderData, 
  cartItems, 
  total, 
  onSuccess, 
  onError 
}) {
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const loadRazorpayScript = () => {
    return new Promise((resolve) => {
      if (window.Razorpay) {
        resolve(true)
        return
      }
      
      const script = document.createElement('script')
      script.src = 'https://checkout.razorpay.com/v1/checkout.js'
      script.onload = () => resolve(true)
      script.onerror = () => resolve(false)
      document.body.appendChild(script)
    })
  }

  const handlePayment = async () => {
    setLoading(true)
    
    try {
      // Load Razorpay script
      const scriptLoaded = await loadRazorpayScript()
      if (!scriptLoaded) {
        throw new Error('Failed to load payment gateway')
      }

      // Create order on backend
      const orderResponse = await ordersAPI.create({
        ...orderData,
        items: cartItems.map(item => ({
          product_id: item.id,
          quantity: item.quantity,
          size: item.size,
          price: item.price
        }))
      })

      const orderId = orderResponse.data.order_id

      // Create Razorpay payment order
      const paymentResponse = await paymentAPI.create(orderId)
      const razorpayOrder = paymentResponse.data

      // Razorpay options
      const options = {
        key: import.meta.env.VITE_RAZORPAY_KEY,
        amount: razorpayOrder.amount,
        currency: razorpayOrder.currency || 'INR',
        name: 'MegaArtsStore',
        description: `Order #${orderId}`,
        order_id: razorpayOrder.razorpay_order_id,
        prefill: {
          name: orderData.fullName,
          email: orderData.email,
          contact: orderData.phone
        },
        theme: {
          color: '#B8860B'
        },
        handler: async (response) => {
          try {
            // Verify payment on backend
            await paymentAPI.verify({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              order_id: orderId
            })

            toast.success('Payment successful!')
            onSuccess?.(orderId)
          } catch (error) {
            toast.error('Payment verification failed')
            onError?.(error)
          }
        },
        modal: {
          ondismiss: () => {
            setLoading(false)
            toast.info('Payment cancelled')
          }
        }
      }

      const razorpay = new window.Razorpay(options)
      razorpay.open()
      
    } catch (error) {
      console.error('Payment error:', error)
      toast.error(error.response?.data?.detail || 'Payment failed. Please try again.')
      onError?.(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="payment-section">
      <div className="payment-summary">
        <h3>Payment Summary</h3>
        <div className="payment-total">
          <span>Total Amount</span>
          <span className="total-amount gradient-text">₹{total.toLocaleString()}</span>
        </div>
      </div>

      <div className="payment-methods">
        <div className="payment-method active">
          <div className="payment-method-icon">💳</div>
          <div>
            <strong>Online Payment</strong>
            <span>Credit/Debit Card, UPI, Netbanking</span>
          </div>
        </div>
      </div>

      <div className="payment-secure">
        <span className="secure-icon">🔒</span>
        <span>Secure payment powered by Razorpay</span>
      </div>

      <Button 
        variant="primary" 
        size="large" 
        onClick={handlePayment}
        loading={loading}
        className="pay-now-btn"
      >
        Pay ₹{total.toLocaleString()}
      </Button>
    </div>
  )
}
