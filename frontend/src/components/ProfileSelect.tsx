import { useState } from 'react'
import { api } from '../api'
import type { Profile } from '../types'

export function ProfileSelect({
  profiles,
  onProfilesChange,
  onSelect,
}: {
  profiles: Profile[]
  onProfilesChange: (profiles: Profile[]) => void
  onSelect: (profile: Profile) => void
}) {
  const [newName, setNewName] = useState('')
  const [error, setError] = useState('')

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!newName.trim()) return
    setError('')
    try {
      const profile = await api.createProfile(newName.trim())
      onProfilesChange([...profiles, profile])
      setNewName('')
      onSelect(profile)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <div className="screen">
      <h1>Who's practicing?</h1>
      {profiles.length > 0 && (
        <ul className="profile-list">
          {profiles.map((p) => (
            <li key={p.id}>
              <button className="secondary" onClick={() => onSelect(p)}>
                <span className="profile-avatar">{p.name.charAt(0)}</span>
                {p.name}
              </button>
            </li>
          ))}
        </ul>
      )}
      <form onSubmit={handleCreate} className="stack">
        <input
          placeholder="New profile name"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
        />
        <button type="submit" disabled={!newName.trim()}>
          Create profile
        </button>
      </form>
      {error && <p className="error">{error}</p>}
    </div>
  )
}
