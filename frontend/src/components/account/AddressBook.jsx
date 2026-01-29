import { useState } from 'react'
import { motion } from 'framer-motion'
import Modal from '../common/Modal'
import Button from '../common/Button'
import AddressForm from '../checkout/AddressForm'
import useToast from '../../hooks/useToast'
import './AddressBook.css'

export default function AddressBook({ addresses = [], onAdd, onEdit, onDelete, onSetDefault }) {
  const [showForm, setShowForm] = useState(false)
  const [editingAddress, setEditingAddress] = useState(null)
  const { toast } = useToast()

  const handleSubmit = (formData) => {
    if (editingAddress) {
      onEdit?.(editingAddress.id, formData)
      toast.success('Address updated successfully')
    } else {
      onAdd?.(formData)
      toast.success('Address added successfully')
    }
    setShowForm(false)
    setEditingAddress(null)
  }

  const handleEdit = (address) => {
    setEditingAddress(address)
    setShowForm(true)
  }

  const handleDelete = (addressId) => {
    if (window.confirm('Are you sure you want to delete this address?')) {
      onDelete?.(addressId)
      toast.success('Address deleted')
    }
  }

  return (
    <div className="address-book">
      <div className="address-book-header">
        <h3>Saved Addresses</h3>
        <Button variant="primary" onClick={() => setShowForm(true)}>
          + Add New Address
        </Button>
      </div>

      {addresses.length === 0 ? (
        <div className="addresses-empty">
          <div className="empty-icon">📍</div>
          <h4>No addresses saved</h4>
          <p>Add a delivery address to make checkout faster!</p>
        </div>
      ) : (
        <div className="addresses-grid">
          {addresses.map((address, index) => (
            <motion.div
              key={address.id}
              className={`address-card ${address.isDefault ? 'default' : ''}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              {address.isDefault && (
                <span className="default-badge">Default</span>
              )}

              <div className="address-content">
                <strong className="address-name">{address.fullName}</strong>
                <p className="address-text">
                  {address.addressLine1}
                  {address.addressLine2 && <><br />{address.addressLine2}</>}
                  <br />
                  {address.city}, {address.state} {address.pincode}
                </p>
                <p className="address-phone">📞 {address.phone}</p>
              </div>

              <div className="address-actions">
                <button className="action-btn" onClick={() => handleEdit(address)}>
                  Edit
                </button>
                <button 
                  className="action-btn" 
                  onClick={() => handleDelete(address.id)}
                >
                  Delete
                </button>
                {!address.isDefault && (
                  <button 
                    className="action-btn set-default"
                    onClick={() => onSetDefault?.(address.id)}
                  >
                    Set as Default
                  </button>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Add/Edit Address Modal */}
      <Modal
        isOpen={showForm}
        onClose={() => {
          setShowForm(false)
          setEditingAddress(null)
        }}
        title={editingAddress ? 'Edit Address' : 'Add New Address'}
        size="medium"
      >
        <AddressForm
          initialValues={editingAddress || {}}
          onSubmit={handleSubmit}
          onCancel={() => {
            setShowForm(false)
            setEditingAddress(null)
          }}
          submitLabel={editingAddress ? 'Update Address' : 'Add Address'}
        />
      </Modal>
    </div>
  )
}
