import { useState } from 'react'
import { motion } from 'framer-motion'
import './StarRating.css'

export default function StarRating({ 
  rating = 0, 
  maxStars = 5, 
  size = 'medium',
  interactive = false,
  onChange = null,
  showCount = false,
  count = 0
}) {
  const [hoverRating, setHoverRating] = useState(0)
  const [selectedRating, setSelectedRating] = useState(rating)

  const handleClick = (value) => {
    if (!interactive) return
    setSelectedRating(value)
    onChange?.(value)
  }

  const handleMouseEnter = (value) => {
    if (!interactive) return
    setHoverRating(value)
  }

  const handleMouseLeave = () => {
    if (!interactive) return
    setHoverRating(0)
  }

  const displayRating = interactive ? (hoverRating || selectedRating) : rating

  return (
    <div className={`star-rating ${size} ${interactive ? 'interactive' : ''}`}>
      <div className="stars">
        {[...Array(maxStars)].map((_, index) => {
          const starValue = index + 1
          const isFilled = starValue <= displayRating
          const isPartial = !isFilled && starValue - 0.5 <= displayRating

          return (
            <motion.button
              key={index}
              type="button"
              className={`star ${isFilled ? 'filled' : ''} ${isPartial ? 'partial' : ''}`}
              onClick={() => handleClick(starValue)}
              onMouseEnter={() => handleMouseEnter(starValue)}
              onMouseLeave={handleMouseLeave}
              disabled={!interactive}
              whileHover={interactive ? { scale: 1.1 } : {}}
              whileTap={interactive ? { scale: 0.95 } : {}}
            >
              {isPartial ? (
                <span className="star-icon">
                  <span className="star-half">★</span>
                  <span className="star-empty">☆</span>
                </span>
              ) : (
                <span className="star-icon">{isFilled ? '★' : '☆'}</span>
              )}
            </motion.button>
          )
        })}
      </div>
      {showCount && count > 0 && (
        <span className="rating-count">({count})</span>
      )}
    </div>
  )
}
