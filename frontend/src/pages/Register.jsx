import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore } from '../store/authStore'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import useToast from '../hooks/useToast'
import './Auth.css'

export default function Register() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { register } = useAuthStore()
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [loading, setLoading] = useState(false)
  const [acceptTerms, setAcceptTerms] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const getPasswordStrength = (password) => {
    if (password.length === 0) return { strength: 0, label: '' }
    if (password.length < 6) return { strength: 1, label: 'Weak' }
    if (password.length < 10) return { strength: 2, label: 'Medium' }
    return { strength: 3, label: 'Strong' }
  }

  const passwordStrength = getPasswordStrength(formData.password)

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match')
      return
    }

    if (!acceptTerms) {
      toast.error('Please accept the terms and conditions')
      return
    }

    setLoading(true)

    try {
      await register(formData.name, formData.email, formData.password)
      toast.success('Account created successfully!')
      navigate('/')
    } catch (error) {
      toast.error(error.response?.data?.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="container">
        <motion.div
          className="auth-container"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="auth-card">
            <div className="auth-header">
              <h1 className="font-display">Create Account</h1>
              <p>Join us to explore luxury jewellery</p>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              <Input
                label="Full Name"
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                icon="👤"
                required
              />

              <Input
                label="Email Address"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                icon="📧"
                required
              />

              <div>
                <Input
                  label="Password"
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  icon="🔒"
                  required
                />
                {formData.password && (
                  <div className="password-strength">
                    <div className="strength-bar">
                      <div 
                        className={`strength-fill strength-${passwordStrength.strength}`}
                        style={{ width: `${(passwordStrength.strength / 3) * 100}%` }}
                      ></div>
                    </div>
                    <span className="strength-label">{passwordStrength.label}</span>
                  </div>
                )}
              </div>

              <Input
                label="Confirm Password"
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                icon="🔒"
                error={
                  formData.confirmPassword && formData.password !== formData.confirmPassword
                    ? 'Passwords do not match'
                    : ''
                }
                required
              />

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={acceptTerms}
                  onChange={(e) => setAcceptTerms(e.target.checked)}
                />
                <span>
                  I agree to the{' '}
                  <Link to="/terms" className="auth-link">
                    Terms & Conditions
                  </Link>
                </span>
              </label>

              <Button
                type="submit"
                variant="primary"
                size="large"
                loading={loading}
                className="auth-submit"
              >
                Create Account
              </Button>
            </form>

            <div className="auth-divider">
              <span>or continue with</span>
            </div>

            <div className="social-login">
              <button className="social-btn google">
                <span>🔍</span>
                Google
              </button>
              <button className="social-btn facebook">
                <span>📘</span>
                Facebook
              </button>
            </div>

            <p className="auth-footer">
              Already have an account?{' '}
              <Link to="/login" className="auth-link">
                Sign in
              </Link>
            </p>
          </div>

          <div className="auth-visual">
            <div className="visual-content">
              <h2 className="font-display gradient-text">
                Join Our Community
              </h2>
              <p>Get exclusive access to new collections</p>
              <div className="visual-features">
                <div className="feature">
                  <span className="feature-icon">🎁</span>
                  <span>Welcome Offer</span>
                </div>
                <div className="feature">
                  <span className="feature-icon">⭐</span>
                  <span>Exclusive Deals</span>
                </div>
                <div className="feature">
                  <span className="feature-icon">💎</span>
                  <span>VIP Access</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
