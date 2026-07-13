import { useEffect, useState } from 'react'
import './App.css'

const API_BASE = 'http://127.0.0.1:8000'

function App() {
  const [name, setName] = useState('World')
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetch(`${API_BASE}/`)
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch(() => setMessage('Could not reach backend'))
  }, [])

  const sayHello = async () => {
    const res = await fetch(`${API_BASE}/hello/${encodeURIComponent(name)}`)
    const data = await res.json()
    setMessage(data.message)
  }

  return (
    <section id="center">
      <h1>{message}</h1>
      <input value={name} onChange={(e) => setName(e.target.value)} />
      <button type="button" onClick={sayHello}>
        Say hello
      </button>
    </section>
  )
}

export default App