import { useState } from 'react'
import Button from '../common/Button'
import Input from '../common/Input'
import './AddressForm.css'

export default function AddressForm({ 
  initialValues = {}, 
  onSubmit, 
  onCancel,
  submitLabel = 'Save Address',
  loading = false 
}) {
  const [formData, setFormData] = useState({
    fullName: initialValues.fullName || '',
    phone: initialValues.phone || '',
    addressLine1: initialValues.addressLine1 || '',
    addressLine2: initialValues.addressLine2 || '',
    city: initialValues.city || '',
    state: initialValues.state || '',
    pincode: initialValues.pincode || '',
    isDefault: initialValues.isDefault || false
  })

  const [errors, setErrors] = useState({})

  const validate = () => {
    const newErrors = {}
    
    if (!formData.fullName.trim()) newErrors.fullName = 'Full name is required'
    if (!formData.phone.trim()) newErrors.phone = 'Phone number is required'
    else if (!/^[6-9]\d{9}$/.test(formData.phone)) newErrors.phone = 'Invalid phone number'
    if (!formData.addressLine1.trim()) newErrors.addressLine1 = 'Address is required'
    if (!formData.city.trim()) newErrors.city = 'City is required'
    if (!formData.state.trim()) newErrors.state = 'State is required'
    if (!formData.pincode.trim()) newErrors.pincode = 'Pincode is required'
    else if (!/^\d{6}$/.test(formData.pincode)) newErrors.pincode = 'Invalid pincode'

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
    // Clear error when user types
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }))
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validate()) {
      onSubmit(formData)
    }
  }

  const indianStates = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
    'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
    'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
    'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
    'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
    'Delhi', 'Jammu and Kashmir', 'Ladakh'
  ]

  return (
    <form className="address-form" onSubmit={handleSubmit}>
      <div className="form-row">
        <div className="form-group">
          <label htmlFor="fullName">Full Name *</label>
          <input
            id="fullName"
            name="fullName"
            type="text"
            value={formData.fullName}
            onChange={handleChange}
            placeholder="Enter full name"
            className={`form-input ${errors.fullName ? 'error' : ''}`}
          />
          {errors.fullName && <span className="error-text">{errors.fullName}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="phone">Phone Number *</label>
          <input
            id="phone"
            name="phone"
            type="tel"
            value={formData.phone}
            onChange={handleChange}
            placeholder="10-digit mobile number"
            className={`form-input ${errors.phone ? 'error' : ''}`}
          />
          {errors.phone && <span className="error-text">{errors.phone}</span>}
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="addressLine1">Address Line 1 *</label>
        <input
          id="addressLine1"
          name="addressLine1"
          type="text"
          value={formData.addressLine1}
          onChange={handleChange}
          placeholder="House/Flat No., Building Name, Street"
          className={`form-input ${errors.addressLine1 ? 'error' : ''}`}
        />
        {errors.addressLine1 && <span className="error-text">{errors.addressLine1}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="addressLine2">Address Line 2</label>
        <input
          id="addressLine2"
          name="addressLine2"
          type="text"
          value={formData.addressLine2}
          onChange={handleChange}
          placeholder="Landmark, Area (optional)"
          className="form-input"
        />
      </div>

      <div className="form-row form-row-3">
        <div className="form-group">
          <label htmlFor="city">City *</label>
          <input
            id="city"
            name="city"
            type="text"
            value={formData.city}
            onChange={handleChange}
            placeholder="City"
            className={`form-input ${errors.city ? 'error' : ''}`}
          />
          {errors.city && <span className="error-text">{errors.city}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="state">State *</label>
          <select
            id="state"
            name="state"
            value={formData.state}
            onChange={handleChange}
            className={`form-select ${errors.state ? 'error' : ''}`}
          >
            <option value="">Select State</option>
            {indianStates.map(state => (
              <option key={state} value={state}>{state}</option>
            ))}
          </select>
          {errors.state && <span className="error-text">{errors.state}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="pincode">Pincode *</label>
          <input
            id="pincode"
            name="pincode"
            type="text"
            value={formData.pincode}
            onChange={handleChange}
            placeholder="6-digit pincode"
            maxLength={6}
            className={`form-input ${errors.pincode ? 'error' : ''}`}
          />
          {errors.pincode && <span className="error-text">{errors.pincode}</span>}
        </div>
      </div>

      <label className="checkbox-label">
        <input
          type="checkbox"
          name="isDefault"
          checked={formData.isDefault}
          onChange={handleChange}
        />
        <span>Set as default address</span>
      </label>

      <div className="form-actions">
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" variant="primary" loading={loading}>
          {submitLabel}
        </Button>
      </div>
    </form>
  )
}
