import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { productsAPI, reviewsAPI, recommendationsAPI } from '../services/api'
import { useCartStore } from '../store/cartStore'
import { useWishlistStore } from '../store/wishlistStore'
import Button from '../components/common/Button'
import ProductCard from '../components/products/ProductCard'
import useToast from '../hooks/useToast'
import './ProductDetail.css'

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { toast } = useToast()
  const { addItem } = useCartStore()
  const { items: wishlistItems, addItem: addToWishlist, removeItem: removeFromWishlist } = useWishlistStore()
  
  const [selectedImage, setSelectedImage] = useState(0)
  const [quantity, setQuantity] = useState(1)
  const [selectedSize, setSelectedSize] = useState('')

  const { data: productData, isLoading } = useQuery({
    queryKey: ['product', id],
    queryFn: () => productsAPI.getById(id)
  })

  const { data: reviewsData } = useQuery({
    queryKey: ['reviews', id],
    queryFn: () => reviewsAPI.getByProduct(id)
  })

  const { data: similarData } = useQuery({
    queryKey: ['similar', id],
    queryFn: () => recommendationsAPI.similar(id),
    enabled: !!productData
  })

  const product = productData?.data
  const reviews = reviewsData?.data || []
  const similarProducts = similarData?.data?.products || []
  const isInWishlist = wishlistItems.some(item => item.id === product?.id)

  const handleAddToCart = () => {
    if (!selectedSize && product?.sizes?.length > 0) {
      toast.error('Please select a size')
      return
    }
    
    addItem({ ...product, quantity, size: selectedSize })
    toast.success(`${product.name} added to cart!`)
  }

  const handleToggleWishlist = () => {
    if (isInWishlist) {
      removeFromWishlist(product.id)
      toast.info('Removed from wishlist')
    } else {
      addToWishlist(product)
      toast.success('Added to wishlist!')
    }
  }

  if (isLoading) {
    return (
      <div className="product-detail-loading">
        <div className="spinner-large"></div>
        <p>Loading product...</p>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="product-not-found">
        <h2>Product not found</h2>
        <Button variant="primary" onClick={() => navigate('/products')}>
          Browse Products
        </Button>
      </div>
    )
  }

  const images = product.images || ['/placeholder.jpg']
  const sizes = product.sizes || []

  return (
    <div className="product-detail-page">
      <div className="container">
        {/* Breadcrumb */}
        <nav className="breadcrumb">
          <Link to="/">Home</Link>
          <span>/</span>
          <Link to="/products">Products</Link>
          <span>/</span>
          <Link to={`/products/${product.category}`}>{product.category}</Link>
          <span>/</span>
          <span>{product.name}</span>
        </nav>

        <div className="product-detail-grid">
          {/* Image Gallery */}
          <div className="product-gallery">
            <motion.div 
              className="main-image"
              key={selectedImage}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {product.ar_enabled && (
                <span className="badge badge-gold ar-badge">AR Available</span>
              )}
              <img 
                src={images[selectedImage]} 
                alt={product.name}
                className="gallery-main-img"
              />
            </motion.div>
            
            <div className="thumbnail-grid">
              {images.map((img, index) => (
                <motion.button
                  key={index}
                  className={`thumbnail ${selectedImage === index ? 'active' : ''}`}
                  onClick={() => setSelectedImage(index)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <img src={img} alt={`${product.name} ${index + 1}`} />
                </motion.button>
              ))}
            </div>

            {/* 3D Model Viewer */}
            {product.model_3d_url && (
              <div className="model-viewer-container">
                <model-viewer
                  src={product.model_3d_url}
                  alt={product.name}
                  auto-rotate
                  camera-controls
                  shadow-intensity="1"
                  className="model-viewer"
                ></model-viewer>
              </div>
            )}
          </div>

          {/* Product Info */}
          <div className="product-info">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <h1 className="product-title font-display">{product.name}</h1>
              <p className="product-category">{product.category}</p>

              {/* Rating */}
              {product.avg_rating > 0 && (
                <div className="product-rating-display">
                  <div className="stars">
                    {'⭐'.repeat(Math.round(product.avg_rating))}
                  </div>
                  <span className="rating-text">
                    {product.avg_rating.toFixed(1)} ({reviews.length} reviews)
                  </span>
                </div>
              )}

              {/* Price */}
              <div className="product-price-section">
                {product.discount > 0 ? (
                  <>
                    <span className="price-original">₹{product.price.toLocaleString()}</span>
                    <span className="price-current gradient-text">
                      ₹{(product.price * (1 - product.discount / 100)).toLocaleString()}
                    </span>
                    <span className="badge badge-sale">-{product.discount}% OFF</span>
                  </>
                ) : (
                  <span className="price-current gradient-text">₹{product.price.toLocaleString()}</span>
                )}
              </div>

              {/* Description */}
              <p className="product-description">{product.description}</p>

              {/* Size Selector */}
              {sizes.length > 0 && (
                <div className="size-selector">
                  <h4>Select Size</h4>
                  <div className="size-options">
                    {sizes.map((size) => (
                      <button
                        key={size}
                        className={`size-btn ${selectedSize === size ? 'active' : ''}`}
                        onClick={() => setSelectedSize(size)}
                      >
                        {size}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Quantity Selector */}
              <div className="quantity-selector">
                <h4>Quantity</h4>
                <div className="quantity-controls">
                  <button 
                    className="qty-btn"
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  >
                    −
                  </button>
                  <span className="qty-value">{quantity}</span>
                  <button 
                    className="qty-btn"
                    onClick={() => setQuantity(quantity + 1)}
                  >
                    +
                  </button>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="product-actions">
                <Button 
                  variant="primary" 
                  size="large"
                  onClick={handleAddToCart}
                  className="add-to-cart-btn"
                >
                  Add to Cart
                </Button>
                <Button 
                  variant="secondary" 
                  size="large"
                  onClick={handleToggleWishlist}
                >
                  {isInWishlist ? '❤️ Saved' : '🤍 Save'}
                </Button>
              </div>

              {/* AR Try-On Button */}
              {product.ar_enabled && (
                <Link to={`/ar-try-on/${product.id}`}>
                  <Button variant="dark" size="large" className="ar-try-btn">
                    📱 Try in AR
                  </Button>
                </Link>
              )}

              {/* Product Details */}
              <div className="product-specs">
                <h4>Product Details</h4>
                <div className="specs-grid">
                  {product.material && (
                    <div className="spec-item">
                      <span className="spec-label">Material:</span>
                      <span className="spec-value">{product.material}</span>
                    </div>
                  )}
                  {product.weight && (
                    <div className="spec-item">
                      <span className="spec-label">Weight:</span>
                      <span className="spec-value">{product.weight}g</span>
                    </div>
                  )}
                  <div className="spec-item">
                    <span className="spec-label">SKU:</span>
                    <span className="spec-value">{product.id}</span>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Reviews Section */}
        {reviews.length > 0 && (
          <section className="reviews-section">
            <h2 className="font-display">Customer Reviews</h2>
            <div className="reviews-grid">
              {reviews.slice(0, 6).map((review, index) => (
                <motion.div
                  key={review.id}
                  className="review-card"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="review-header">
                    <div>
                      <p className="review-author">{review.user_name || 'Anonymous'}</p>
                      <div className="review-stars">
                        {'⭐'.repeat(review.rating)}
                      </div>
                    </div>
                    <span className="review-date">
                      {new Date(review.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="review-comment">{review.comment}</p>
                </motion.div>
              ))}
            </div>
          </section>
        )}

        {/* Similar Products */}
        {similarProducts.length > 0 && (
          <section className="similar-products">
            <h2 className="font-display">You May Also Like</h2>
            <div className="similar-grid">
              {similarProducts.slice(0, 4).map((product, index) => (
                <ProductCard key={product.id} product={product} index={index} />
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  )
}
