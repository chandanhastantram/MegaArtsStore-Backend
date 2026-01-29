import { Navigate } from 'react-router-dom'
import useAdminStore from '../../store/adminStore'

export default function AdminRoute({ children }) {
  const { admin, token } = useAdminStore()

  if (!token || !admin) {
    return <Navigate to="/admin/login" replace />
  }

  // TEMPORARILY DISABLED: Role verification for testing
  // Any logged-in user can access admin panel
  // Uncomment below to re-enable admin role check:
  /*
  if (admin.role !== 'admin' && admin.role !== 'sub_admin') {
    return <Navigate to="/" replace />
  }
  */

  return children
}
