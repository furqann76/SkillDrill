import { useState } from 'react'
import { api } from '../api'

export function Login({ onSuccess }: { onSuccess: () => void }) {
  const [pin, setPin] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      await api.login(pin)
      onSuccess()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="screen">
      <h1>SkillDrill</h1>
      <p>Enter your PIN to continue.</p>
      <form onSubmit={handleSubmit} className="stack">
        <input
          type="password"
          placeholder="PIN"
          value={pin}
          onChange={(e) => setPin(e.target.value)}
          autoFocus
        />
        <button type="submit" disabled={busy || !pin}>
          Enter
        </button>
      </form>
      {error && <p className="error">{error}</p>}
    </div>
  )
}
