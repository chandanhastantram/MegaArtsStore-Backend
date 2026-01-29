import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { usersAPI } from '../../services/api'
import { StatusBadge, RoleBadge } from '../../components/common/Badge'
import Modal from '../../components/common/Modal'
import Button from '../../components/common/Button'
import { TableRowSkeleton } from '../../components/common/Skeleton'
import useToast from '../../hooks/useToast'
import './UsersManagement.css'

export default function UsersManagement() {
  const [selectedUser, setSelectedUser] = useState(null)
  const [filterRole, setFilterRole] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['admin-users', filterRole],
    queryFn: () => usersAPI.getAll?.({ role: filterRole !== 'all' ? filterRole : undefined })
  })

  const updateRoleMutation = useMutation({
    mutationFn: ({ userId, role }) => usersAPI.updateRole?.(userId, role),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-users'])
      toast.success('User role updated')
    },
    onError: () => toast.error('Failed to update role')
  })

  const toggleStatusMutation = useMutation({
    mutationFn: ({ userId, isActive }) => usersAPI.toggleStatus?.(userId, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-users'])
      toast.success('User status updated')
    },
    onError: () => toast.error('Failed to update status')
  })

  const users = data?.data || []
  const filteredUsers = users.filter(user => 
    user.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="users-management">
      <div className="page-header">
        <h1>Users Management</h1>
        <p>Manage user accounts and permissions</p>
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search users..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-tabs">
          {['all', 'user', 'admin'].map(role => (
            <button
              key={role}
              className={filterRole === role ? 'active' : ''}
              onClick={() => setFilterRole(role)}
            >
              {role.charAt(0).toUpperCase() + role.slice(1)}s
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="users-stats">
        <div className="stat-card">
          <span className="stat-icon">👥</span>
          <div>
            <span className="stat-value">{users.length}</span>
            <span className="stat-label">Total Users</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">👤</span>
          <div>
            <span className="stat-value">{users.filter(u => u.role === 'user').length}</span>
            <span className="stat-label">Customers</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">🛡️</span>
          <div>
            <span className="stat-value">{users.filter(u => u.role === 'admin').length}</span>
            <span className="stat-label">Admins</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">✓</span>
          <div>
            <span className="stat-value">{users.filter(u => u.is_active).length}</span>
            <span className="stat-label">Active</span>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th>User</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Joined</th>
              <th>Orders</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRowSkeleton key={i} columns={7} />
              ))
            ) : filteredUsers.length === 0 ? (
              <tr>
                <td colSpan={7} className="empty-row">
                  No users found
                </td>
              </tr>
            ) : (
              filteredUsers.map((user, index) => (
                <motion.tr
                  key={user.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.03 }}
                >
                  <td>
                    <div className="user-cell">
                      <div className="user-avatar">
                        {user.name?.charAt(0).toUpperCase() || 'U'}
                      </div>
                      <span className="user-name">{user.name || 'N/A'}</span>
                    </div>
                  </td>
                  <td className="user-email">{user.email}</td>
                  <td><RoleBadge role={user.role} /></td>
                  <td>
                    <StatusBadge status={user.is_active ? 'active' : 'inactive'} />
                  </td>
                  <td className="join-date">
                    {new Date(user.created_at).toLocaleDateString('en-IN', {
                      day: 'numeric',
                      month: 'short',
                      year: 'numeric'
                    })}
                  </td>
                  <td>{user.orders_count || 0}</td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="action-btn view"
                        onClick={() => setSelectedUser(user)}
                      >
                        View
                      </button>
                      <button 
                        className={`action-btn ${user.is_active ? 'disable' : 'enable'}`}
                        onClick={() => toggleStatusMutation.mutate({ 
                          userId: user.id, 
                          isActive: !user.is_active 
                        })}
                      >
                        {user.is_active ? 'Disable' : 'Enable'}
                      </button>
                    </div>
                  </td>
                </motion.tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* User Details Modal */}
      <Modal
        isOpen={!!selectedUser}
        onClose={() => setSelectedUser(null)}
        title="User Details"
        size="medium"
      >
        {selectedUser && (
          <div className="user-details-modal">
            <div className="user-profile">
              <div className="user-avatar-large">
                {selectedUser.name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <h3>{selectedUser.name}</h3>
              <p>{selectedUser.email}</p>
              <div className="user-badges">
                <RoleBadge role={selectedUser.role} />
                <StatusBadge status={selectedUser.is_active ? 'active' : 'inactive'} />
              </div>
            </div>

            <div className="user-info-grid">
              <div className="info-item">
                <span className="label">Phone</span>
                <span className="value">{selectedUser.phone || 'Not provided'}</span>
              </div>
              <div className="info-item">
                <span className="label">Joined</span>
                <span className="value">
                  {new Date(selectedUser.created_at).toLocaleDateString('en-IN', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                  })}
                </span>
              </div>
              <div className="info-item">
                <span className="label">Total Orders</span>
                <span className="value">{selectedUser.orders_count || 0}</span>
              </div>
              <div className="info-item">
                <span className="label">Total Spent</span>
                <span className="value">₹{selectedUser.total_spent?.toLocaleString() || 0}</span>
              </div>
            </div>

            <div className="role-update">
              <label>Update Role:</label>
              <div className="role-buttons">
                {['user', 'admin'].map(role => (
                  <button
                    key={role}
                    className={selectedUser.role === role ? 'active' : ''}
                    onClick={() => {
                      updateRoleMutation.mutate({ userId: selectedUser.id, role })
                      setSelectedUser({ ...selectedUser, role })
                    }}
                  >
                    {role.charAt(0).toUpperCase() + role.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
