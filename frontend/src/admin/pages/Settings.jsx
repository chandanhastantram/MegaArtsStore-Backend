import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import Button from '../../components/common/Button'
import useToast from '../../hooks/useToast'
import { settingsAPI } from '../../services/api'
import './Settings.css'

export default function Settings() {
  const { toast } = useToast()
  const [activeTab, setActiveTab] = useState('general')

  const tabs = [
    { id: 'general', label: 'General', icon: '⚙️' },
    { id: 'payment', label: 'Payment', icon: '💳' },
    { id: 'shipping', label: 'Shipping', icon: '🚚' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' }
  ]

  return (
    <div className="settings-page">
      <div className="page-header">
        <h1>Settings</h1>
        <p>Configure your store settings</p>
      </div>

      <div className="settings-container">
        {/* Sidebar */}
        <div className="settings-sidebar">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`settings-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content */}
        <motion.div 
          className="settings-content"
          key={activeTab}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          {activeTab === 'general' && <GeneralSettings toast={toast} />}
          {activeTab === 'payment' && <PaymentSettings toast={toast} />}
          {activeTab === 'shipping' && <ShippingSettings toast={toast} />}
          {activeTab === 'notifications' && <NotificationSettings toast={toast} />}
        </motion.div>
      </div>
    </div>
  )
}

function GeneralSettings({ toast }) {
  const [settings, setSettings] = useState({
    storeName: 'MegaArtsStore',
    storeEmail: 'contact@megaartsstore.com',
    storePhone: '+91 98765 43210',
    storeCurrency: 'INR',
    storeTimezone: 'Asia/Kolkata',
    maintenanceMode: false
  })

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSave = () => {
    toast.success('Settings saved successfully')
  }

  return (
    <div className="settings-section">
      <h2>General Settings</h2>

      <div className="settings-form">
        <div className="form-group">
          <label htmlFor="storeName">Store Name</label>
          <input
            id="storeName"
            name="storeName"
            type="text"
            value={settings.storeName}
            onChange={handleChange}
            className="form-input"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="storeEmail">Contact Email</label>
            <input
              id="storeEmail"
              name="storeEmail"
              type="email"
              value={settings.storeEmail}
              onChange={handleChange}
              className="form-input"
            />
          </div>
          <div className="form-group">
            <label htmlFor="storePhone">Contact Phone</label>
            <input
              id="storePhone"
              name="storePhone"
              type="tel"
              value={settings.storePhone}
              onChange={handleChange}
              className="form-input"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="storeCurrency">Currency</label>
            <select
              id="storeCurrency"
              name="storeCurrency"
              value={settings.storeCurrency}
              onChange={handleChange}
              className="form-select"
            >
              <option value="INR">INR (₹)</option>
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="storeTimezone">Timezone</label>
            <select
              id="storeTimezone"
              name="storeTimezone"
              value={settings.storeTimezone}
              onChange={handleChange}
              className="form-select"
            >
              <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
              <option value="UTC">UTC</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              name="maintenanceMode"
              checked={settings.maintenanceMode}
              onChange={handleChange}
            />
            <span>Enable Maintenance Mode</span>
          </label>
          <span className="form-hint">When enabled, customers will see a maintenance page</span>
        </div>

        <Button variant="primary" onClick={handleSave}>
          Save Changes
        </Button>
      </div>
    </div>
  )
}

function PaymentSettings({ toast }) {
  const [settings, setSettings] = useState({
    razorpayEnabled: true,
    razorpayKeyId: 'rzp_test_xxxxxxxxxxxxx',
    razorpayKeySecret: '************************',
    codEnabled: true,
    codMinOrder: 500,
    codMaxOrder: 50000
  })

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSave = () => {
    toast.success('Payment settings saved')
  }

  return (
    <div className="settings-section">
      <h2>Payment Settings</h2>

      <div className="settings-form">
        {/* Razorpay */}
        <div className="settings-block">
          <div className="block-header">
            <div>
              <h3>Razorpay</h3>
              <p>Online payment gateway</p>
            </div>
            <label className="toggle">
              <input
                type="checkbox"
                name="razorpayEnabled"
                checked={settings.razorpayEnabled}
                onChange={handleChange}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          {settings.razorpayEnabled && (
            <div className="block-content">
              <div className="form-group">
                <label htmlFor="razorpayKeyId">Key ID</label>
                <input
                  id="razorpayKeyId"
                  name="razorpayKeyId"
                  type="text"
                  value={settings.razorpayKeyId}
                  onChange={handleChange}
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label htmlFor="razorpayKeySecret">Key Secret</label>
                <input
                  id="razorpayKeySecret"
                  name="razorpayKeySecret"
                  type="password"
                  value={settings.razorpayKeySecret}
                  onChange={handleChange}
                  className="form-input"
                />
              </div>
            </div>
          )}
        </div>

        {/* COD */}
        <div className="settings-block">
          <div className="block-header">
            <div>
              <h3>Cash on Delivery</h3>
              <p>Accept payment on delivery</p>
            </div>
            <label className="toggle">
              <input
                type="checkbox"
                name="codEnabled"
                checked={settings.codEnabled}
                onChange={handleChange}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          {settings.codEnabled && (
            <div className="block-content">
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="codMinOrder">Min Order (₹)</label>
                  <input
                    id="codMinOrder"
                    name="codMinOrder"
                    type="number"
                    value={settings.codMinOrder}
                    onChange={handleChange}
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="codMaxOrder">Max Order (₹)</label>
                  <input
                    id="codMaxOrder"
                    name="codMaxOrder"
                    type="number"
                    value={settings.codMaxOrder}
                    onChange={handleChange}
                    className="form-input"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        <Button variant="primary" onClick={handleSave}>
          Save Changes
        </Button>
      </div>
    </div>
  )
}

function ShippingSettings({ toast }) {
  const [settings, setSettings] = useState({
    freeShippingThreshold: 5000,
    flatShippingRate: 99,
    expressShippingRate: 199,
    processingDays: 2,
    deliveryDays: 5
  })

  const handleChange = (e) => {
    setSettings(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleSave = () => {
    toast.success('Shipping settings saved')
  }

  return (
    <div className="settings-section">
      <h2>Shipping Settings</h2>

      <div className="settings-form">
        <div className="form-group">
          <label htmlFor="freeShippingThreshold">Free Shipping Threshold (₹)</label>
          <input
            id="freeShippingThreshold"
            name="freeShippingThreshold"
            type="number"
            value={settings.freeShippingThreshold}
            onChange={handleChange}
            className="form-input"
          />
          <span className="form-hint">Orders above this amount get free shipping</span>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="flatShippingRate">Standard Shipping (₹)</label>
            <input
              id="flatShippingRate"
              name="flatShippingRate"
              type="number"
              value={settings.flatShippingRate}
              onChange={handleChange}
              className="form-input"
            />
          </div>
          <div className="form-group">
            <label htmlFor="expressShippingRate">Express Shipping (₹)</label>
            <input
              id="expressShippingRate"
              name="expressShippingRate"
              type="number"
              value={settings.expressShippingRate}
              onChange={handleChange}
              className="form-input"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="processingDays">Processing Days</label>
            <input
              id="processingDays"
              name="processingDays"
              type="number"
              value={settings.processingDays}
              onChange={handleChange}
              className="form-input"
            />
          </div>
          <div className="form-group">
            <label htmlFor="deliveryDays">Estimated Delivery Days</label>
            <input
              id="deliveryDays"
              name="deliveryDays"
              type="number"
              value={settings.deliveryDays}
              onChange={handleChange}
              className="form-input"
            />
          </div>
        </div>

        <Button variant="primary" onClick={handleSave}>
          Save Changes
        </Button>
      </div>
    </div>
  )
}

function NotificationSettings({ toast }) {
  const [settings, setSettings] = useState({
    emailOrderConfirmation: true,
    emailShippingUpdate: true,
    emailDeliveryConfirmation: true,
    emailNewsletter: false,
    smsOrderConfirmation: true,
    smsDeliveryUpdate: true
  })

  const handleChange = (e) => {
    setSettings(prev => ({
      ...prev,
      [e.target.name]: e.target.checked
    }))
  }

  const handleSave = () => {
    toast.success('Notification settings saved')
  }

  return (
    <div className="settings-section">
      <h2>Notification Settings</h2>

      <div className="settings-form">
        <div className="settings-block">
          <h3>Email Notifications</h3>
          <div className="notification-list">
            {[
              { name: 'emailOrderConfirmation', label: 'Order Confirmation' },
              { name: 'emailShippingUpdate', label: 'Shipping Updates' },
              { name: 'emailDeliveryConfirmation', label: 'Delivery Confirmation' },
              { name: 'emailNewsletter', label: 'Newsletter & Promotions' }
            ].map(notification => (
              <label key={notification.name} className="notification-item">
                <span>{notification.label}</span>
                <label className="toggle">
                  <input
                    type="checkbox"
                    name={notification.name}
                    checked={settings[notification.name]}
                    onChange={handleChange}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </label>
            ))}
          </div>
        </div>

        <div className="settings-block">
          <h3>SMS Notifications</h3>
          <div className="notification-list">
            {[
              { name: 'smsOrderConfirmation', label: 'Order Confirmation' },
              { name: 'smsDeliveryUpdate', label: 'Delivery Updates' }
            ].map(notification => (
              <label key={notification.name} className="notification-item">
                <span>{notification.label}</span>
                <label className="toggle">
                  <input
                    type="checkbox"
                    name={notification.name}
                    checked={settings[notification.name]}
                    onChange={handleChange}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </label>
            ))}
          </div>
        </div>

        <Button variant="primary" onClick={handleSave}>
          Save Changes
        </Button>
      </div>
    </div>
  )
}
