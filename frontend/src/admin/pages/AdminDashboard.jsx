import { useQuery } from '@tanstack/react-query'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { motion } from 'framer-motion'
import StatsCard from '../components/StatsCard'
import adminService from '../../services/adminService'
import './AdminDashboard.css'

export default function AdminDashboard() {
  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ['admin-overview'],
    queryFn: () => adminService.getOverview()
  })

  const { data: salesReport } = useQuery({
    queryKey: ['sales-report', 30],
    queryFn: () => adminService.getSalesReport(30)
  })

  const { data: topProducts } = useQuery({
    queryKey: ['top-products'],
    queryFn: () => adminService.getTopProducts(5, 30)
  })

  const { data: orderStatus } = useQuery({
    queryKey: ['order-status'],
    queryFn: () => adminService.getOrderStatusBreakdown(30)
  })

  const stats = overview?.data || {}
  const dailySales = salesReport?.data?.daily_data || []
  const products = topProducts?.data?.products || []
  const statusBreakdown = orderStatus?.data?.breakdown || {}

  // Prepare chart data
  const statusData = Object.entries(statusBreakdown).map(([status, data]) => ({
    name: status.charAt(0).toUpperCase() + status.slice(1),
    value: data.count,
    revenue: data.revenue
  }))

  const COLORS = ['#10b981', '#f59e0b', '#3b82f6', '#ef4444', '#8b5cf6']

  if (overviewLoading) {
    return <div className="admin-loading">Loading dashboard...</div>
  }

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <h1>Dashboard Overview</h1>
        <p>Welcome back! Here's what's happening with your store.</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <StatsCard
          title="Total Revenue"
          value={`₹${stats.total_revenue?.toLocaleString() || 0}`}
          icon="💰"
          trend="up"
          trendValue="+12.5%"
          color="green"
        />
        <StatsCard
          title="Total Orders"
          value={stats.total_orders || 0}
          icon="🛒"
          trend="up"
          trendValue="+8.2%"
          color="blue"
        />
        <StatsCard
          title="Total Users"
          value={stats.total_users || 0}
          icon="👥"
          trend="up"
          trendValue="+15.3%"
          color="purple"
        />
        <StatsCard
          title="Pending Orders"
          value={stats.pending_orders || 0}
          icon="⏳"
          color="gold"
        />
      </div>

      {/* Charts Row */}
      <div className="charts-grid">
        {/* Sales Trend */}
        <motion.div
          className="chart-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h3>Sales Trend (Last 30 Days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={dailySales}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={2} />
              <Line type="monotone" dataKey="orders" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Order Status */}
        <motion.div
          className="chart-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <h3>Order Status Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Top Products */}
      <motion.div
        className="top-products-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h3>Top Selling Products</h3>
        <div className="products-table">
          <table>
            <thead>
              <tr>
                <th>Product</th>
                <th>Sold</th>
                <th>Revenue</th>
                <th>Stock</th>
                <th>AR</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product, index) => (
                <tr key={index}>
                  <td className="product-name">{product.product_name}</td>
                  <td>{product.quantity_sold}</td>
                  <td>₹{product.revenue.toLocaleString()}</td>
                  <td className={product.current_stock < 10 ? 'low-stock' : ''}>
                    {product.current_stock}
                  </td>
                  <td>{product.ar_enabled ? '✅' : '❌'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Quick Stats */}
      <div className="quick-stats">
        <div className="stat-item">
          <span className="stat-label">Today's Orders</span>
          <span className="stat-value">{stats.today_orders || 0}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Today's Revenue</span>
          <span className="stat-value">₹{stats.today_revenue?.toLocaleString() || 0}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">AR Products</span>
          <span className="stat-value">{stats.ar_enabled_products || 0}</span>
        </div>
      </div>
    </div>
  )
}
