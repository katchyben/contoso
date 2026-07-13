import { useState, type FormEvent } from 'react'
import { Alert, Button, Paper, Stack, Tab, Tabs, TextField, Typography } from '@mui/material'
import { useAuth } from '../auth/AuthContext'

export function AuthPanel({ title = 'Sign in' }: { title?: string }) {
  const { login, register } = useAuth()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [phone, setPhone] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      if (mode === 'login') {
        await login(email, password)
      } else {
        await register({ email, password, first_name: firstName, last_name: lastName, phone: phone || undefined })
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Paper component="form" onSubmit={handleSubmit} variant="outlined" sx={{ p: 4, maxWidth: 420 }}>
      <Typography variant="h5" sx={{ mb: 2 }}>
        {title}
      </Typography>
      <Tabs value={mode} onChange={(_, v) => setMode(v)} sx={{ mb: 2 }}>
        <Tab value="login" label="Sign in" />
        <Tab value="register" label="Create account" />
      </Tabs>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Stack spacing={2}>
        {mode === 'register' && (
          <Stack direction="row" spacing={2}>
            <TextField label="First name" value={firstName} onChange={(e) => setFirstName(e.target.value)} required fullWidth />
            <TextField label="Last name" value={lastName} onChange={(e) => setLastName(e.target.value)} required fullWidth />
          </Stack>
        )}
        <TextField label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required fullWidth />
        <TextField
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          fullWidth
        />
        {mode === 'register' && (
          <TextField label="Phone (optional)" value={phone} onChange={(e) => setPhone(e.target.value)} fullWidth />
        )}
        <Button type="submit" variant="contained" disabled={submitting}>
          {submitting ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account & continue'}
        </Button>
      </Stack>
    </Paper>
  )
}
