import { useCallback, useEffect, useState, type ReactNode } from 'react'
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  IconButton,
  InputAdornment,
  MenuItem,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import UploadIcon from '@mui/icons-material/UploadOutlined'
import { api, uploadImage } from '../api/client'
import type { FieldConfig, ResourceConfig } from '../config/resources'
import { styleForStatus } from '../config/statusStyles'
import { useAuth } from '../auth/AuthContext'

type Row = Record<string, unknown>
type DialogMode = 'create' | 'edit'

const MONO_KEY_PATTERN = /^id$|_id$|number|sku|tracking|reference/i

function singular(label: string): string {
  return label.replace(/s$/, '')
}

function isMonoField(field: FieldConfig): boolean {
  return field.type === 'number' || field.type === 'decimal' || MONO_KEY_PATTERN.test(field.key)
}

function defaultValueFor(field: FieldConfig): unknown {
  if (field.default !== undefined) return field.default
  if (field.type === 'boolean') return false
  return ''
}

function fieldsFor(fields: FieldConfig[], mode: DialogMode): FieldConfig[] {
  return fields.filter((f) => (mode === 'create' ? f.showOnCreate !== false : f.showOnEdit !== false))
}

function buildInitialFormState(fields: FieldConfig[], mode: DialogMode, row?: Row): Record<string, unknown> {
  const state: Record<string, unknown> = {}
  for (const field of fieldsFor(fields, mode)) {
    state[field.key] = mode === 'edit' && row ? (row[field.key] ?? defaultValueFor(field)) : defaultValueFor(field)
  }
  return state
}

function toDatetimeLocal(value: unknown): string {
  if (!value || typeof value !== 'string') return ''
  return value.slice(0, 16)
}

function formatCell(field: FieldConfig, value: unknown, referenceOptions?: Row[]): ReactNode {
  if (value === null || value === undefined || value === '') {
    return <span style={{ opacity: 0.35 }}>—</span>
  }
  if (field.type === 'reference' && field.reference) {
    const match = referenceOptions?.find((option) => option.id === value)
    const label = match ? String(match[field.reference.labelKey]) : String(value)
    return <span>{label}</span>
  }
  if (field.image) {
    return (
      <Box
        component="img"
        src={String(value)}
        alt=""
        sx={{ width: 40, height: 40, objectFit: 'cover', borderRadius: 1, display: 'block' }}
      />
    )
  }
  if (field.type === 'boolean') {
    const style = value ? styleForStatus('paid') : styleForStatus('refunded')
    return (
      <Chip
        size="small"
        label={value ? 'Yes' : 'No'}
        sx={{ bgcolor: style.bg, color: style.fg, border: '1px solid', borderColor: style.border }}
      />
    )
  }
  if (field.type === 'enum') {
    const style = styleForStatus(String(value))
    return (
      <Chip
        size="small"
        label={String(value).replace(/_/g, ' ')}
        sx={{ bgcolor: style.bg, color: style.fg, border: '1px solid', borderColor: style.border }}
      />
    )
  }
  if (field.type === 'datetime') {
    const d = new Date(value as string)
    const formatted = Number.isNaN(d.getTime()) ? String(value) : d.toLocaleString()
    return (
      <Typography component="span" sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '0.78rem' }}>
        {formatted}
      </Typography>
    )
  }
  if (field.type === 'decimal') {
    return (
      <Typography component="span" sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '0.82rem' }}>
        ${Number(value).toFixed(2)}
      </Typography>
    )
  }
  if (isMonoField(field)) {
    return (
      <Typography component="span" sx={{ fontFamily: '"IBM Plex Mono", monospace', fontSize: '0.82rem' }}>
        {String(value)}
      </Typography>
    )
  }
  return String(value)
}

function buildPayload(fields: FieldConfig[], mode: DialogMode, formState: Record<string, unknown>) {
  const payload: Record<string, unknown> = {}
  for (const field of fieldsFor(fields, mode)) {
    const raw = formState[field.key]
    if (raw === '' && !field.required) continue
    if (field.type === 'number' || field.type === 'reference') {
      payload[field.key] = raw === '' ? null : Number(raw)
    } else {
      payload[field.key] = raw
    }
  }
  return payload
}

