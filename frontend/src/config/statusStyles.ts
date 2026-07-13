export interface StatusStyle {
  bg: string
  fg: string
  border: string
}

const amber: StatusStyle = { bg: 'rgba(242,165,65,0.12)', fg: '#f2a541', border: 'rgba(242,165,65,0.45)' }
const blue: StatusStyle = { bg: 'rgba(93,140,239,0.12)', fg: '#82a6f2', border: 'rgba(93,140,239,0.45)' }
const green: StatusStyle = { bg: 'rgba(76,175,125,0.14)', fg: '#5fce97', border: 'rgba(76,175,125,0.45)' }
const teal: StatusStyle = { bg: 'rgba(77,214,208,0.12)', fg: '#4dd6d0', border: 'rgba(77,214,208,0.45)' }
const red: StatusStyle = { bg: 'rgba(224,96,90,0.14)', fg: '#ea8781', border: 'rgba(224,96,90,0.45)' }
const slate: StatusStyle = { bg: 'rgba(233,230,223,0.07)', fg: '#a8afba', border: 'rgba(233,230,223,0.22)' }

export const STATUS_STYLES: Record<string, StatusStyle> = {
  pending: amber,
  confirmed: blue,
  authorized: blue,
  paid: green,
  captured: green,
  delivered: green,
  fulfilling: teal,
  in_transit: teal,
  shipped: teal,
  cancelled: red,
  failed: red,
  returned: red,
  refunded: slate,
}

export const DEFAULT_STATUS_STYLE: StatusStyle = slate

export function styleForStatus(value: string): StatusStyle {
  return STATUS_STYLES[value] ?? DEFAULT_STATUS_STYLE
}
