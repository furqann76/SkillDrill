import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Profile, PublicTopic } from '../types'

type Mode = 'login' | 'signup'

export function AuthPage({
  initialTopic,
  onSuccess,
}: {
  initialTopic?: string
  onSuccess: (profile: Profile) => void
}) {
  const [mode, setMode] = useState<Mode>('login')
  const [topics, setTopics] = useState<PublicTopic[]>([])
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const [identifier, setIdentifier] = useState('')
  const [remember, setRemember] = useState(true)

  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [preferredTopic, setPreferredTopic] = useState(initialTopic || '')

  useEffect(() => {
    api
      .publicTopics()
      .then(setTopics)
      .catch(() => setTopics([]))
  }, [])

  function switchMode(next: Mode) {
    setMode(next)
    setError('')
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      const res = await api.login(identifier, password, remember)
      if (res.profile) onSuccess(res.profile)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }
    setBusy(true)
    try {
      const res = await api.signup(username, email, password, confirmPassword, preferredTopic)
      if (res.profile) onSuccess(res.profile)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="hero-screen auth-screen">
      <div className="auth-brand">
        <h1>SkillDrill</h1>
        <p>Master CS concepts daily.</p>
      </div>

      <div className="auth-tabs">
        <button
          type="button"
          className={mode === 'login' ? 'auth-tab active' : 'auth-tab'}
          onClick={() => switchMode('login')}
        >
          Log in
        </button>
        <button
          type="button"
          className={mode === 'signup' ? 'auth-tab active' : 'auth-tab'}
          onClick={() => switchMode('signup')}
        >
          Sign up
        </button>
      </div>

      {mode === 'login' ? (
        <form onSubmit={handleLogin} className="stack">
          <input
            placeholder="Email or username"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            autoFocus
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <div className="auth-row">
            <label className="auth-checkbox">
              <input
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
              />
              Remember me
            </label>
            <span className="auth-inert-link" title="Not available yet">
              Forgot password?
            </span>
          </div>
          <button type="submit" disabled={busy || !identifier || !password}>
            {busy ? 'Logging in…' : 'Log in →'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleSignup} className="stack">
          <input
            placeholder="Full name / username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
          />
          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <input
            type="password"
            placeholder="Confirm password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
          <select value={preferredTopic} onChange={(e) => setPreferredTopic(e.target.value)}>
            <option value="">Primary goal / focus area (optional)</option>
            {topics.map((t) => (
              <option key={t.id} value={t.name}>
                {t.display_name}
              </option>
            ))}
          </select>
          <button
            type="submit"
            disabled={busy || !username || !email || !password || !confirmPassword}
          >
            {busy ? 'Creating account…' : 'Create account →'}
          </button>
        </form>
      )}

      <div className="auth-social">
        <button type="button" className="secondary" disabled title="Coming soon">
          Continue with GitHub
        </button>
        <button type="button" className="secondary" disabled title="Coming soon">
          Continue with Google
        </button>
      </div>

      {error && <p className="error">{error}</p>}
    </div>
  )
}
