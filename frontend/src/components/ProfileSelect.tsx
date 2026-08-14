import { useState } from 'react'
import { api } from '../api'
import type { Profile } from '../types'
import { DmHeader } from './DmHeader'
import { LedgerRow } from './LedgerRow'

export function ProfileSelect({
  profiles,
  onProfilesChange,
  onSelect,
  onGoHome,
}: {
  profiles: Profile[]
  onProfilesChange: (profiles: Profile[]) => void
  onSelect: (profile: Profile) => void
  onGoHome: () => void
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
    <div className="dm-app">
      <DmHeader onLogoClick={onGoHome} />
      <div className="dm-body">
        <h2>Who's practicing?</h2>

        {profiles.length > 0 && (
          <div className="dm-ledger">
            {profiles.map((p, i) => (
              <LedgerRow
                key={p.id}
                index={i + 1}
                main={<span className="dm-row-name">{p.name}</span>}
                trailing={<span className="dm-row-arrow">→</span>}
                onClick={() => onSelect(p)}
              />
            ))}
          </div>
        )}

        <form onSubmit={handleCreate} className="dm-form">
          <div className="dm-field">
            <label>New profile</label>
            <input
              className="dm-input"
              placeholder="Profile name"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
            />
          </div>
          <button type="submit" className="dm-btn" disabled={!newName.trim()}>
            Create profile →
          </button>
        </form>

        {error && <p className="dm-error">{error}</p>}
      </div>
    </div>
  )
}
