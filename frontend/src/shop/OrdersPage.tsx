import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import { fetchMyOrders, type OrderSummary } from '../api/client'
import { styleForStatus } from '../config/statusStyles'

export function OrdersPage() {
  const [orders, setOrders] = useState<OrderSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchMyOrders()
      .then(setOrders)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load orders'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 6 }}>
        <CircularProgress size={28} sx={{ color: '#f2a541' }} />
      </Box>
    )
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>
  }

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>
        My Orders
      </Typography>
      {orders.length === 0 ? (
        <Typography sx={{ color: 'text.secondary' }}>You haven't placed any orders yet.</Typography>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Order #</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Total</TableCell>
                <TableCell>Placed</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {orders.map((order) => {
                const style = styleForStatus(order.status)
                return (
                  <TableRow
                    key={order.id}
                    hover
                    onClick={() => navigate(`/orders/${order.id}`)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell sx={{ fontFamily: '"IBM Plex Mono", monospace' }}>{order.order_number}</TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={order.status}
                        sx={{ bgcolor: style.bg, color: style.fg, border: '1px solid', borderColor: style.border }}
                      />
                    </TableCell>
                    <TableCell align="right" sx={{ fontFamily: '"IBM Plex Mono", monospace' }}>
                      ${Number(order.total_amount).toFixed(2)}
                    </TableCell>
                    <TableCell>{new Date(order.placed_at).toLocaleString()}</TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  )
}
