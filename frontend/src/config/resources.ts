import type { ComponentType } from 'react'
import PeopleAltOutlined from '@mui/icons-material/PeopleAltOutlined'
import MapOutlined from '@mui/icons-material/MapOutlined'
import CategoryOutlined from '@mui/icons-material/CategoryOutlined'
import Inventory2Outlined from '@mui/icons-material/Inventory2Outlined'
import ReceiptLongOutlined from '@mui/icons-material/ReceiptLongOutlined'
import ListAltOutlined from '@mui/icons-material/ListAltOutlined'
import PaymentsOutlined from '@mui/icons-material/PaymentsOutlined'
import LocalShippingOutlined from '@mui/icons-material/LocalShippingOutlined'

export type FieldType = 'string' | 'number' | 'decimal' | 'boolean' | 'enum' | 'datetime'

export interface FieldConfig {
  key: string
  label: string
  type: FieldType
  required?: boolean
  options?: string[]
  default?: unknown
  // Whether the field appears on the create / edit form. Mirrors the backend's
  // Create/Update pydantic schemas in backend/schemas.py exactly, since PATCH
  // to a field the Update schema doesn't accept is silently dropped server-side.
  showOnCreate?: boolean
  showOnEdit?: boolean
}

export interface ResourceConfig {
  key: string
  label: string
  path: string
  icon: ComponentType
  fields: FieldConfig[]
}

const readOnly = (key: string, label: string, type: FieldType = 'number'): FieldConfig => ({
  key,
  label,
  type,
  showOnCreate: false,
  showOnEdit: false,
})

