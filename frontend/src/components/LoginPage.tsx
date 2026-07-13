import { useState, type FormEvent } from 'react'
import { Alert, Box, Button, Paper, TextField, Typography } from '@mui/material'
import { useAuth } from '../auth/AuthContext'

function BrandMark() {
  return (
    <svg width="28" height="28" viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <rect x="1" y="1" width="18" height="18" stroke="#f2a541" strokeWidth="1.4" transform="rotate(45 10 10)" />
      <circle cx="10" cy="10" r="2" fill="#f2a541" />
    </svg>
  )
}

export function LoginPage() {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await login(email, password)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
      }}
    >
      <Paper
        component="form"
        onSubmit={handleSubmit}
        variant="outlined"
        sx={{ width: 360, p: 4 }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25, mb: 3 }}>
          <BrandMark />
          <Box>
            <Typography variant="h6" sx={{ fontSize: '1rem', lineHeight: 1.1, letterSpacing: '0.1em' }}>
              Contoso
            </Typography>
            <Typography
              variant="caption"
              sx={{ fontFamily: '"IBM Plex Mono", monospace', color: 'text.secondary', letterSpacing: '0.08em' }}
            >
              ORDER OPS
            </Typography>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <TextField
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          fullWidth
          autoFocus
          sx={{ mb: 2 }}
        />
        <TextField
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          fullWidth
          sx={{ mb: 3 }}
        />
        <Button type="submit" variant="contained" fullWidth disabled={submitting}>
          {submitting ? 'Signing in…' : 'Sign in'}
        </Button>
      </Paper>
    </Box>
  )
}
