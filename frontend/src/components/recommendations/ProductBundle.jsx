import { useState } from 'react'
import { motion } from 'framer-motion'
import Button from '../common/Button'
import { useCartStore } from '../../store/cartStore'
import useToast from '../../hooks/useToast'
import './ProductBundle.css'

export default function ProductBundle({ mainProduct, bundleProducts = [] }) {
  const { addItem } = useCartStore()
  const { toast } = useToast()
  const [selectedProducts, setSelectedProducts] = useState([mainProduct.id])

  const toggleProduct = (productId) => {
    if (productId === mainProduct.id) return // Can't deselect main product
    
    setSelectedProducts(prev =>
      prev.includes(productId)
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    )
  }

  const allProducts = [mainProduct, ...bundleProducts]
  const selectedItems = allProducts.filter(p => selectedProducts.includes(p.id))
  
  const totalPrice = selectedItems.reduce((sum, p) => sum + p.price, 0)
  const savings = totalPrice * 0.1 // 10% bundle discount
  const finalPrice = totalPrice - savings

  const handleAddBundle = () => {
    selectedItems.forEach(product => {
      addItem(product)
    })
    toast.success(`Added ${selectedItems.length} items to cart!`)
  }

  return (
    <motion.div
      className="product-bundle"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <h3 className="bundle-title">Frequently Bought Together</h3>
      
      <div className="bundle-items">
        {allProducts.map((product, index) => (
          <div key={product.id} className="bundle-item-wrapper">
            {index > 0 && <div className="plus-icon">+</div>}
            <div
              className={`bundle-item ${selectedProducts.includes(product.id) ? 'selected' : ''}`}
              onClick={() => toggleProduct(product.id)}
            >
              <div className="item-image">
                <img src={product.images?.[0]} alt={product.name} />
                {product.id !== mainProduct.id && (
                  <div className="checkbox">
                    {selectedProducts.includes(product.id) ? '✓' : ''}
                  </div>
                )}
              </div>
              <div className="item-info">
                <p className="item-name">{product.name}</p>
                <p className="item-price">₹{product.price.toLocaleString()}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bundle-summary">
        <div className="price-breakdown">
          <div className="price-row">
            <span>Total Price:</span>
            <span className="original-price">₹{totalPrice.toLocaleString()}</span>
          </div>
          <div className="price-row savings">
            <span>Bundle Savings (10%):</span>
            <span>-₹{savings.toLocaleString()}</span>
          </div>
          <div className="price-row total">
            <span>Final Price:</span>
            <span className="gradient-text">₹{finalPrice.toLocaleString()}</span>
          </div>
        </div>

        <Button
          variant="primary"
          size="large"
          onClick={handleAddBundle}
          className="add-bundle-btn"
        >
          Add {selectedItems.length} Items to Cart
        </Button>
      </div>
    </motion.div>
  )
}
