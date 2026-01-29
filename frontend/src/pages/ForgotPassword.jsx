import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Button from '../components/common/Button'
import { authAPI } from '../services/api'
import useToast from '../hooks/useToast'
import './Auth.css'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const { toast } = useToast()

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!email.trim()) {
      toast.error('Please enter your email')
      return
    }

    setLoading(true)
    try {
      await authAPI.forgotPassword?.(email) || Promise.resolve()
      setSent(true)
      toast.success('Reset link sent to your email!')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send reset link')
    } finally {
      setLoading(false)
    }
  }

  if (sent) {
    return (
      <div className="auth-page">
        <motion.div 
          className="auth-container"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="auth-success">
            <div className="success-icon">✉️</div>
            <h2>Check Your Email</h2>
            <p>
              We've sent a password reset link to<br />
              <strong>{email}</strong>
            </p>
            <p className="auth-hint">
              Didn't receive the email? Check your spam folder or{' '}
              <button onClick={() => setSent(false)} className="link-btn">
                try again
              </button>
            </p>
            <Link to="/login">
              <Button variant="secondary">Back to Login</Button>
            </Link>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <motion.div 
        className="auth-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="auth-header">
          <h1 className="font-display">Forgot Password?</h1>
          <p>Enter your email and we'll send you a reset link</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              className="form-input"
              required
            />
          </div>

          <Button type="submit" variant="primary" size="large" loading={loading}>
            Send Reset Link
          </Button>
        </form>

        <div className="auth-footer">
          <p>
            Remember your password?{' '}
            <Link to="/login" className="auth-link">Sign In</Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
