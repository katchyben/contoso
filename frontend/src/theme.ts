import { createTheme } from '@mui/material'

// "Manifest" theme: a dark ops-console look for a logistics / order-management
// back office, styled after shipping manifests and cargo tags rather than a
// generic admin dashboard.

const ink = '#0f1216'
const panel = '#171b21'
const panelRaised = '#1d222a'
const hairline = 'rgba(233, 230, 223, 0.09)'
const textPrimary = '#e9e6df'
const textSecondary = '#8790a0'
const amber = '#f2a541'
const teal = '#4dd6d0'

export const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: ink,
      paper: panel,
    },
    divider: hairline,
    text: {
      primary: textPrimary,
      secondary: textSecondary,
    },
    primary: {
      main: amber,
      contrastText: ink,
    },
    secondary: {
      main: teal,
      contrastText: ink,
    },
    error: {
      main: '#e0605a',
    },
    success: {
      main: '#4caf7d',
    },
  },
  shape: {
    borderRadius: 3,
  },
  typography: {
    fontFamily: '"IBM Plex Sans", "Helvetica Neue", sans-serif',
    h1: { fontFamily: '"Oswald", sans-serif' },
    h2: { fontFamily: '"Oswald", sans-serif' },
    h3: { fontFamily: '"Oswald", sans-serif' },
    h4: { fontFamily: '"Oswald", sans-serif' },
    h5: {
      fontFamily: '"Oswald", sans-serif',
      fontWeight: 600,
      textTransform: 'uppercase',
      letterSpacing: '0.06em',
      fontSize: '1.15rem',
    },
    h6: {
      fontFamily: '"Oswald", sans-serif',
      fontWeight: 600,
      textTransform: 'uppercase',
      letterSpacing: '0.08em',
    },
    button: {
      fontFamily: '"IBM Plex Sans", sans-serif',
      fontWeight: 600,
      letterSpacing: '0.05em',
      textTransform: 'uppercase',
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundImage: `
            linear-gradient(rgba(233,230,223,0.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(233,230,223,0.025) 1px, transparent 1px)
          `,
          backgroundSize: '28px 28px',
        },
        '::selection': {
          background: 'rgba(242,165,65,0.35)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
        outlined: {
          borderColor: hairline,
        },
      },
    },
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: {
          borderRadius: 2,
        },
        outlined: {
          borderWidth: '1.5px',
          '&:hover': { borderWidth: '1.5px' },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 2,
          fontFamily: '"IBM Plex Mono", monospace',
          fontSize: '0.7rem',
          fontWeight: 600,
          letterSpacing: '0.04em',
          textTransform: 'uppercase',
          height: 22,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          fontFamily: '"IBM Plex Sans", sans-serif',
          fontSize: '0.7rem',
          fontWeight: 600,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          color: textSecondary,
          borderBottomColor: hairline,
          backgroundColor: panelRaised,
        },
        body: {
          borderBottomColor: hairline,
          fontSize: '0.85rem',
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          '&:hover': {
            backgroundColor: 'rgba(242,165,65,0.045)',
          },
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: panel,
          backgroundImage: 'none',
          borderRight: `1px solid ${hairline}`,
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          backgroundColor: panelRaised,
          backgroundImage: 'none',
          border: `1px solid ${hairline}`,
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 2,
        },
      },
    },
  },
})
