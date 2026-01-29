import { motion } from 'framer-motion'
import './StatsCard.css'

export default function StatsCard({ title, value, icon, trend, trendValue, color = 'blue' }) {
  const isPositive = trend === 'up'

  return (
    <motion.div
      className={`stats-card stats-card-${color}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
    >
      <div className="stats-header">
        <div className="stats-info">
          <p className="stats-title">{title}</p>
          <h3 className="stats-value">{value}</h3>
        </div>
        <div className="stats-icon">{icon}</div>
      </div>

      {trendValue && (
        <div className={`stats-trend ${isPositive ? 'positive' : 'negative'}`}>
          <span className="trend-icon">{isPositive ? '↑' : '↓'}</span>
          <span className="trend-value">{trendValue}</span>
          <span className="trend-label">vs last month</span>
        </div>
      )}
    </motion.div>
  )
}
