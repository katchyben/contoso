import { Link as RouterLink, Outlet, useNavigate } from 'react-router-dom'
import { AppBar, Badge, Box, Button, Container, Toolbar, Typography } from '@mui/material'
import ShoppingCartOutlined from '@mui/icons-material/ShoppingCartOutlined'
import { useAuth } from '../auth/AuthContext'
import { useCart } from './CartContext'

function BrandMark() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <rect x="1" y="1" width="18" height="18" stroke="#f2a541" strokeWidth="1.4" transform="rotate(45 10 10)" />
      <circle cx="10" cy="10" r="2" fill="#f2a541" />
    </svg>
  )
}

export function ShopLayout() {
  const { user, logout } = useAuth()
  const { count } = useCart()
  const navigate = useNavigate()
  const isCustomer = user?.role === 'customer'

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <AppBar position="static" sx={{ bgcolor: 'background.paper', color: 'text.primary' }}>
        <Toolbar sx={{ gap: 3 }}>
          <Box
            component={RouterLink}
            to="/"
            sx={{ display: 'flex', alignItems: 'center', gap: 1, textDecoration: 'none', color: 'inherit' }}
          >
            <BrandMark />
            <Typography variant="h6" sx={{ fontSize: '0.95rem', letterSpacing: '0.1em' }}>
              Contoso Shop
            </Typography>
          </Box>

          <Box sx={{ flexGrow: 1 }} />

          {isCustomer && (
            <Button component={RouterLink} to="/orders" color="inherit" size="small">
              My Orders
            </Button>
          )}

          <Button
            component={RouterLink}
            to="/cart"
            color="inherit"
            size="small"
            startIcon={
              <Badge badgeContent={count} color="warning">
                <ShoppingCartOutlined fontSize="small" />
              </Badge>
            }
          >
            Cart
          </Button>

          {isCustomer ? (
            <Button
              size="small"
              onClick={() => {
                logout()
                navigate('/')
              }}
            >
              Sign out ({user.full_name.split(' ')[0]})
            </Button>
          ) : (
            <Button component={RouterLink} to="/login" variant="outlined" size="small">
              Sign in
            </Button>
          )}

          <Button component={RouterLink} to="/admin" size="small" sx={{ color: 'text.secondary' }}>
            Staff login
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4, flexGrow: 1 }}>
        <Outlet />
      </Container>
    </Box>
  )
}
