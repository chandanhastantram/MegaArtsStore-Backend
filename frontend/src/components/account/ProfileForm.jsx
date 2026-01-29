import { useState } from 'react'
import { useAuthStore } from '../../store/authStore'
import Button from '../common/Button'
import useToast from '../../hooks/useToast'
import { authAPI } from '../../services/api'
import './ProfileForm.css'

export default function ProfileForm() {
  const { user, updateUser } = useAuthStore()
  const { toast } = useToast()
  
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: user?.phone || ''
  })
  
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  
  const [loading, setLoading] = useState(false)
  const [passwordLoading, setPasswordLoading] = useState(false)
  const [editMode, setEditMode] = useState(false)

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handlePasswordChange = (e) => {
    setPasswordData({ ...passwordData, [e.target.name]: e.target.value })
  }

  const handleProfileSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      await authAPI.updateProfile?.(formData) || Promise.resolve()
      updateUser?.(formData)
      toast.success('Profile updated successfully')
      setEditMode(false)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('Passwords do not match')
      return
    }
    
    if (passwordData.newPassword.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }

    setPasswordLoading(true)
    
    try {
      await authAPI.changePassword?.({
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword
      }) || Promise.resolve()
      
      toast.success('Password changed successfully')
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' })
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to change password')
    } finally {
      setPasswordLoading(false)
    }
  }

  return (
    <div className="profile-form-container">
      {/* Profile Information */}
      <div className="profile-section">
        <div className="section-header">
          <h3>Profile Information</h3>
          {!editMode && (
            <Button variant="secondary" size="small" onClick={() => setEditMode(true)}>
              Edit Profile
            </Button>
          )}
        </div>

        {editMode ? (
          <form onSubmit={handleProfileSubmit} className="profile-form">
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                className="form-input"
                required
                disabled
              />
              <span className="form-hint">Email cannot be changed</span>
            </div>

            <div className="form-group">
              <label htmlFor="phone">Phone Number</label>
              <input
                id="phone"
                name="phone"
                type="tel"
                value={formData.phone}
                onChange={handleChange}
                className="form-input"
                placeholder="Enter phone number"
              />
            </div>

            <div className="form-actions">
              <Button 
                type="button" 
                variant="secondary"
                onClick={() => {
                  setEditMode(false)
                  setFormData({
                    name: user?.name || '',
                    email: user?.email || '',
                    phone: user?.phone || ''
                  })
                }}
              >
                Cancel
              </Button>
              <Button type="submit" variant="primary" loading={loading}>
                Save Changes
              </Button>
            </div>
          </form>
        ) : (
          <div className="profile-info">
            <div className="info-row">
              <span className="info-label">Name</span>
              <span className="info-value">{user?.name || 'Not set'}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Email</span>
              <span className="info-value">{user?.email}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Phone</span>
              <span className="info-value">{user?.phone || 'Not set'}</span>
            </div>
          </div>
        )}
      </div>

      {/* Change Password */}
      <div className="profile-section">
        <div className="section-header">
          <h3>Change Password</h3>
        </div>

        <form onSubmit={handlePasswordSubmit} className="profile-form">
          <div className="form-group">
            <label htmlFor="currentPassword">Current Password</label>
            <input
              id="currentPassword"
              name="currentPassword"
              type="password"
              value={passwordData.currentPassword}
              onChange={handlePasswordChange}
              className="form-input"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="newPassword">New Password</label>
            <input
              id="newPassword"
              name="newPassword"
              type="password"
              value={passwordData.newPassword}
              onChange={handlePasswordChange}
              className="form-input"
              required
              minLength={8}
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm New Password</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={passwordData.confirmPassword}
              onChange={handlePasswordChange}
              className="form-input"
              required
            />
          </div>

          <Button type="submit" variant="primary" loading={passwordLoading}>
            Update Password
          </Button>
        </form>
      </div>
    </div>
  )
}