export const resources: ResourceConfig[] = [
  {
    key: 'customers',
    label: 'Customers',
    path: '/customers',
    icon: PeopleAltOutlined,
    fields: [
      readOnly('id', 'ID'),
      { key: 'email', label: 'Email', type: 'string', required: true },
      { key: 'first_name', label: 'First name', type: 'string', required: true },
      { key: 'last_name', label: 'Last name', type: 'string', required: true },
      { key: 'phone', label: 'Phone', type: 'string' },
      readOnly('created_at', 'Created at', 'datetime'),
    ],
  },
  {
    key: 'addresses',
    label: 'Addresses',
    path: '/addresses',
    icon: MapOutlined,
    fields: [
      readOnly('id', 'ID'),
      { key: 'customer_id', label: 'Customer ID', type: 'number', required: true, showOnEdit: false },
      {
        key: 'type',
        label: 'Type',
        type: 'enum',
        required: true,
        options: ['shipping', 'billing'],
        default: 'shipping',
      },
      { key: 'line1', label: 'Line 1', type: 'string', required: true },
      { key: 'line2', label: 'Line 2', type: 'string' },
      { key: 'city', label: 'City', type: 'string', required: true },
      { key: 'state', label: 'State', type: 'string' },
      { key: 'postal_code', label: 'Postal code', type: 'string', required: true },
      { key: 'country', label: 'Country (ISO-2)', type: 'string', required: true },
      { key: 'is_default', label: 'Default address', type: 'boolean', default: false },
    ],
  },
  {
    key: 'categories',
    label: 'Categories',
    path: '/categories',
    icon: CategoryOutlined,
    fields: [
      readOnly('id', 'ID'),
      { key: 'name', label: 'Name', type: 'string', required: true },
      { key: 'parent_id', label: 'Parent category ID', type: 'number' },
    ],
  },
  {
    key: 'products',
    label: 'Products',
    path: '/products',
    icon: Inventory2Outlined,
    fields: [
      readOnly('id', 'ID'),
      { key: 'sku', label: 'SKU', type: 'string', required: true },
      { key: 'name', label: 'Name', type: 'string', required: true },
      { key: 'description', label: 'Description', type: 'string' },
      { key: 'unit_price', label: 'Unit price', type: 'decimal', required: true },
      { key: 'stock_quantity', label: 'Stock quantity', type: 'number', default: 0 },
      { key: 'is_active', label: 'Active', type: 'boolean', default: true },
      { key: 'image_url', label: 'Image URL', type: 'string' },
      { key: 'category_id', label: 'Category ID', type: 'number' },
    ],
  },
  {
    key: 'orders',
    label: 'Orders',
    path: '/orders',
    icon: ReceiptLongOutlined,
    fields: [
      readOnly('id', 'ID'),
      { key: 'order_number', label: 'Order number', type: 'string', required: true },
      { key: 'customer_id', label: 'Customer ID', type: 'number', required: true, showOnEdit: false },
      {
        key: 'status',
        label: 'Status',
        type: 'enum',
        showOnCreate: false,
        options: [
          'pending',
          'confirmed',
          'paid',
          'fulfilling',
          'shipped',
          'delivered',
          'cancelled',
          'refunded',
        ],
      },
      { key: 'shipping_address_id', label: 'Shipping address ID', type: 'number', required: true },
      { key: 'billing_address_id', label: 'Billing address ID', type: 'number', required: true },
      { key: 'subtotal', label: 'Subtotal', type: 'decimal', required: true },
      { key: 'tax_amount', label: 'Tax amount', type: 'decimal', default: '0' },
      { key: 'shipping_amount', label: 'Shipping amount', type: 'decimal', default: '0' },
      { key: 'total_amount', label: 'Total amount', type: 'decimal', required: true },
      { key: 'currency', label: 'Currency', type: 'string', default: 'USD' },
      readOnly('placed_at', 'Placed at', 'datetime'),
      readOnly('updated_at', 'Updated at', 'datetime'),
    ],
  },
  {
    key: 'order-items',
    label: 'Order Items',
    path: '/order-items',
    icon: ListAltOutlined,
    fields: [
      readOnly('id', 'ID'),
      { key: 'order_id', label: 'Order ID', type: 'number', required: true, showOnEdit: false },
      { key: 'product_id', label: 'Product ID', type: 'number', required: true, showOnEdit: false },
      { key: 'quantity', label: 'Quantity', type: 'number', required: true },
      { key: 'unit_price', label: 'Unit price', type: 'decimal', required: true },
      { key: 'total_price', label: 'Total price', type: 'decimal', required: true },
    ],
  },
  {
    key: 'payments',
    label: 'Payments',
    path: '/payments',
    icon: PaymentsOutlined,
    fields: [
      readOnly('id', 'ID'),
      { key: 'order_id', label: 'Order ID', type: 'number', required: true, showOnEdit: false },
      { key: 'amount', label: 'Amount', type: 'decimal', required: true },
      { key: 'currency', label: 'Currency', type: 'string', default: 'USD' },
      {
        key: 'status',
        label: 'Status',
        type: 'enum',
        options: ['pending', 'authorized', 'captured', 'failed', 'refunded'],
        default: 'pending',
      },
      { key: 'provider', label: 'Provider', type: 'string', required: true },
      { key: 'provider_reference', label: 'Provider reference', type: 'string' },
      readOnly('created_at', 'Created at', 'datetime'),
    ],
  },
  {
    key: 'shipments',
    label: 'Shipments',
    path: '/shipments',
    icon: LocalShippingOutlined,
    fields: [
      readOnly('id', 'ID'),
      { key: 'order_id', label: 'Order ID', type: 'number', required: true, showOnEdit: false },
      { key: 'carrier', label: 'Carrier', type: 'string', required: true },
      { key: 'tracking_number', label: 'Tracking number', type: 'string' },
      {
        key: 'status',
        label: 'Status',
        type: 'enum',
        options: ['pending', 'in_transit', 'delivered', 'returned'],
        default: 'pending',
      },
      { key: 'shipped_at', label: 'Shipped at', type: 'datetime' },
      { key: 'delivered_at', label: 'Delivered at', type: 'datetime' },
    ],
  },
]
