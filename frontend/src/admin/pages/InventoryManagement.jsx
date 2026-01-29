import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { productsAPI } from '../../services/api'
import { StatusBadge } from '../../components/common/Badge'
import useToast from '../../hooks/useToast'
import './InventoryManagement.css'

export default function InventoryManagement() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStock, setFilterStock] = useState('all')
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['inventory'],
    queryFn: () => productsAPI.getAll?.()
  })

  const updateStockMutation = useMutation({
    mutationFn: ({ productId, stock }) => productsAPI.updateStock?.(productId, stock),
    onSuccess: () => {
      queryClient.invalidateQueries(['inventory'])
      toast.success('Stock updated successfully')
    },
    onError: () => toast.error('Failed to update stock')
  })

  const products = data?.data || []
  
  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name?.toLowerCase().includes(searchQuery.toLowerCase())
    
    if (filterStock === 'low') {
      return matchesSearch && product.stock <= 10 && product.stock > 0
    } else if (filterStock === 'out') {
      return matchesSearch && product.stock === 0
    } else if (filterStock === 'in') {
      return matchesSearch && product.stock > 10
    }
    return matchesSearch
  })

  const getStockStatus = (stock) => {
    if (stock === 0) return 'out-of-stock'
    if (stock <= 10) return 'low-stock'
    return 'in-stock'
  }

  // Summary stats
  const totalProducts = products.length
  const lowStockCount = products.filter(p => p.stock <= 10 && p.stock > 0).length
  const outOfStockCount = products.filter(p => p.stock === 0).length
  const totalValue = products.reduce((sum, p) => sum + (p.price * p.stock), 0)

  return (
    <div className="inventory-management">
      <div className="page-header">
        <h1>Inventory Management</h1>
        <p>Track and manage product stock levels</p>
      </div>

      {/* Stats */}
      <div className="inventory-stats">
        <div className="stat-card">
          <span className="stat-icon">📦</span>
          <div>
            <span className="stat-value">{totalProducts}</span>
            <span className="stat-label">Total Products</span>
          </div>
        </div>
        <div className="stat-card warning">
          <span className="stat-icon">⚠️</span>
          <div>
            <span className="stat-value">{lowStockCount}</span>
            <span className="stat-label">Low Stock</span>
          </div>
        </div>
        <div className="stat-card danger">
          <span className="stat-icon">❌</span>
          <div>
            <span className="stat-value">{outOfStockCount}</span>
            <span className="stat-label">Out of Stock</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">💰</span>
          <div>
            <span className="stat-value">₹{(totalValue / 100000).toFixed(1)}L</span>
            <span className="stat-label">Total Value</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search products..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-tabs">
          {[
            { key: 'all', label: 'All' },
            { key: 'in', label: 'In Stock' },
            { key: 'low', label: 'Low Stock' },
            { key: 'out', label: 'Out of Stock' }
          ].map(({ key, label }) => (
            <button
              key={key}
              className={filterStock === key ? 'active' : ''}
              onClick={() => setFilterStock(key)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Inventory Table */}
      <div className="table-container">
        <table className="inventory-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>SKU</th>
              <th>Category</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="skeleton-row">
                  <td colSpan={7}><div className="skeleton" /></td>
                </tr>
              ))
            ) : filteredProducts.length === 0 ? (
              <tr>
                <td colSpan={7} className="empty-row">
                  No products found
                </td>
              </tr>
            ) : (
              filteredProducts.map((product, index) => (
                <motion.tr
                  key={product.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.02 }}
                  className={getStockStatus(product.stock)}
                >
                  <td>
                    <div className="product-cell">
                      <img 
                        src={product.images?.[0] || '/placeholder.jpg'} 
                        alt={product.name}
                        className="product-thumb"
                      />
                      <span className="product-name">{product.name}</span>
                    </div>
                  </td>
                  <td className="sku">
                    {product.sku || `SKU-${product.id?.slice(-6).toUpperCase()}`}
                  </td>
                  <td>{product.category}</td>
                  <td className="price">₹{product.price?.toLocaleString()}</td>
                  <td>
                    <StockInput 
                      value={product.stock} 
                      onChange={(newStock) => 
                        updateStockMutation.mutate({ 
                          productId: product.id, 
                          stock: newStock 
                        })
                      }
                    />
                  </td>
                  <td>
                    <StatusBadge status={getStockStatus(product.stock)} />
                  </td>
                  <td>
                    <button className="action-btn restock">
                      Restock
                    </button>
                  </td>
                </motion.tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Stock Input Component
function StockInput({ value, onChange }) {
  const [editing, setEditing] = useState(false)
  const [inputValue, setInputValue] = useState(value)

  const handleSave = () => {
    const newValue = parseInt(inputValue, 10)
    if (!isNaN(newValue) && newValue >= 0) {
      onChange(newValue)
    } else {
      setInputValue(value)
    }
    setEditing(false)
  }

  if (editing) {
    return (
      <div className="stock-input-edit">
        <input
          type="number"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onBlur={handleSave}
          onKeyDown={(e) => e.key === 'Enter' && handleSave()}
          autoFocus
          min={0}
        />
      </div>
    )
  }

  return (
    <button 
      className={`stock-value ${value <= 10 ? 'low' : ''} ${value === 0 ? 'out' : ''}`}
      onClick={() => setEditing(true)}
    >
      {value}
    </button>
  )
}
