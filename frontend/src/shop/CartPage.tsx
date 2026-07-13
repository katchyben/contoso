import { Link as RouterLink, useNavigate } from 'react-router-dom'
import {
  Box,
  Button,
  IconButton,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import { useCart } from './CartContext'

export function CartPage() {
  const { lines, subtotal, updateQuantity, removeItem } = useCart()
  const navigate = useNavigate()

  if (lines.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Your cart is empty
        </Typography>
        <Button component={RouterLink} to="/" variant="contained">
          Browse products
        </Button>
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>
        Cart
      </Typography>
      <TableContainer component={Paper} variant="outlined" sx={{ mb: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Product</TableCell>
              <TableCell align="right">Unit price</TableCell>
              <TableCell align="center">Quantity</TableCell>
              <TableCell align="right">Line total</TableCell>
              <TableCell align="right">Remove</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {lines.map((line) => (
              <TableRow key={line.product.id}>
                <TableCell>{line.product.name}</TableCell>
                <TableCell align="right" sx={{ fontFamily: '"IBM Plex Mono", monospace' }}>
                  ${Number(line.product.unit_price).toFixed(2)}
                </TableCell>
                <TableCell align="center">
                  <TextField
                    type="number"
                    size="small"
                    value={line.quantity}
                    onChange={(e) => updateQuantity(line.product.id, Number(e.target.value))}
                    slotProps={{ htmlInput: { min: 1, style: { width: 56, textAlign: 'center' } } }}
                  />
                </TableCell>
                <TableCell align="right" sx={{ fontFamily: '"IBM Plex Mono", monospace' }}>
                  ${(Number(line.product.unit_price) * line.quantity).toFixed(2)}
                </TableCell>
                <TableCell align="right">
                  <IconButton size="small" onClick={() => removeItem(line.product.id)} aria-label="remove">
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Stack direction="row" sx={{ justifyContent: 'flex-end', alignItems: 'center', gap: 3 }}>
        <Typography sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '1.1rem' }}>
          Subtotal: ${subtotal.toFixed(2)}
        </Typography>
        <Button variant="contained" onClick={() => navigate('/checkout')}>
          Proceed to checkout
        </Button>
      </Stack>
    </Box>
  )
}
