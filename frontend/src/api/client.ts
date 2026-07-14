import { clearToken, getToken } from '../auth/authStore'

export const API_BASE: string = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = getToken()
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...options,
  })

  if (res.status === 401) {
    clearToken()
  }

  if (!res.ok) {
    const body = await res.json().catch(() => null)
    const detail = typeof body?.detail === 'string' ? body.detail : `Request failed (${res.status})`
    throw new Error(detail)
  }

  if (res.status === 204) {
    return undefined as T
  }
  return (await res.json()) as T
}

export const api = {
  list: <T>(path: string): Promise<T[]> => request<T[]>(path),
  create: <T>(path: string, data: Record<string, unknown>): Promise<T> =>
    request<T>(path, { method: 'POST', body: JSON.stringify(data) }),
  update: <T>(path: string, id: number, data: Record<string, unknown>): Promise<T> =>
    request<T>(`${path}/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  remove: (path: string, id: number): Promise<void> =>
    request<void>(`${path}/${id}`, { method: 'DELETE' }),
}

export interface CurrentUser {
  id: number
  email: string
  full_name: string
  role: 'admin' | 'staff' | 'customer'
  is_active: boolean
}

export async function login(email: string, password: string): Promise<string> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(typeof body?.detail === 'string' ? body.detail : 'Login failed')
  }
  const data = await res.json()
  return data.access_token as string
}

export function fetchMe(): Promise<CurrentUser> {
  return request<CurrentUser>('/auth/me')
}

export interface Product {
  id: number
  sku: string
  name: string
  description: string | null
  unit_price: string
  stock_quantity: number
  is_active: boolean
  image_url: string | null
  category_id: number | null
}

export interface Category {
  id: number
  name: string
  parent_id: number | null
}

export interface OrderSummary {
  id: number
  order_number: string
  customer_id: number
  status: string
  shipping_address_id: number
  billing_address_id: number
  subtotal: string
  tax_amount: string
  shipping_amount: string
  total_amount: string
  currency: string
  placed_at: string
  updated_at: string
}

export interface OrderItemDetail {
  id: number
  order_id: number
  product_id: number
  quantity: number
  unit_price: string
  total_price: string
}

export interface OrderDetail extends OrderSummary {
  items: OrderItemDetail[]
}

export interface CheckoutAddressInput {
  line1: string
  line2?: string
  city: string
  state?: string
  postal_code: string
  country: string
}

export interface CheckoutPayload {
  shipping_address: CheckoutAddressInput
  billing_address?: CheckoutAddressInput
  items: { product_id: number; quantity: number }[]
}

export interface RegisterPayload {
  email: string
  password: string
  first_name: string
  last_name: string
  phone?: string
}

export async function registerCustomer(payload: RegisterPayload): Promise<string> {
  const data = await request<{ access_token: string }>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  return data.access_token
}

export function checkout(payload: CheckoutPayload): Promise<OrderDetail> {
  return request<OrderDetail>('/checkout', { method: 'POST', body: JSON.stringify(payload) })
}

export function fetchMyOrders(): Promise<OrderSummary[]> {
  return request<OrderSummary[]>('/me/orders')
}

export function fetchMyOrderDetail(id: number): Promise<OrderDetail> {
  return request<OrderDetail>(`/me/orders/${id}`)
}
