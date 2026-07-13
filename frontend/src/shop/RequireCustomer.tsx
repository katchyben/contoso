import type { ReactNode } from 'react'
import { Alert, Box, CircularProgress } from '@mui/material'
import { useAuth } from '../auth/AuthContext'
import { AuthPanel } from './AuthPanel'

export function RequireCustomer({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 6 }}>
        <CircularProgress size={28} sx={{ color: '#f2a541' }} />
      </Box>
    )
  }

  if (!user) {
    return <AuthPanel title="Sign in to view your orders" />
  }

  if (user.role !== 'customer') {
    return <Alert severity="warning">Only customer accounts have order history here.</Alert>
  }

  return <>{children}</>
}
