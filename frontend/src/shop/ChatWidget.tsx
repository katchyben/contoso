import { useEffect, useRef, useState } from 'react'
import { Box, Fab, IconButton, Paper, Stack, TextField, Typography } from '@mui/material'
import ChatBubbleOutlineOutlined from '@mui/icons-material/ChatBubbleOutlineOutlined'
import CloseOutlined from '@mui/icons-material/CloseOutlined'
import SendOutlined from '@mui/icons-material/SendOutlined'
import { API_BASE } from '../api/client'
import { getToken } from '../auth/authStore'

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

type ConnectionState = 'connecting' | 'open' | 'closed'

const WS_BASE = API_BASE.replace(/^http/, 'ws')

export function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [draft, setDraft] = useState('')
  const [status, setStatus] = useState<ConnectionState>('connecting')
  const socketRef = useRef<WebSocket | null>(null)
  const bottomRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!open) return

    const token = getToken()
    if (!token) {
      setStatus('closed')
      setMessages([{ role: 'system', content: 'Sign in to chat with support.' }])
      return
    }

    setStatus('connecting')
    const socket = new WebSocket(`${WS_BASE}/ws/chat?token=${encodeURIComponent(token)}`)
    socketRef.current = socket

    socket.onopen = () => setStatus('open')
    socket.onclose = () => setStatus('closed')
    socket.onerror = () => setStatus('closed')
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data) as ChatMessage
      setMessages((prev) => [...prev, data])
    }

    return () => {
      socket.close()
      socketRef.current = null
    }
  }, [open])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = () => {
    const text = draft.trim()
    const socket = socketRef.current
    if (!text || !socket || socket.readyState !== WebSocket.OPEN) return
    socket.send(text)
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setDraft('')
  }

  return (
    <Box sx={{ position: 'fixed', bottom: 24, right: 24, zIndex: 1300 }}>
      {open && (
        <Paper
          elevation={8}
          sx={{
            width: 320,
            height: 420,
            mb: 2,
            display: 'flex',
            flexDirection: 'column',
            border: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Box
            sx={{
              px: 2,
              py: 1.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              borderBottom: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Typography variant="h6" sx={{ fontSize: '0.8rem' }}>
              Support Chat
            </Typography>
            <IconButton size="small" onClick={() => setOpen(false)} aria-label="Close chat">
              <CloseOutlined fontSize="small" />
            </IconButton>
          </Box>

          <Stack spacing={1} sx={{ flexGrow: 1, overflowY: 'auto', p: 1.5 }}>
            {messages.length === 0 && status === 'open' && (
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                Ask about products, orders, shipping, or returns.
              </Typography>
            )}
            {messages.map((message, index) => (
              <Box
                key={index}
                data-testid={`chat-message-${message.role}`}
                sx={{
                  alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '85%',
                  bgcolor: message.role === 'user' ? 'primary.main' : 'background.default',
                  color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
                  border: message.role === 'user' ? 'none' : '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1,
                  px: 1.25,
                  py: 0.75,
                }}
              >
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </Typography>
              </Box>
            ))}
            <div ref={bottomRef} />
          </Stack>

          <Box sx={{ p: 1.5, borderTop: '1px solid', borderColor: 'divider', display: 'flex', gap: 1 }}>
            <TextField
              size="small"
              fullWidth
              placeholder={status === 'open' ? 'Type a message…' : 'Connecting…'}
              value={draft}
              disabled={status !== 'open'}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') sendMessage()
              }}
              slotProps={{ htmlInput: { 'data-testid': 'chat-input' } }}
            />
            <IconButton
              color="primary"
              onClick={sendMessage}
              disabled={status !== 'open' || !draft.trim()}
              data-testid="chat-send"
            >
              <SendOutlined fontSize="small" />
            </IconButton>
          </Box>
        </Paper>
      )}

      <Fab
        color="primary"
        onClick={() => setOpen((prev) => !prev)}
        aria-label="Toggle support chat"
        data-testid="chat-toggle"
      >
        {open ? <CloseOutlined /> : <ChatBubbleOutlineOutlined />}
      </Fab>
    </Box>
  )
}
