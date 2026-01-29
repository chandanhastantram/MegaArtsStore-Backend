import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import './ImageLightbox.css'

export default function ImageLightbox({ images, isOpen, onClose, initialIndex = 0 }) {
  const [currentIndex, setCurrentIndex] = useState(initialIndex)

  const handlePrevious = (e) => {
    e.stopPropagation()
    setCurrentIndex(prev => (prev - 1 + images.length) % images.length)
  }

  const handleNext = (e) => {
    e.stopPropagation()
    setCurrentIndex(prev => (prev + 1) % images.length)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowLeft') handlePrevious(e)
    if (e.key === 'ArrowRight') handleNext(e)
    if (e.key === 'Escape') onClose()
  }

  if (!isOpen || !images?.length) return null

  return (
    <AnimatePresence>
      <motion.div
        className="lightbox-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        onKeyDown={handleKeyDown}
        tabIndex={0}
      >
        {/* Close button */}
        <button className="lightbox-close" onClick={onClose}>✕</button>

        {/* Counter */}
        <div className="lightbox-counter">
          {currentIndex + 1} / {images.length}
        </div>

        {/* Navigation */}
        {images.length > 1 && (
          <>
            <button className="lightbox-nav lightbox-prev" onClick={handlePrevious}>
              ‹
            </button>
            <button className="lightbox-nav lightbox-next" onClick={handleNext}>
              ›
            </button>
          </>
        )}

        {/* Main Image */}
        <motion.div
          className="lightbox-content"
          key={currentIndex}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          onClick={e => e.stopPropagation()}
        >
          <img
            src={images[currentIndex]}
            alt=""
            className="lightbox-image"
          />
        </motion.div>

        {/* Thumbnails */}
        {images.length > 1 && (
          <div className="lightbox-thumbnails">
            {images.map((img, index) => (
              <button
                key={index}
                className={`lightbox-thumb ${currentIndex === index ? 'active' : ''}`}
                onClick={(e) => {
                  e.stopPropagation()
                  setCurrentIndex(index)
                }}
              >
                <img src={img} alt="" />
              </button>
            ))}
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  )
}
