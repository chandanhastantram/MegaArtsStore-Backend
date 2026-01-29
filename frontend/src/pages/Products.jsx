import { useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { productsAPI } from '../services/api'
import ProductCard from '../components/products/ProductCard'
import Button from '../components/common/Button'
import './Products.css'

export default function Products() {
  const { category } = useParams()
  const [searchParams, setSearchParams] = useSearchParams()
  
  const [filters, setFilters] = useState({
    category: category || searchParams.get('category') || '',
    minPrice: searchParams.get('minPrice') || '',
    maxPrice: searchParams.get('maxPrice') || '',
    material: searchParams.get('material') || '',
    arEnabled: searchParams.get('arEnabled') === 'true',
    sort: searchParams.get('sort') || 'newest'
  })
  
  const [viewMode, setViewMode] = useState('grid')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['products', filters, page],
    queryFn: () => productsAPI.getAll({
      category: filters.category,
      min_price: filters.minPrice,
      max_price: filters.maxPrice,
      material: filters.material,
      ar_enabled: filters.arEnabled || undefined,
      sort: filters.sort,
      page,
      per_page: 12
    })
  })

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    setPage(1)
    
    // Update URL params
    const params = new URLSearchParams()
    Object.entries(newFilters).forEach(([k, v]) => {
      if (v) params.set(k, v)
    })
    setSearchParams(params)
  }

  const clearFilters = () => {
    setFilters({
      category: '',
      minPrice: '',
      maxPrice: '',
      material: '',
      arEnabled: false,
      sort: 'newest'
    })
    setSearchParams({})
    setPage(1)
  }

  const products = data?.data?.products || []
  const totalPages = data?.data?.total_pages || 1

  return (
    <div className="products-page">
      <div className="container">
        {/* Header */}
        <motion.div 
          className="products-header"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div>
            <h1 className="font-display">
              {category ? category.charAt(0).toUpperCase() + category.slice(1) : 'All Products'}
            </h1>
            <p className="products-count">
              {data?.data?.total || 0} products found
            </p>
          </div>
          
          <div className="view-toggle">
            <button 
              className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => setViewMode('grid')}
            >
              ⊞
            </button>
            <button 
              className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
            >
              ☰
            </button>
          </div>
        </motion.div>

        <div className="products-layout">
          {/* Filters Sidebar */}
          <motion.aside 
            className="filters-sidebar"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <div className="filters-header">
              <h3>Filters</h3>
              <button className="clear-filters" onClick={clearFilters}>
                Clear All
              </button>
            </div>

            {/* Category Filter */}
            <div className="filter-group">
              <h4>Category</h4>
              <div className="filter-options">
                {['bangles', 'rings', 'necklaces', 'earrings'].map((cat) => (
                  <label key={cat} className="filter-option">
                    <input
                      type="radio"
                      name="category"
                      checked={filters.category === cat}
                      onChange={() => handleFilterChange('category', cat)}
                    />
                    <span>{cat.charAt(0).toUpperCase() + cat.slice(1)}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Price Range */}
            <div className="filter-group">
              <h4>Price Range</h4>
              <div className="price-inputs">
                <input
                  type="number"
                  placeholder="Min"
                  value={filters.minPrice}
                  onChange={(e) => handleFilterChange('minPrice', e.target.value)}
                  className="price-input"
                />
                <span>-</span>
                <input
                  type="number"
                  placeholder="Max"
                  value={filters.maxPrice}
                  onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
                  className="price-input"
                />
              </div>
            </div>

            {/* Material Filter */}
            <div className="filter-group">
              <h4>Material</h4>
              <div className="filter-options">
                {['gold', 'silver', 'platinum', 'diamond'].map((mat) => (
                  <label key={mat} className="filter-option">
                    <input
                      type="radio"
                      name="material"
                      checked={filters.material === mat}
                      onChange={() => handleFilterChange('material', mat)}
                    />
                    <span>{mat.charAt(0).toUpperCase() + mat.slice(1)}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* AR Enabled */}
            <div className="filter-group">
              <label className="filter-option">
                <input
                  type="checkbox"
                  checked={filters.arEnabled}
                  onChange={(e) => handleFilterChange('arEnabled', e.target.checked)}
                />
                <span>AR Try-On Available</span>
              </label>
            </div>
          </motion.aside>

          {/* Products Grid */}
          <div className="products-content">
            {/* Sort Bar */}
            <div className="sort-bar">
              <select 
                value={filters.sort}
                onChange={(e) => handleFilterChange('sort', e.target.value)}
                className="sort-select"
              >
                <option value="newest">Newest First</option>
                <option value="price_low">Price: Low to High</option>
                <option value="price_high">Price: High to Low</option>
                <option value="rating">Highest Rated</option>
                <option value="popular">Most Popular</option>
              </select>
            </div>

            {/* Products Grid/List */}
            {isLoading ? (
              <div className="products-loading">
                <div className="spinner-large"></div>
                <p>Loading products...</p>
              </div>
            ) : products.length === 0 ? (
              <motion.div 
                className="products-empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <div className="empty-icon">🔍</div>
                <h3>No products found</h3>
                <p>Try adjusting your filters or search criteria</p>
                <Button variant="primary" onClick={clearFilters}>
                  Clear Filters
                </Button>
              </motion.div>
            ) : (
              <>
                <div className={`products-grid ${viewMode}`}>
                  {products.map((product, index) => (
                    <ProductCard 
                      key={product.id} 
                      product={product} 
                      index={index}
                    />
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="pagination">
                    <Button
                      variant="secondary"
                      disabled={page === 1}
                      onClick={() => setPage(page - 1)}
                    >
                      ← Previous
                    </Button>
                    
                    <div className="pagination-pages">
                      {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                        <button
                          key={p}
                          className={`page-btn ${p === page ? 'active' : ''}`}
                          onClick={() => setPage(p)}
                        >
                          {p}
                        </button>
                      ))}
                    </div>
                    
                    <Button
                      variant="secondary"
                      disabled={page === totalPages}
                      onClick={() => setPage(page + 1)}
                    >
                      Next →
                    </Button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
