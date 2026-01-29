import { useState } from 'react'
import { motion } from 'framer-motion'
import Button from '../common/Button'
import StarRating from '../common/StarRating'
import { reviewsAPI } from '../../services/api'
import useToast from '../../hooks/useToast'
import './ReviewForm.css'

export default function ReviewForm({ productId, productName, onSuccess, onCancel }) {
  const [rating, setRating] = useState(0)
  const [title, setTitle] = useState('')
  const [comment, setComment] = useState('')
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (rating === 0) {
      toast.error('Please select a rating')
      return
    }
    
    if (!comment.trim()) {
      toast.error('Please write a review')
      return
    }

    setLoading(true)
    try {
      await reviewsAPI.add(productId, {
        rating,
        title,
        comment
      })
      toast.success('Review submitted successfully!')
      onSuccess?.()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit review')
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div 
      className="review-form"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <h3>Write a Review for {productName}</h3>
      
      <form onSubmit={handleSubmit}>
        {/* Rating */}
        <div className="form-group">
          <label>Your Rating *</label>
          <StarRating 
            rating={rating} 
            onRatingChange={setRating}
            interactive
            size="large"
          />
        </div>

        {/* Title */}
        <div className="form-group">
          <label htmlFor="review-title">Review Title</label>
          <input
            id="review-title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Summarize your review"
            className="form-input"
          />
        </div>

        {/* Comment */}
        <div className="form-group">
          <label htmlFor="review-comment">Your Review *</label>
          <textarea
            id="review-comment"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Share your experience with this product..."
            rows={5}
            className="form-textarea"
            required
          />
          <span className="char-count">{comment.length}/500</span>
        </div>

        {/* Actions */}
        <div className="review-form-actions">
          {onCancel && (
            <Button type="button" variant="secondary" onClick={onCancel}>
              Cancel
            </Button>
          )}
          <Button type="submit" variant="primary" loading={loading}>
            Submit Review
          </Button>
        </div>
      </form>
    </motion.div>
  )
}
