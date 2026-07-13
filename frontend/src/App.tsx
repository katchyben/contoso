import { useMemo, useState } from 'react'
import {
  Box,
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
import { theme } from './theme'
import { resources } from './config/resources'
import { ResourceCrudPage } from './components/ResourceCrudPage'

const DRAWER_WIDTH = 240

function BrandMark() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <rect x="1" y="1" width="18" height="18" stroke="#f2a541" strokeWidth="1.4" transform="rotate(45 10 10)" />
      <circle cx="10" cy="10" r="2" fill="#f2a541" />
    </svg>
  )
}

function App() {
  const [activeKey, setActiveKey] = useState(resources[0].key)
  const activeResource = useMemo(
    () => resources.find((r) => r.key === activeKey) ?? resources[0],
    [activeKey],
  )

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
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
          <Box sx={{ mt: 'auto', px: 2.5, py: 2 }}>
            <Typography
              variant="caption"
              sx={{ fontFamily: '"IBM Plex Mono", monospace', color: 'text.secondary', opacity: 0.6 }}
            >
              v1.0 · postgres
            </Typography>
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
    </ThemeProvider>
  )
}

export default App
