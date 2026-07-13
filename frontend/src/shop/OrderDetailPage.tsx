import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import { fetchMyOrderDetail, type OrderDetail } from '../api/client'
import { styleForStatus } from '../config/statusStyles'

export function OrderDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [order, setOrder] = useState<OrderDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    fetchMyOrderDetail(Number(id))
      .then(setOrder)
      .catch((err) => setError(err instanceof Error ? err.message : 'Order not found'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 6 }}>
        <CircularProgress size={28} sx={{ color: '#f2a541' }} />
      </Box>
    )
  }

  if (error || !order) {
    return <Alert severity="error">{error ?? 'Order not found'}</Alert>
  }

  const style = styleForStatus(order.status)

  return (
    <Box>
      <Stack direction="row" sx={{ alignItems: 'center', gap: 2, mb: 3 }}>
        <Typography variant="h5" sx={{ fontFamily: '"IBM Plex Mono", monospace' }}>
          {order.order_number}
        </Typography>
        <Chip
          label={order.status}
          sx={{ bgcolor: style.bg, color: style.fg, border: '1px solid', borderColor: style.border }}
        />
      </Stack>

      <TableContainer component={Paper} variant="outlined" sx={{ mb: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Product ID</TableCell>
              <TableCell align="center">Quantity</TableCell>
              <TableCell align="right">Unit price</TableCell>
              <TableCell align="right">Line total</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {order.items.map((item) => (
              <TableRow key={item.id}>
                <TableCell sx={{ fontFamily: '"IBM Plex Mono", monospace' }}>{item.product_id}</TableCell>
                <TableCell align="center">{item.quantity}</TableCell>
                <TableCell align="right" sx={{ fontFamily: '"IBM Plex Mono", monospace' }}>
                  ${Number(item.unit_price).toFixed(2)}
                </TableCell>
                <TableCell align="right" sx={{ fontFamily: '"IBM Plex Mono", monospace' }}>
                  ${Number(item.total_price).toFixed(2)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Paper variant="outlined" sx={{ p: 3, maxWidth: 320, ml: 'auto' }}>
        <Stack spacing={1}>
          <Stack direction="row" sx={{ justifyContent: 'space-between' }}>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              Subtotal
            </Typography>
            <Typography sx={{ fontFamily: '"IBM Plex Mono", monospace' }}>
              ${Number(order.subtotal).toFixed(2)}
            </Typography>
          </Stack>
          <Stack direction="row" sx={{ justifyContent: 'space-between' }}>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              Tax
            </Typography>
            <Typography sx={{ fontFamily: '"IBM Plex Mono", monospace' }}>
              ${Number(order.tax_amount).toFixed(2)}
            </Typography>
          </Stack>
          <Stack direction="row" sx={{ justifyContent: 'space-between' }}>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              Shipping
            </Typography>
            <Typography sx={{ fontFamily: '"IBM Plex Mono", monospace' }}>
              ${Number(order.shipping_amount).toFixed(2)}
            </Typography>
          </Stack>
          <Stack direction="row" sx={{ justifyContent: 'space-between' }}>
            <Typography sx={{ fontWeight: 600 }}>Total</Typography>
            <Typography sx={{ fontFamily: '"IBM Plex Mono", monospace', fontWeight: 600 }}>
              ${Number(order.total_amount).toFixed(2)}
            </Typography>
          </Stack>
        </Stack>
      </Paper>
    </Box>
  )
}
