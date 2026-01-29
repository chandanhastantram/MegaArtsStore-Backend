import './Badge.css'

const variants = {
  success: 'badge-success',
  warning: 'badge-warning',
  error: 'badge-error',
  info: 'badge-info',
  gold: 'badge-gold',
  default: 'badge-default'
}

export default function Badge({ 
  children, 
  variant = 'default', 
  size = 'medium',
  dot = false 
}) {
  return (
    <span className={`badge ${variants[variant]} badge-${size}`}>
      {dot && <span className="badge-dot" />}
      {children}
    </span>
  )
}

// Predefined status badges
export function StatusBadge({ status }) {
  const statusConfig = {
    pending: { label: 'Pending', variant: 'warning' },
    processing: { label: 'Processing', variant: 'info' },
    shipped: { label: 'Shipped', variant: 'info' },
    delivered: { label: 'Delivered', variant: 'success' },
    cancelled: { label: 'Cancelled', variant: 'error' },
    active: { label: 'Active', variant: 'success' },
    inactive: { label: 'Inactive', variant: 'default' },
    approved: { label: 'Approved', variant: 'success' },
    rejected: { label: 'Rejected', variant: 'error' },
    'in-stock': { label: 'In Stock', variant: 'success' },
    'low-stock': { label: 'Low Stock', variant: 'warning' },
    'out-of-stock': { label: 'Out of Stock', variant: 'error' }
  }

  const config = statusConfig[status?.toLowerCase()] || { label: status, variant: 'default' }

  return (
    <Badge variant={config.variant} dot>
      {config.label}
    </Badge>
  )
}

export function RoleBadge({ role }) {
  const roleConfig = {
    admin: { label: 'Admin', variant: 'gold' },
    user: { label: 'User', variant: 'default' },
    superadmin: { label: 'Super Admin', variant: 'error' }
  }

  const config = roleConfig[role?.toLowerCase()] || { label: role, variant: 'default' }

  return <Badge variant={config.variant}>{config.label}</Badge>
}
