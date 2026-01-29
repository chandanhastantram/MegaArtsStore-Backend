import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { productsAPI } from '../services/api'
import ProductCard from '../components/products/ProductCard'
import './Search.css'

export default function Search() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''
  
  const { data, isLoading } = useQuery({
    queryKey: ['search', query],
    queryFn: () => productsAPI.search(query),
    enabled: !!query
  })

  const products = data?.data?.products || []

  return (
    <div className="search-page">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="search-header">
            <h1 className="font-display">
              Search Results {query && `for "${query}"`}
            </h1>
            <p className="search-count">
              {products.length} products found
            </p>
          </div>

          {isLoading ? (
            <div className="search-loading">
              <div className="spinner-large"></div>
              <p>Searching...</p>
            </div>
          ) : products.length === 0 ? (
            <div className="search-empty">
              <div className="empty-icon">🔍</div>
              <h2>No results found</h2>
              <p>Try different keywords or browse our categories</p>
            </div>
          ) : (
            <div className="search-results">
              {products.map((product, index) => (
                <ProductCard key={product.id} product={product} index={index} />
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}
