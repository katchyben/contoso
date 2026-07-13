import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import type { Product } from '../api/client'

const CART_KEY = 'contoso_cart'

export interface CartLine {
  product: Product
  quantity: number
}

interface CartContextValue {
  lines: CartLine[]
  count: number
  subtotal: number
  addItem: (product: Product, quantity?: number) => void
  updateQuantity: (productId: number, quantity: number) => void
  removeItem: (productId: number) => void
  clear: () => void
}

const CartContext = createContext<CartContextValue | null>(null)

function loadCart(): CartLine[] {
  try {
    const raw = localStorage.getItem(CART_KEY)
    return raw ? (JSON.parse(raw) as CartLine[]) : []
  } catch {
    return []
  }
}

export function CartProvider({ children }: { children: ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>(loadCart)

  useEffect(() => {
    localStorage.setItem(CART_KEY, JSON.stringify(lines))
  }, [lines])

  const addItem = (product: Product, quantity = 1) => {
    setLines((prev) => {
      const existing = prev.find((l) => l.product.id === product.id)
      if (existing) {
        return prev.map((l) =>
          l.product.id === product.id ? { ...l, quantity: l.quantity + quantity } : l,
        )
      }
      return [...prev, { product, quantity }]
    })
  }

  const updateQuantity = (productId: number, quantity: number) => {
    setLines((prev) =>
      quantity <= 0
        ? prev.filter((l) => l.product.id !== productId)
        : prev.map((l) => (l.product.id === productId ? { ...l, quantity } : l)),
    )
  }

  const removeItem = (productId: number) => {
    setLines((prev) => prev.filter((l) => l.product.id !== productId))
  }

  const clear = () => setLines([])

  const count = lines.reduce((sum, l) => sum + l.quantity, 0)
  const subtotal = lines.reduce((sum, l) => sum + Number(l.product.unit_price) * l.quantity, 0)

  return (
    <CartContext.Provider value={{ lines, count, subtotal, addItem, updateQuantity, removeItem, clear }}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart(): CartContextValue {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart must be used within CartProvider')
  return ctx
}
