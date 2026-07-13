import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { Alert, Box, Button, Paper, Stack, TextField, Typography } from '@mui/material'
import { useAuth } from '../auth/AuthContext'
import { checkout } from '../api/client'
import { useCart } from './CartContext'
import { AuthPanel } from './AuthPanel'

function AddressAndPlaceOrder() {
  const { lines, subtotal, clear } = useCart()
  const navigate = useNavigate()
  const [line1, setLine1] = useState('')
  const [line2, setLine2] = useState('')
  const [city, setCity] = useState('')
  const [state, setState] = useState('')
  const [postalCode, setPostalCode] = useState('')
  const [country, setCountry] = useState('US')
  const [error, setError] = useState<string | null>(null)
  const [placing, setPlacing] = useState(false)

  const handlePlaceOrder = async (event: FormEvent) => {
    event.preventDefault()
    setPlacing(true)
    setError(null)
    try {
      const order = await checkout({
        shipping_address: {
          line1,
          line2: line2 || undefined,
          city,
          state: state || undefined,
          postal_code: postalCode,
          country,
        },
        items: lines.map((l) => ({ product_id: l.product.id, quantity: l.quantity })),
      })
      clear()
      navigate(`/orders/${order.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Checkout failed')
    } finally {
      setPlacing(false)
    }
  }

  return (
    <Box component="form" onSubmit={handlePlaceOrder} sx={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
      <Paper variant="outlined" sx={{ p: 4, flex: '1 1 380px' }}>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Shipping address
        </Typography>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <Stack spacing={2}>
          <TextField label="Address line 1" value={line1} onChange={(e) => setLine1(e.target.value)} required fullWidth />
          <TextField label="Address line 2" value={line2} onChange={(e) => setLine2(e.target.value)} fullWidth />
          <Stack direction="row" spacing={2}>
            <TextField label="City" value={city} onChange={(e) => setCity(e.target.value)} required fullWidth />
            <TextField label="State" value={state} onChange={(e) => setState(e.target.value)} fullWidth />
          </Stack>
          <Stack direction="row" spacing={2}>
            <TextField
              label="Postal code"
              value={postalCode}
              onChange={(e) => setPostalCode(e.target.value)}
              required
              fullWidth
            />
            <TextField
              label="Country (ISO-2)"
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              required
              fullWidth
            />
          </Stack>
          <Button type="submit" variant="contained" disabled={placing}>
            {placing ? 'Placing order…' : `Place order — $${subtotal.toFixed(2)}+`}
          </Button>
        </Stack>
      </Paper>

      <Paper variant="outlined" sx={{ p: 4, flex: '1 1 260px', height: 'fit-content' }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Order summary
        </Typography>
        <Stack spacing={1}>
          {lines.map((l) => (
            <Stack key={l.product.id} direction="row" sx={{ justifyContent: 'space-between' }}>
              <Typography variant="body2">
                {l.product.name} × {l.quantity}
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: '"IBM Plex Mono", monospace' }}>
                ${(Number(l.product.unit_price) * l.quantity).toFixed(2)}
              </Typography>
            </Stack>
          ))}
        </Stack>
      </Paper>
    </Box>
  )
}

export function CheckoutPage() {
  const { user } = useAuth()
  const { lines } = useCart()

  if (lines.length === 0) {
    return <Alert severity="info">Your cart is empty — add something before checking out.</Alert>
  }

  if (user?.role === 'admin' || user?.role === 'staff') {
    return <Alert severity="warning">Staff accounts can't place orders. Sign in with a customer account.</Alert>
  }

  return user ? <AddressAndPlaceOrder /> : <AuthPanel title="Sign in to check out" />
}
