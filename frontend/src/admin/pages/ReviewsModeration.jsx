import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { reviewsAPI } from '../../services/api'
import { StatusBadge } from '../../components/common/Badge'
import StarRating from '../../components/common/StarRating'
import Modal from '../../components/common/Modal'
import Button from '../../components/common/Button'
import useToast from '../../hooks/useToast'
import './ReviewsModeration.css'

export default function ReviewsModeration() {
  const [filterStatus, setFilterStatus] = useState('pending')
  const [selectedReview, setSelectedReview] = useState(null)
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['admin-reviews', filterStatus],
    queryFn: () => reviewsAPI.getAll?.({ status: filterStatus !== 'all' ? filterStatus : undefined })
  })

  const moderateMutation = useMutation({
    mutationFn: ({ reviewId, action }) => reviewsAPI.moderate?.(reviewId, action),
    onSuccess: (_, { action }) => {
      queryClient.invalidateQueries(['admin-reviews'])
      toast.success(`Review ${action === 'approve' ? 'approved' : 'rejected'}`)
      setSelectedReview(null)
    },
    onError: () => toast.error('Failed to moderate review')
  })

  const reviews = data?.data || []

  const handleModerate = (reviewId, action) => {
    moderateMutation.mutate({ reviewId, action })
  }

  // Stats
  const pendingCount = reviews.filter(r => r.status === 'pending').length
  const approvedCount = reviews.filter(r => r.status === 'approved').length
  const rejectedCount = reviews.filter(r => r.status === 'rejected').length

  return (
    <div className="reviews-moderation">
      <div className="page-header">
        <h1>Reviews Moderation</h1>
        <p>Review and moderate customer feedback</p>
      </div>

      {/* Stats */}
      <div className="reviews-stats">
        <div className="stat-card warning">
          <span className="stat-value">{pendingCount}</span>
          <span className="stat-label">Pending</span>
        </div>
        <div className="stat-card success">
          <span className="stat-value">{approvedCount}</span>
          <span className="stat-label">Approved</span>
        </div>
        <div className="stat-card danger">
          <span className="stat-value">{rejectedCount}</span>
          <span className="stat-label">Rejected</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="filter-tabs">
        {[
          { key: 'pending', label: 'Pending', count: pendingCount },
          { key: 'approved', label: 'Approved' },
          { key: 'rejected', label: 'Rejected' },
          { key: 'all', label: 'All' }
        ].map(({ key, label, count }) => (
          <button
            key={key}
            className={filterStatus === key ? 'active' : ''}
            onClick={() => setFilterStatus(key)}
          >
            {label}
            {count > 0 && <span className="count">{count}</span>}
          </button>
        ))}
      </div>

      {/* Reviews List */}
      {isLoading ? (
        <div className="loading-state">Loading reviews...</div>
      ) : reviews.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">⭐</div>
          <h3>No reviews found</h3>
          <p>No reviews match the current filter</p>
        </div>
      ) : (
        <div className="reviews-list">
          {reviews.map((review, index) => (
            <motion.div
              key={review.id}
              className="review-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.03 }}
            >
              <div className="review-header">
                <div className="review-product">
                  <img 
                    src={review.product?.images?.[0] || '/placeholder.jpg'} 
                    alt={review.product?.name}
                    className="product-thumb"
                  />
                  <div>
                    <span className="product-name">{review.product?.name || 'Unknown Product'}</span>
                    <span className="customer-name">by {review.user?.name || 'Anonymous'}</span>
                  </div>
                </div>
                <StatusBadge status={review.status} />
              </div>

              <div className="review-content">
                <div className="review-rating">
                  <StarRating rating={review.rating} size="small" />
                  <span className="rating-value">({review.rating}/5)</span>
                </div>
                {review.title && <h4 className="review-title">{review.title}</h4>}
                <p className="review-comment">{review.comment}</p>
                <span className="review-date">
                  {new Date(review.created_at).toLocaleDateString('en-IN', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric'
                  })}
                </span>
              </div>

              {review.status === 'pending' && (
                <div className="review-actions">
                  <Button 
                    variant="primary" 
                    size="small"
                    onClick={() => handleModerate(review.id, 'approve')}
                    loading={moderateMutation.isPending}
                  >
                    Approve
                  </Button>
                  <Button 
                    variant="secondary" 
                    size="small"
                    onClick={() => setSelectedReview(review)}
                  >
                    View Full
                  </Button>
                  <button 
                    className="reject-btn"
                    onClick={() => handleModerate(review.id, 'reject')}
                  >
                    Reject
                  </button>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      )}

      {/* Review Detail Modal */}
      <Modal
        isOpen={!!selectedReview}
        onClose={() => setSelectedReview(null)}
        title="Review Details"
        size="medium"
      >
        {selectedReview && (
          <div className="review-detail-modal">
            <div className="modal-product">
              <img 
                src={selectedReview.product?.images?.[0] || '/placeholder.jpg'} 
                alt={selectedReview.product?.name}
              />
              <div>
                <h4>{selectedReview.product?.name}</h4>
                <p>₹{selectedReview.product?.price?.toLocaleString()}</p>
              </div>
            </div>

            <div className="modal-reviewer">
              <h5>Reviewer</h5>
              <p>{selectedReview.user?.name} ({selectedReview.user?.email})</p>
            </div>

            <div className="modal-rating">
              <StarRating rating={selectedReview.rating} />
            </div>

            {selectedReview.title && (
              <div className="modal-title">
                <h5>Title</h5>
                <p>{selectedReview.title}</p>
              </div>
            )}

            <div className="modal-comment">
              <h5>Review</h5>
              <p>{selectedReview.comment}</p>
            </div>

            {selectedReview.status === 'pending' && (
              <div className="modal-actions">
                <Button 
                  variant="primary"
                  onClick={() => handleModerate(selectedReview.id, 'approve')}
                  loading={moderateMutation.isPending}
                >
                  Approve Review
                </Button>
                <Button 
                  variant="secondary"
                  onClick={() => handleModerate(selectedReview.id, 'reject')}
                >
                  Reject Review
                </Button>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}
