import { useState } from 'react'
import { motion } from 'framer-motion'
import Modal from '../common/Modal'
import Button from '../common/Button'
import useToast from '../../hooks/useToast'
import './ShareModal.css'

export default function ShareModal({ image, onClose }) {
  const { toast } = useToast()
  const [copying, setCopying] = useState(false)

  const shareOptions = [
    { name: 'WhatsApp', icon: '💬', color: '#25D366', action: 'whatsapp' },
    { name: 'Facebook', icon: '📘', color: '#1877F2', action: 'facebook' },
    { name: 'Twitter', icon: '🐦', color: '#1DA1F2', action: 'twitter' },
    { name: 'Instagram', icon: '📷', color: '#E4405F', action: 'instagram' },
  ]

  const handleShare = async (platform) => {
    const shareUrl = window.location.href
    const shareText = 'Check out how this looks on me! 💍'

    const urls = {
      whatsapp: `https://wa.me/?text=${encodeURIComponent(shareText + ' ' + shareUrl)}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`,
      twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`,
      instagram: shareUrl // Instagram doesn't support direct sharing via URL
    }

    if (platform === 'instagram') {
      toast.info('Save the image and share it on Instagram!')
      return
    }

    window.open(urls[platform], '_blank', 'width=600,height=400')
    toast.success(`Sharing to ${platform}!`)
  }

  const handleCopyLink = async () => {
    setCopying(true)
    try {
      await navigator.clipboard.writeText(window.location.href)
      toast.success('Link copied to clipboard!')
    } catch (error) {
      toast.error('Failed to copy link')
    } finally {
      setCopying(false)
    }
  }

  const handleNativeShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'My AR Try-On',
          text: 'Check out how this looks on me!',
          url: window.location.href
        })
        toast.success('Shared successfully!')
      } catch (error) {
        if (error.name !== 'AbortError') {
          toast.error('Failed to share')
        }
      }
    } else {
      toast.info('Sharing not supported on this device')
    }
  }

  return (
    <Modal isOpen onClose={onClose} size="medium">
      <div className="share-modal">
        <h3>Share Your AR Try-On</h3>

        <div className="preview-image">
          <img src={image?.url} alt="AR Try-on" />
        </div>

        <div className="share-options">
          {shareOptions.map((option) => (
            <motion.button
              key={option.action}
              className="share-option"
              onClick={() => handleShare(option.action)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="option-icon" style={{ background: option.color }}>
                {option.icon}
              </span>
              <span className="option-name">{option.name}</span>
            </motion.button>
          ))}
        </div>

        <div className="share-actions">
          <Button
            variant="secondary"
            onClick={handleCopyLink}
            loading={copying}
          >
            📋 Copy Link
          </Button>
          
          {navigator.share && (
            <Button variant="primary" onClick={handleNativeShare}>
              📤 Share
            </Button>
          )}
        </div>
      </div>
    </Modal>
  )
}
