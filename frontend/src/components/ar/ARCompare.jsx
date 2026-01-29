import { useState } from 'react'
import { motion } from 'framer-motion'
import Button from '../common/Button'
import './ARCompare.css'

export default function ARCompare({ screenshots = [], onClose }) {
  const [selectedImages, setSelectedImages] = useState([screenshots[0], screenshots[1]].filter(Boolean))

  const toggleImage = (image) => {
    if (selectedImages.includes(image)) {
      setSelectedImages(selectedImages.filter(img => img !== image))
    } else if (selectedImages.length < 2) {
      setSelectedImages([...selectedImages, image])
    }
  }

  return (
    <div className="ar-compare">
      <div className="compare-header">
        <h3>Compare AR Try-Ons</h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      {/* Comparison View */}
      <div className="comparison-view">
        {selectedImages.length === 2 ? (
          <>
            <div className="compare-image">
              <img src={selectedImages[0].url} alt="Comparison 1" />
              <span className="image-label">Image 1</span>
            </div>
            <div className="vs-divider">VS</div>
            <div className="compare-image">
              <img src={selectedImages[1].url} alt="Comparison 2" />
              <span className="image-label">Image 2</span>
            </div>
          </>
        ) : (
          <div className="select-prompt">
            <p>Select 2 images to compare</p>
            <p className="prompt-hint">
              {selectedImages.length === 0 ? 'Choose your first image' : 'Choose your second image'}
            </p>
          </div>
        )}
      </div>

      {/* Image Selector */}
      <div className="image-selector">
        <p className="selector-label">Select images ({selectedImages.length}/2)</p>
        <div className="selector-grid">
          {screenshots.map((screenshot, index) => (
            <motion.div
              key={screenshot.id || index}
              className={`selector-item ${selectedImages.includes(screenshot) ? 'selected' : ''}`}
              onClick={() => toggleImage(screenshot)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <img src={screenshot.url} alt={`Option ${index + 1}`} />
              {selectedImages.includes(screenshot) && (
                <div className="selected-badge">
                  {selectedImages.indexOf(screenshot) + 1}
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