export function ResourceCrudPage({ resource }: { resource: ResourceConfig }) {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const [rows, setRows] = useState<Row[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [referenceData, setReferenceData] = useState<Record<string, Row[]>>({})

  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogMode, setDialogMode] = useState<DialogMode>('create')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formState, setFormState] = useState<Record<string, unknown>>({})
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const [uploadingField, setUploadingField] = useState<string | null>(null)

  const [deleteTarget, setDeleteTarget] = useState<Row | null>(null)
  const [deleting, setDeleting] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setRows(await api.list<Row>(resource.path))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }, [resource.path])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    const referencePaths = [
      ...new Set(resource.fields.filter((f) => f.type === 'reference' && f.reference).map((f) => f.reference!.path)),
    ]
    if (referencePaths.length === 0) {
      setReferenceData({})
      return
    }
    let cancelled = false
    Promise.all(referencePaths.map((path) => api.list<Row>(path))).then((results) => {
      if (cancelled) return
      setReferenceData(Object.fromEntries(referencePaths.map((path, i) => [path, results[i]])))
    })
    return () => {
      cancelled = true
    }
  }, [resource.fields])

  const openCreate = () => {
    setDialogMode('create')
    setEditingId(null)
    setFormState(buildInitialFormState(resource.fields, 'create'))
    setFormError(null)
    setDialogOpen(true)
  }

  const openEdit = (row: Row) => {
    setDialogMode('edit')
    setEditingId(row.id as number)
    setFormState(buildInitialFormState(resource.fields, 'edit', row))
    setFormError(null)
    setDialogOpen(true)
  }

  const closeDialog = () => {
    if (saving) return
    setDialogOpen(false)
  }

  const handleFieldChange = (key: string, value: unknown) => {
    setFormState((prev) => ({ ...prev, [key]: value }))
  }

  const handleImageUpload = async (key: string, file: File) => {
    setUploadingField(key)
    setFormError(null)
    try {
      const url = await uploadImage(file)
      handleFieldChange(key, url)
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploadingField(null)
    }
  }

  const handleSubmit = async () => {
    setSaving(true)
    setFormError(null)
    try {
      const payload = buildPayload(resource.fields, dialogMode, formState)
      if (dialogMode === 'create') {
        await api.create(resource.path, payload)
      } else if (editingId !== null) {
        await api.update(resource.path, editingId, payload)
      }
      setDialogOpen(false)
      await load()
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return
    setDeleting(true)
    try {
      await api.remove(resource.path, deleteTarget.id as number)
      setDeleteTarget(null)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    } finally {
      setDeleting(false)
    }
  }

  const formFields = fieldsFor(resource.fields, dialogMode)

  return (
    <Box>
      <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', mb: 2.5 }}>
        <Stack direction="row" sx={{ alignItems: 'center', gap: 1.5 }}>
          <Typography variant="h5">{resource.label}</Typography>
          <Chip
            label={`${rows.length} record${rows.length === 1 ? '' : 's'}`}
            size="small"
            sx={{
              bgcolor: 'transparent',
              border: '1px solid',
              borderColor: 'divider',
              color: 'text.secondary',
            }}
          />
        </Stack>
        <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate}>
          Add {singular(resource.label)}
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress size={28} sx={{ color: '#f2a541' }} />
        </Box>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow>
                {resource.fields.map((field) => (
                  <TableCell key={field.key}>{field.label}</TableCell>
                ))}
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.length === 0 && (
                <TableRow>
                  <TableCell colSpan={resource.fields.length + 1} align="center" sx={{ color: 'text.secondary', py: 4 }}>
                    No records yet
                  </TableCell>
                </TableRow>
              )}
              {rows.map((row, index) => (
                <TableRow
                  key={String(row.id)}
                  hover
                  sx={{
                    opacity: 0,
                    animation: 'rowRise 0.35s ease forwards',
                    animationDelay: `${Math.min(index, 12) * 30}ms`,
                    '@keyframes rowRise': {
                      from: { opacity: 0, transform: 'translateY(4px)' },
                      to: { opacity: 1, transform: 'translateY(0)' },
                    },
                  }}
                >
                  {resource.fields.map((field) => (
                    <TableCell key={field.key}>
                      {formatCell(field, row[field.key], field.reference && referenceData[field.reference.path])}
                    </TableCell>
                  ))}
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => openEdit(row)} aria-label="edit">
                      <EditIcon fontSize="small" />
                    </IconButton>
                    {isAdmin && (
                      <IconButton size="small" onClick={() => setDeleteTarget(row)} aria-label="delete">
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={dialogOpen} onClose={closeDialog} fullWidth maxWidth="sm">
        <DialogTitle sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
          {dialogMode === 'create' ? `Add ${singular(resource.label)}` : `Edit ${singular(resource.label)}`}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 2.5 }}>
            {formError && <Alert severity="error">{formError}</Alert>}
            {formFields.map((field) => {
              const value = formState[field.key]

              if (field.type === 'boolean') {
                return (
                  <FormControlLabel
                    key={field.key}
                    control={
                      <Checkbox
                        checked={Boolean(value)}
                        onChange={(e) => handleFieldChange(field.key, e.target.checked)}
                      />
                    }
                    label={field.label}
                  />
                )
              }

              if (field.image) {
                const isUploading = uploadingField === field.key
                return (
                  <Stack key={field.key} direction="row" spacing={1.5} sx={{ alignItems: 'center' }}>
                    {value ? (
                      <Box
                        component="img"
                        src={String(value)}
                        alt=""
                        sx={{ width: 56, height: 56, objectFit: 'cover', borderRadius: 1, flexShrink: 0 }}
                      />
                    ) : (
                      <Box
                        sx={{
                          width: 56,
                          height: 56,
                          borderRadius: 1,
                          flexShrink: 0,
                          border: '1px dashed',
                          borderColor: 'divider',
                        }}
                      />
                    )}
                    <TextField
                      label={field.label}
                      value={value ?? ''}
                      required={field.required}
                      onChange={(e) => handleFieldChange(field.key, e.target.value)}
                      fullWidth
                    />
                    <Button
                      component="label"
                      variant="outlined"
                      startIcon={isUploading ? <CircularProgress size={16} /> : <UploadIcon />}
                      disabled={isUploading}
                      sx={{ flexShrink: 0 }}
                    >
                      Upload
                      <input
                        type="file"
                        accept="image/*"
                        hidden
                        onChange={(e) => {
                          const file = e.target.files?.[0]
                          e.target.value = ''
                          if (file) void handleImageUpload(field.key, file)
                        }}
                      />
                    </Button>
                  </Stack>
                )
              }

              if (field.type === 'reference' && field.reference) {
                const options = referenceData[field.reference.path] ?? []
                return (
                  <TextField
                    key={field.key}
                    select
                    label={field.label}
                    value={value ?? ''}
                    required={field.required}
                    onChange={(e) => handleFieldChange(field.key, e.target.value === '' ? '' : Number(e.target.value))}
                    fullWidth
                  >
                    {!field.required && <MenuItem value="">{'—'}</MenuItem>}
                    {options.map((option) => (
                      <MenuItem key={String(option.id)} value={option.id as number}>
                        {String(option[field.reference!.labelKey])}
                      </MenuItem>
                    ))}
                  </TextField>
                )
              }

              if (field.type === 'enum') {
                return (
                  <TextField
                    key={field.key}
                    select
                    label={field.label}
                    value={value ?? ''}
                    required={field.required}
                    onChange={(e) => handleFieldChange(field.key, e.target.value)}
                    fullWidth
                  >
                    {(field.options ?? []).map((option) => (
                      <MenuItem key={option} value={option}>
                        {option.replace(/_/g, ' ')}
                      </MenuItem>
                    ))}
                  </TextField>
                )
              }

              if (field.type === 'datetime') {
                return (
                  <TextField
                    key={field.key}
                    label={field.label}
                    type="datetime-local"
                    value={toDatetimeLocal(value)}
                    required={field.required}
                    onChange={(e) => handleFieldChange(field.key, e.target.value)}
                    slotProps={{ inputLabel: { shrink: true } }}
                    fullWidth
                  />
                )
              }

              return (
                <TextField
                  key={field.key}
                  label={field.label}
                  type={field.type === 'number' || field.type === 'decimal' ? 'number' : 'text'}
                  value={value ?? ''}
                  required={field.required}
                  onChange={(e) => handleFieldChange(field.key, e.target.value)}
                  fullWidth
                  slotProps={{
                    htmlInput: field.type === 'decimal' ? { step: '0.01' } : undefined,
                    input:
                      field.type === 'decimal'
                        ? { startAdornment: <InputAdornment position="start">$</InputAdornment> }
                        : undefined,
                  }}
                />
              )
            })}
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={closeDialog} disabled={saving}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} variant="contained" disabled={saving}>
            {saving ? 'Saving…' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(deleteTarget)} onClose={() => !deleting && setDeleteTarget(null)}>
        <DialogTitle sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
          Delete {singular(resource.label)}?
        </DialogTitle>
        <DialogContent sx={{ pt: 2.5 }}>
          <Typography>This action cannot be undone.</Typography>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setDeleteTarget(null)} disabled={deleting}>
            Cancel
          </Button>
          <Button onClick={handleDelete} color="error" variant="contained" disabled={deleting}>
            {deleting ? 'Deleting…' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
