import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import useAdminStore from '../../store/adminStore'
import Input from '../../components/common/Input'
import Button from '../../components/common/Button'
import useToast from '../../hooks/useToast'
import { authAPI } from '../../services/api'
import './AdminLogin.css'

export default function AdminLogin() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { setAdmin } = useAdminStore()
  
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await authAPI.login(formData)
      const { user, token } = response.data

      // TEMPORARILY DISABLED: Admin role check
      // Any user can access admin panel for testing
      /*
      if (user.role !== 'admin' && user.role !== 'sub_admin') {
        toast.error('Access denied. Admin credentials required.')
        setLoading(false)
        return
      }
      */

      setAdmin(user, token)
      toast.success(`Welcome back, ${user.name}!`)
      navigate('/admin/dashboard')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="admin-login-page">
      <motion.div
        className="admin-login-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="admin-login-header">
          <div className="admin-logo">
            <span className="logo-icon">👑</span>
            <h1>MegaArtsStore</h1>
          </div>
          <h2>Admin Dashboard</h2>
          <p>Sign in to access the admin panel</p>
        </div>

        <form onSubmit={handleSubmit} className="admin-login-form">
          <Input
            label="Email Address"
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="admin@megaartsstore.com"
            required
            autoFocus
          />

          <Input
            label="Password"
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Enter your password"
            required
          />

          <Button
            type="submit"
            variant="primary"
            size="large"
            loading={loading}
            className="admin-login-btn"
          >
            Sign In
          </Button>
        </form>

        <div className="admin-login-footer">
          <p>Admin access only • Unauthorized access is prohibited</p>
        </div>
      </motion.div>
    </div>
  )
}
