import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts'
import { analyticsAPI } from '../../services/api'
import './Analytics.css'

export default function Analytics() {
  const { data: stats } = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: () => analyticsAPI.getStats?.()
  })

  // Mock data for demonstration
  const arUsageData = [
    { name: 'Jan', sessions: 120, conversions: 45 },
    { name: 'Feb', sessions: 180, conversions: 65 },
    { name: 'Mar', sessions: 250, conversions: 95 },
    { name: 'Apr', sessions: 310, conversions: 120 },
    { name: 'May', sessions: 420, conversions: 165 },
    { name: 'Jun', sessions: 380, conversions: 145 }
  ]

  const salesData = [
    { name: 'Mon', revenue: 45000, orders: 12 },
    { name: 'Tue', revenue: 52000, orders: 18 },
    { name: 'Wed', revenue: 38000, orders: 10 },
    { name: 'Thu', revenue: 67000, orders: 25 },
    { name: 'Fri', revenue: 89000, orders: 32 },
    { name: 'Sat', revenue: 125000, orders: 45 },
    { name: 'Sun', revenue: 98000, orders: 38 }
  ]

  const categoryData = [
    { name: 'Bangles', value: 35 },
    { name: 'Necklaces', value: 28 },
    { name: 'Rings', value: 20 },
    { name: 'Earrings', value: 17 }
  ]

  const topProducts = [
    { name: 'Gold Kundan Bangle Set', sales: 156, revenue: 624000 },
    { name: 'Diamond Necklace', sales: 89, revenue: 534000 },
    { name: 'Pearls Earrings', sales: 234, revenue: 351000 },
    { name: 'Ruby Ring', sales: 67, revenue: 268000 },
    { name: 'Emerald Pendant', sales: 45, revenue: 225000 }
  ]

  const COLORS = ['#B8860B', '#E8B4B8', '#F7E7CE', '#8B7355']

  const analytics = stats?.data || {}

  return (
    <div className="analytics-page">
      <div className="page-header">
        <h1>Analytics Dashboard</h1>
        <p>Track your store's performance and AR engagement</p>
      </div>

      {/* Key Metrics */}
      <div className="metrics-grid">
        <motion.div 
          className="metric-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="metric-icon revenue">💰</div>
          <div className="metric-content">
            <span className="metric-value">₹{(analytics.total_revenue || 5142000).toLocaleString()}</span>
            <span className="metric-label">Total Revenue</span>
            <span className="metric-change positive">+12.5%</span>
          </div>
        </motion.div>

        <motion.div 
          className="metric-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="metric-icon orders">📦</div>
          <div className="metric-content">
            <span className="metric-value">{analytics.total_orders || 1247}</span>
            <span className="metric-label">Total Orders</span>
            <span className="metric-change positive">+8.3%</span>
          </div>
        </motion.div>

        <motion.div 
          className="metric-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="metric-icon ar">🔮</div>
          <div className="metric-content">
            <span className="metric-value">{analytics.ar_sessions || 3842}</span>
            <span className="metric-label">AR Sessions</span>
            <span className="metric-change positive">+24.7%</span>
          </div>
        </motion.div>

        <motion.div 
          className="metric-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="metric-icon conversion">🎯</div>
          <div className="metric-content">
            <span className="metric-value">{analytics.ar_conversion || 38}%</span>
            <span className="metric-label">AR Conversion</span>
            <span className="metric-change positive">+5.2%</span>
          </div>
        </motion.div>
      </div>

      {/* Charts Row */}
      <div className="charts-grid">
        {/* Sales Chart */}
        <motion.div 
          className="chart-card"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        >
          <h3>Weekly Sales</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={salesData}>
              <defs>
                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#B8860B" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#B8860B" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="name" stroke="#666" />
              <YAxis stroke="#666" tickFormatter={(v) => `₹${v/1000}k`} />
              <Tooltip 
                contentStyle={{ background: '#1a1a1a', border: 'none', borderRadius: '8px' }}
                formatter={(value) => [`₹${value.toLocaleString()}`, 'Revenue']}
              />
              <Area 
                type="monotone" 
                dataKey="revenue" 
                stroke="#B8860B" 
                fill="url(#colorRevenue)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* AR Usage Chart */}
        <motion.div 
          className="chart-card"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
        >
          <h3>AR Engagement</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={arUsageData}>
              <XAxis dataKey="name" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip 
                contentStyle={{ background: '#1a1a1a', border: 'none', borderRadius: '8px' }}
              />
              <Line 
                type="monotone" 
                dataKey="sessions" 
                stroke="#E8B4B8" 
                strokeWidth={2}
                dot={{ fill: '#E8B4B8' }}
              />
              <Line 
                type="monotone" 
                dataKey="conversions" 
                stroke="#B8860B" 
                strokeWidth={2}
                dot={{ fill: '#B8860B' }}
              />
            </LineChart>
          </ResponsiveContainer>
          <div className="chart-legend">
            <span><span className="dot rose"></span> Sessions</span>
            <span><span className="dot gold"></span> Conversions</span>
          </div>
        </motion.div>
      </div>

      {/* Bottom Row */}
      <div className="bottom-grid">
        {/* Category Distribution */}
        <motion.div 
          className="chart-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h3>Sales by Category</h3>
          <div className="pie-chart-container">
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="pie-legend">
              {categoryData.map((item, index) => (
                <div key={item.name} className="legend-item">
                  <span className="legend-dot" style={{ background: COLORS[index] }}></span>
                  <span className="legend-label">{item.name}</span>
                  <span className="legend-value">{item.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Top Products */}
        <motion.div 
          className="chart-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h3>Top Products</h3>
          <div className="top-products">
            {topProducts.map((product, index) => (
              <div key={product.name} className="product-row">
                <span className="rank">#{index + 1}</span>
                <div className="product-info">
                  <span className="product-name">{product.name}</span>
                  <span className="product-sales">{product.sales} sales</span>
                </div>
                <span className="product-revenue">₹{(product.revenue / 1000).toFixed(0)}k</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
