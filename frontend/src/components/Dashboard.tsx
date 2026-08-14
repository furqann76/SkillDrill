import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Profile, TopicStats } from '../types'
import { DmHeader } from './DmHeader'

function fmtPct(v: number | null): string {
  return v === null ? '—' : `${Math.round(v)}%`
}

function BarRow({ stat, isWeak }: { stat: TopicStats; isWeak: boolean }) {
  const pct = stat.accuracy_pct ?? 0
  const color = isWeak ? 'var(--status-critical)' : 'var(--status-good)'

  const breakdown: string[] = []
  if (stat.mcq_accuracy_pct !== null) breakdown.push(`MCQ ${fmtPct(stat.mcq_accuracy_pct)}`)
  if (stat.scenario_accuracy_pct !== null) {
    breakdown.push(`Scenario ${fmtPct(stat.scenario_accuracy_pct)}`)
  }

  return (
    <div className="bar-row">
      <div className="bar-row-header">
        <span className="bar-label">{stat.display_name}</span>
        <span className="bar-value">{fmtPct(stat.accuracy_pct)}</span>
      </div>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <div className="bar-meta">
        {stat.total_attempts} attempt{stat.total_attempts === 1 ? '' : 's'}
        {breakdown.length > 0 && ` · ${breakdown.join(' · ')}`}
      </div>
    </div>
  )
}

export function Dashboard({
  profile,
  onBack,
  onGoHome,
  onLogout,
}: {
  profile: Profile
  onBack: () => void
  onGoHome: () => void
  onLogout: () => void
}) {
  const [topics, setTopics] = useState<TopicStats[]>([])
  const [weak, setWeak] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .getAnalytics()
      .then((res) => {
        setTopics(res.topics)
        setWeak(res.weak_topics)
      })
      .catch((err) => setError((err as Error).message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="dm-app">
      <DmHeader
        onLogoClick={onGoHome}
        right={
          <div className="dm-nav">
            <button type="button" onClick={onBack}>
              Setup
            </button>
            <button type="button" onClick={onLogout}>
              Log out
            </button>
          </div>
        }
      />
      <div className="dm-body">
        <h2>Progress</h2>
        <p className="dm-label">{profile.name}'s performance by topic</p>

        {loading && <p>Loading…</p>}
        {error && <p className="dm-error">{error}</p>}

        {!loading && !error && topics.length === 0 && (
          <p>No quiz attempts yet — take a quiz to see your progress here.</p>
        )}

        {weak.length > 0 && (
          <div className="weak-banner">
            <strong>⚠ Weak topics:</strong> {weak.join(', ')} — worth another round.
          </div>
        )}

        {topics.length > 0 && (
          <>
            <div className="stack" style={{ marginTop: 4 }}>
              {topics.map((t) => (
                <BarRow key={t.topic} stat={t} isWeak={weak.includes(t.display_name)} />
              ))}
            </div>

            <table className="stats-table">
              <thead>
                <tr>
                  <th>Topic</th>
                  <th>Attempts</th>
                  <th>Accuracy</th>
                  <th>MCQ</th>
                  <th>Scenario</th>
                </tr>
              </thead>
              <tbody>
                {topics.map((t) => (
                  <tr key={t.topic}>
                    <td>{t.display_name}</td>
                    <td>{t.total_attempts}</td>
                    <td>{fmtPct(t.accuracy_pct)}</td>
                    <td>{fmtPct(t.mcq_accuracy_pct)}</td>
                    <td>{fmtPct(t.scenario_accuracy_pct)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </div>
    </div>
  )
}
