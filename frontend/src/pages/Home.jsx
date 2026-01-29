import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { productsAPI, recommendationsAPI } from '../services/api'
import './Home.css'

export default function Home() {
  const { data: featuredProducts } = useQuery({
    queryKey: ['products', 'featured'],
    queryFn: () => productsAPI.getAll({ featured: true, per_page: 8 }),
  })

  const { data: trending } = useQuery({
    queryKey: ['trending'],
    queryFn: () => recommendationsAPI.trending(),
  })

  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-bg"></div>
        <div className="container">
          <motion.div
            className="hero-content"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <motion.h1 
              className="hero-title font-display"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.8 }}
            >
              Experience Jewellery
              <br />
              <span className="gradient-text">In Augmented Reality</span>
            </motion.h1>
            
            <motion.p 
              className="hero-subtitle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.8 }}
            >
              Try on exquisite bangles, rings, and necklaces virtually before you buy.
              <br />
              Premium craftsmanship meets cutting-edge AR technology.
            </motion.p>

            <motion.div 
              className="hero-actions"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.8 }}
            >
              <Link to="/products" className="btn btn-primary btn-lg">
                Explore Collection
              </Link>
              <Link to="/ar-try-on/demo" className="btn btn-secondary btn-lg">
                Try AR Now
              </Link>
            </motion.div>

            <motion.div 
              className="hero-stats"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8, duration: 0.8 }}
            >
              <div className="stat">
                <span className="stat-number gradient-text">500+</span>
                <span className="stat-label">Unique Designs</span>
              </div>
              <div className="stat">
                <span className="stat-number gradient-text">10K+</span>
                <span className="stat-label">Happy Customers</span>
              </div>
              <div className="stat">
                <span className="stat-number gradient-text">AR</span>
                <span className="stat-label">Try-On Enabled</span>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Categories */}
      <section className="categories">
        <div className="container">
          <h2 className="section-title font-display">Shop by Category</h2>
          <div className="categories-grid">
            {['Bangles', 'Rings', 'Necklaces', 'Earrings'].map((category, i) => (
              <motion.div
                key={category}
                className="category-card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                whileHover={{ y: -10 }}
              >
                <Link to={`/products/${category.toLowerCase()}`}>
                  <div className="category-image">
                    <div className="category-overlay"></div>
                  </div>
                  <h3 className="category-name">{category}</h3>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="featured">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title font-display">Featured Collection</h2>
            <Link to="/products" className="view-all">
              View All →
            </Link>
          </div>
          
          <div className="products-grid">
            {featuredProducts?.data?.products?.slice(0, 8).map((product, i) => (
              <motion.div
                key={product.id}
                className="product-card card"
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                whileHover={{ y: -8 }}
              >
                <Link to={`/product/${product.id}`}>
                  <div className="product-image">
                    {product.ar_enabled && (
                      <span className="badge badge-gold ar-badge">AR</span>
                    )}
                    <img 
                      src={product.images?.[0] || '/placeholder.jpg'} 
                      alt={product.name}
                    />
                  </div>
                  <div className="product-info">
                    <h3 className="product-name">{product.name}</h3>
                    <p className="product-price gradient-text">₹{product.price.toLocaleString()}</p>
                    {product.avg_rating > 0 && (
                      <div className="product-rating">
                        {'⭐'.repeat(Math.round(product.avg_rating))}
                        <span>({product.avg_rating})</span>
                      </div>
                    )}
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* AR CTA */}
      <section className="ar-cta">
        <div className="container">
          <motion.div 
            className="ar-cta-content glass"
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
          >
            <div className="ar-cta-text">
              <h2 className="font-display">Try Before You Buy</h2>
              <p>Experience our jewellery in augmented reality. See how it looks on you instantly.</p>
              <Link to="/products" className="btn btn-dark btn-lg">
                Start AR Try-On
              </Link>
            </div>
            <div className="ar-cta-visual">
              <div className="ar-icon animate-float">📱</div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="testimonials">
        <div className="container">
          <h2 className="section-title font-display">What Our Customers Say</h2>
          <div className="testimonials-grid">
            {[
              { name: 'Priya Sharma', text: 'The AR try-on feature is amazing! I could see exactly how the bangle would look.', rating: 5 },
              { name: 'Anjali Patel', text: 'Beautiful craftsmanship and the delivery was super fast. Highly recommend!', rating: 5 },
              { name: 'Meera Reddy', text: 'Love the quality and the AR feature made shopping so easy!', rating: 5 },
            ].map((testimonial, i) => (
              <motion.div
                key={i}
                className="testimonial-card card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <div className="testimonial-rating">
                  {'⭐'.repeat(testimonial.rating)}
                </div>
                <p className="testimonial-text">"{testimonial.text}"</p>
                <p className="testimonial-author">— {testimonial.name}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
