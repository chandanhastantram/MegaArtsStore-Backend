import './Button.css'

export default function Button({ 
  children, 
  variant = 'primary', 
  size = 'medium',
  loading = false,
  disabled = false,
  onClick,
  type = 'button',
  className = '',
  ...props 
}) {
  return (
    <button
      type={type}
      className={`btn btn-${variant} btn-${size} ${className} ${loading ? 'btn-loading' : ''}`}
      onClick={onClick}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? 'Loading...' : children}
    </button>
  )
}
