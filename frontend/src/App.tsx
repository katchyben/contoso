import { useMemo, useState } from 'react'
import { BrowserRouter, Link as RouterLink, Navigate, Route, Routes } from 'react-router-dom'
import {
  Alert,
  Box,
  CircularProgress,
  CssBaseline,
  Divider,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ThemeProvider,
  Typography,
} from '@mui/material'
import LogoutOutlined from '@mui/icons-material/LogoutOutlined'
import { theme } from './theme'
import { resources } from './config/resources'
import { ResourceCrudPage } from './components/ResourceCrudPage'
import { LoginPage } from './components/LoginPage'
import { AuthProvider, useAuth } from './auth/AuthContext'
import { CartProvider } from './shop/CartContext'
import { ShopLayout } from './shop/ShopLayout'
import { ProductGrid } from './shop/ProductGrid'
import { CartPage } from './shop/CartPage'
import { CheckoutPage } from './shop/CheckoutPage'
import { OrdersPage } from './shop/OrdersPage'
import { OrderDetailPage } from './shop/OrderDetailPage'
import { RequireCustomer } from './shop/RequireCustomer'
import { AuthPanel } from './shop/AuthPanel'

const DRAWER_WIDTH = 240

function BrandMark() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <rect x="1" y="1" width="18" height="18" stroke="#f2a541" strokeWidth="1.4" transform="rotate(45 10 10)" />
      <circle cx="10" cy="10" r="2" fill="#f2a541" />
    </svg>
  )
}

function AppShell() {
  const { user, logout } = useAuth()
  const [activeKey, setActiveKey] = useState(resources[0].key)
  const activeResource = useMemo(
    () => resources.find((r) => r.key === activeKey) ?? resources[0],
    [activeKey],
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': { width: DRAWER_WIDTH, boxSizing: 'border-box' },
        }}
      >
        <Box sx={{ px: 2.5, py: 3, display: 'flex', alignItems: 'center', gap: 1.25 }}>
          <BrandMark />
          <Box>
            <Typography variant="h6" sx={{ fontSize: '0.95rem', lineHeight: 1.1, letterSpacing: '0.1em' }}>
              Contoso
            </Typography>
            <Typography
              variant="caption"
              sx={{
                fontFamily: '"IBM Plex Mono", monospace',
                color: 'text.secondary',
                letterSpacing: '0.08em',
              }}
            >
              ORDER OPS
            </Typography>
          </Box>
        </Box>
        <Divider />
        <List sx={{ py: 1 }}>
          {resources.map((resource) => {
            const Icon = resource.icon
            const selected = resource.key === activeKey
            return (
              <ListItemButton
                key={resource.key}
                selected={selected}
                onClick={() => setActiveKey(resource.key)}
                sx={{
                  mx: 1,
                  mb: 0.25,
                  borderRadius: 1,
                  borderLeft: '2px solid transparent',
                  '&.Mui-selected': {
                    borderLeft: '2px solid #f2a541',
                    backgroundColor: 'rgba(242,165,65,0.09)',
                  },
                  '&.Mui-selected:hover': {
                    backgroundColor: 'rgba(242,165,65,0.13)',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 36, color: selected ? '#f2a541' : 'text.secondary' }}>
                  <Icon />
                </ListItemIcon>
                <ListItemText
                  primary={resource.label}
                  slotProps={{
                    primary: {
                      sx: {
                        fontSize: '0.85rem',
                        fontWeight: selected ? 600 : 400,
                        color: selected ? 'text.primary' : 'text.secondary',
                      },
                    },
                  }}
                />
              </ListItemButton>
            )
          })}
        </List>
        <Box sx={{ mt: 'auto' }}>
          <Divider />
          <Box sx={{ px: 2.5, py: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ minWidth: 0, flexGrow: 1 }}>
              <Typography noWrap sx={{ fontSize: '0.8rem', fontWeight: 600 }}>
                {user?.full_name}
              </Typography>
              <Typography
                noWrap
                variant="caption"
                sx={{ fontFamily: '"IBM Plex Mono", monospace', color: 'text.secondary' }}
              >
                {user?.role}
              </Typography>
            </Box>
            <ListItemIcon
              sx={{ minWidth: 'auto', color: 'text.secondary', cursor: 'pointer' }}
              onClick={logout}
              aria-label="logout"
            >
              <LogoutOutlined fontSize="small" />
            </ListItemIcon>
          </Box>
          <Box sx={{ px: 2.5, pb: 1 }}>
            <Typography
              component={RouterLink}
              to="/"
              variant="caption"
              sx={{
                fontFamily: '"IBM Plex Mono", monospace',
                color: 'text.secondary',
                textDecoration: 'none',
                '&:hover': { color: '#f2a541' },
              }}
            >
              ← View shop
            </Typography>
          </Box>
          <Box sx={{ px: 2.5, pb: 2 }}>
            <Typography
              variant="caption"
              sx={{ fontFamily: '"IBM Plex Mono", monospace', color: 'text.secondary', opacity: 0.6 }}
            >
              v1.0 · postgres
            </Typography>
          </Box>
        </Box>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ p: 4, flexGrow: 1 }}>
          <Box key={activeResource.key}>
            <ResourceCrudPage resource={activeResource} />
          </Box>
        </Box>
      </Box>
    </Box>
  )
}

function AdminGate() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress size={28} sx={{ color: '#f2a541' }} />
      </Box>
    )
  }

  if (!user) {
    return <LoginPage />
  }

  if (user.role === 'customer') {
    return (
      <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 4 }}>
        <Alert severity="warning">Customer accounts don't have access to the back office.</Alert>
      </Box>
    )
  }

  return <AppShell />
}

function ShopLoginRoute() {
  const { user } = useAuth()
  if (user) {
    return <Navigate to="/" replace />
  }
  return <AuthPanel title="Sign in" />
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <CartProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/admin/*" element={<AdminGate />} />
              <Route path="/" element={<ShopLayout />}>
                <Route index element={<ProductGrid />} />
                <Route path="cart" element={<CartPage />} />
                <Route path="checkout" element={<CheckoutPage />} />
                <Route path="login" element={<ShopLoginRoute />} />
                <Route
                  path="orders"
                  element={
                    <RequireCustomer>
                      <OrdersPage />
                    </RequireCustomer>
                  }
                />
                <Route
                  path="orders/:id"
                  element={
                    <RequireCustomer>
                      <OrderDetailPage />
                    </RequireCustomer>
                  }
                />
              </Route>
            </Routes>
          </BrowserRouter>
        </CartProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
