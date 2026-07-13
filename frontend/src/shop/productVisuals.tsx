import type { ComponentType } from 'react'
import LaptopMacOutlined from '@mui/icons-material/LaptopMacOutlined'
import LaptopWindowsOutlined from '@mui/icons-material/LaptopWindowsOutlined'
import SmartphoneOutlined from '@mui/icons-material/SmartphoneOutlined'
import PhoneIphoneOutlined from '@mui/icons-material/PhoneIphoneOutlined'
import MouseOutlined from '@mui/icons-material/MouseOutlined'
import UsbOutlined from '@mui/icons-material/UsbOutlined'
import SoupKitchenOutlined from '@mui/icons-material/SoupKitchenOutlined'
import KitchenOutlined from '@mui/icons-material/KitchenOutlined'
import BakeryDiningOutlined from '@mui/icons-material/BakeryDiningOutlined'
import CakeOutlined from '@mui/icons-material/CakeOutlined'
import Inventory2Outlined from '@mui/icons-material/Inventory2Outlined'

type IconType = ComponentType<{ sx?: object }>

export interface ProductVisual {
  icon: IconType
  bg: string
  fg: string
}

interface Tint {
  bg: string
  fg: string
}

const amber: Tint = { bg: 'rgba(242,165,65,0.12)', fg: '#f2a541' }
const teal: Tint = { bg: 'rgba(77,214,208,0.12)', fg: '#4dd6d0' }
const blue: Tint = { bg: 'rgba(93,140,239,0.12)', fg: '#82a6f2' }
const red: Tint = { bg: 'rgba(224,96,90,0.12)', fg: '#ea8781' }
const green: Tint = { bg: 'rgba(76,175,125,0.14)', fg: '#5fce97' }
const slate: Tint = { bg: 'rgba(233,230,223,0.07)', fg: '#a8afba' }

// Exact SKU -> icon for the specific catalog we ship; falls back to a
// category-prefix guess for anything else, then a generic box icon.
const SKU_ICONS: Record<string, IconType> = {
  'LAP-ULT-14': LaptopMacOutlined,
  'LAP-PRO-16': LaptopWindowsOutlined,
  'PHN-NOVA': SmartphoneOutlined,
  'PHN-IRIS-12': PhoneIphoneOutlined,
  'ACC-MOU-01': MouseOutlined,
  'ACC-HUB-01': UsbOutlined,
  'CKW-FRY-10': SoupKitchenOutlined,
  'CKW-POT-SET': KitchenOutlined,
  'BAK-MAT-01': BakeryDiningOutlined,
  'BAK-TIN-12': CakeOutlined,
}

const PREFIX_RULES: Record<string, { icon: IconType; tint: Tint }> = {
  LAP: { icon: LaptopMacOutlined, tint: amber },
  PHN: { icon: SmartphoneOutlined, tint: teal },
  ACC: { icon: UsbOutlined, tint: blue },
  CKW: { icon: KitchenOutlined, tint: red },
  BAK: { icon: BakeryDiningOutlined, tint: green },
}

export function getProductVisual(sku: string): ProductVisual {
  const prefix = sku.split('-')[0]
  const rule = PREFIX_RULES[prefix]
  return {
    icon: SKU_ICONS[sku] ?? rule?.icon ?? Inventory2Outlined,
    ...(rule?.tint ?? slate),
  }
}
