import './Skeleton.css'

// Base skeleton component
export function Skeleton({ width, height, variant = 'rectangular', className = '' }) {
  return (
    <div 
      className={`skeleton skeleton-${variant} ${className}`}
      style={{ width, height }}
    />
  )
}

// Product card skeleton
export function ProductCardSkeleton() {
  return (
    <div className="product-card-skeleton">
      <Skeleton variant="rectangular" height="280px" className="skeleton-image" />
      <div className="skeleton-content">
        <Skeleton width="70%" height="20px" />
        <Skeleton width="50%" height="16px" />
        <Skeleton width="40%" height="24px" />
      </div>
    </div>
  )
}

// Product grid skeleton
export function ProductGridSkeleton({ count = 8 }) {
  return (
    <div className="products-grid-skeleton">
      {Array.from({ length: count }).map((_, i) => (
        <ProductCardSkeleton key={i} />
      ))}
    </div>
  )
}

// Table row skeleton
export function TableRowSkeleton({ columns = 5 }) {
  return (
    <tr className="table-row-skeleton">
      {Array.from({ length: columns }).map((_, i) => (
        <td key={i}>
          <Skeleton width="80%" height="16px" />
        </td>
      ))}
    </tr>
  )
}

// Text skeleton
export function TextSkeleton({ lines = 3 }) {
  return (
    <div className="text-skeleton">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton 
          key={i} 
          width={i === lines - 1 ? '60%' : '100%'} 
          height="16px" 
        />
      ))}
    </div>
  )
}

// Stats card skeleton
export function StatsCardSkeleton() {
  return (
    <div className="stats-card-skeleton">
      <Skeleton width="40px" height="40px" variant="circular" />
      <div>
        <Skeleton width="100px" height="14px" />
        <Skeleton width="60px" height="24px" />
      </div>
    </div>
  )
}

export default Skeleton
