import { useEffect, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  CardMedia,
  Chip,
  CircularProgress,
  Stack,
  Typography,
} from '@mui/material'
import AddShoppingCartOutlined from '@mui/icons-material/AddShoppingCartOutlined'
import { api, type Product } from '../api/client'
import { useCart } from './CartContext'
import { getProductVisual } from './productVisuals'

function ProductThumbnail({ product }: { product: Product }) {
  if (product.image_url) {
    return (
      <CardMedia
        component="img"
        src={product.image_url}
        alt={product.name}
        sx={{ height: 160, objectFit: 'cover' }}
      />
    )
  }
  const { icon: Icon, bg, fg } = getProductVisual(product.sku)
  return (
    <Box
      sx={{
        height: 160,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: bg,
        color: fg,
      }}
    >
      <Icon sx={{ fontSize: 56 }} />
    </Box>
  )
}

export function ProductGrid() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [justAdded, setJustAdded] = useState<number | null>(null)
  const { addItem } = useCart()

  useEffect(() => {
    api
      .list<Product>('/products')
      .then((data) => setProducts(data.filter((p) => p.is_active)))
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load products'))
      .finally(() => setLoading(false))
  }, [])

  const handleAdd = (product: Product) => {
    addItem(product)
    setJustAdded(product.id)
    setTimeout(() => setJustAdded((id) => (id === product.id ? null : id)), 1200)
  }

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
        Catalog
      </Typography>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
          gap: 2.5,
        }}
      >
        {products.map((product) => (
          <Card key={product.id} variant="outlined" sx={{ display: 'flex', flexDirection: 'column' }}>
            <ProductThumbnail product={product} />
            <CardContent sx={{ flexGrow: 1 }}>
              <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {product.name}
                </Typography>
                <Chip
                  size="small"
                  label={product.stock_quantity > 0 ? `${product.stock_quantity} in stock` : 'out of stock'}
                  sx={{
                    bgcolor: product.stock_quantity > 0 ? 'rgba(76,175,125,0.14)' : 'rgba(224,96,90,0.14)',
                    color: product.stock_quantity > 0 ? '#5fce97' : '#ea8781',
                  }}
                />
              </Stack>
              <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1.5 }}>
                {product.description}
              </Typography>
              <Typography
                sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '1.1rem', color: '#f2a541' }}
              >
                ${Number(product.unit_price).toFixed(2)}
              </Typography>
            </CardContent>
            <CardActions sx={{ px: 2, pb: 2 }}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<AddShoppingCartOutlined />}
                disabled={product.stock_quantity <= 0}
                onClick={() => handleAdd(product)}
              >
                {justAdded === product.id ? 'Added' : 'Add to cart'}
              </Button>
            </CardActions>
          </Card>
        ))}
      </Box>
    </Box>
  )
}
