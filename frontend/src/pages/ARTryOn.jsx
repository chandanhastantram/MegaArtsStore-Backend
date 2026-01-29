import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import Button from '../components/common/Button'
import './ARTryOn.css'

export default function ARTryOn() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [cameraActive, setCameraActive] = useState(false)
  const [screenshot, setScreenshot] = useState(null)

  const handleStartAR = () => {
    // In production, this would activate the device camera
    // and overlay the 3D model using AR libraries
    setCameraActive(true)
  }

  const handleCapture = () => {
    // Mock screenshot capture
    setScreenshot('/ar-screenshot-demo.jpg')
  }

  const handleShare = () => {
    // Mock share functionality
    if (navigator.share) {
      navigator.share({
        title: 'My AR Try-On',
        text: 'Check out how this looks on me!',
        url: window.location.href
      })
    }
  }

  return (
    <div className="ar-page">
      {!cameraActive ? (
        <motion.div
          className="ar-intro"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="ar-intro-content">
            <h1 className="font-display">AR Try-On</h1>
            <p>Experience our jewellery in augmented reality</p>
            
            <div className="ar-instructions">
              <div className="instruction">
                <span className="instruction-icon">📱</span>
                <p>Allow camera access</p>
              </div>
              <div className="instruction">
                <span className="instruction-icon">✋</span>
                <p>Show your wrist to the camera</p>
              </div>
              <div className="instruction">
                <span className="instruction-icon">📸</span>
                <p>Capture and share</p>
              </div>
            </div>

            <div className="ar-actions">
              <Button variant="primary" size="large" onClick={handleStartAR}>
                Start AR Experience
              </Button>
              <Button variant="secondary" onClick={() => navigate(-1)}>
                Go Back
              </Button>
            </div>

            <p className="ar-note">
              Note: AR features work best on mobile devices with AR support
            </p>
          </div>
        </motion.div>
      ) : (
        <div className="ar-camera">
          <div className="ar-camera-view">
            {/* In production, this would be the camera feed with AR overlay */}
            <div className="camera-placeholder">
              <p>📱 Camera View</p>
              <p className="camera-hint">AR overlay would appear here</p>
            </div>
          </div>

          <div className="ar-controls">
            <Button variant="secondary" onClick={() => setCameraActive(false)}>
              Exit AR
            </Button>
            <Button variant="primary" onClick={handleCapture}>
              📸 Capture
            </Button>
            {screenshot && (
              <Button variant="dark" onClick={handleShare}>
                Share
              </Button>
            )}
          </div>

          {screenshot && (
            <motion.div
              className="ar-screenshot-preview"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <img src={screenshot} alt="AR Screenshot" />
              <p>Screenshot saved!</p>
            </motion.div>
          )}
        </div>
      )}
    </div>
  )
}
