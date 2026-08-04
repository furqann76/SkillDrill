import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Topic } from '../types'

export function AdminTopics({ onBack }: { onBack: () => void }) {
  const [topics, setTopics] = useState<Topic[]>([])
  const [name, setName] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  function reload() {
    setLoading(true)
    api
      .listTopics(true)
      .then(setTopics)
      .catch((err) => setError((err as Error).message))
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    setError('')
    try {
      await api.createTopic(name.trim(), displayName.trim() || undefined)
      setName('')
      setDisplayName('')
      reload()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  async function toggle(topic: Topic) {
    setError('')
    try {
      await api.setTopicActive(topic.id, !topic.is_active)
      reload()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <div className="screen">
      <h1>Manage topics</h1>
      <p>Topics generate questions on demand — inactive topics are hidden from quiz setup.</p>

      {loading && <p>Loading…</p>}

      {!loading && (
        <ul className="topic-admin-list">
          {topics.map((t) => (
            <li key={t.id}>
              <span className={t.is_active ? '' : 'muted'}>{t.display_name}</span>
              <button className="secondary" onClick={() => toggle(t)}>
                {t.is_active ? 'Deactivate' : 'Activate'}
              </button>
            </li>
          ))}
        </ul>
      )}

      <form onSubmit={handleCreate} className="stack">
        <label>
          Topic name (used internally, e.g. matches CLI generation)
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="SQL" />
        </label>
        <label>
          Display name (optional, shown in the UI)
          <input
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="SQL"
          />
        </label>
        <button type="submit" disabled={!name.trim()}>
          Add topic
        </button>
      </form>
      {error && <p className="error">{error}</p>}

      <button className="secondary" onClick={onBack} style={{ marginTop: 20 }}>
        Back
      </button>
    </div>
  )
}
