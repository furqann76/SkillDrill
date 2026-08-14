import { useEffect, useState } from 'react'
import { api } from '../api'
import { PublicFooter } from '../components/PublicFooter'
import { PublicNav } from '../components/PublicNav'
import type { LeaderboardEntry } from '../types'
import './publicPages.css'

export function LeaderboardPage() {
  const [leaders, setLeaders] = useState<LeaderboardEntry[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .publicLeaderboard()
      .then(setLeaders)
      .catch(() => setLeaders([]))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="public-page">
      <PublicNav />

      <section className="public-section">
        <div className="public-section-head">
          <span className="public-eyebrow">Leaderboard</span>
          <h2>Ranked by accuracy</h2>
          <p>
            Every profile with at least 5 graded attempts, ranked by overall accuracy. Ties break
            in favor of whoever has answered more questions.
          </p>
        </div>

        {loading && <p className="public-empty">Loading…</p>}

        {!loading && leaders.length === 0 && (
          <p className="public-empty">
            Nobody qualifies yet -- take a few quizzes to put your name on the board.
          </p>
        )}

        {!loading && leaders.length > 0 && (
          <div className="public-leaderboard-list">
            {leaders.map((entry) => (
              <div className="public-leaderboard-row" key={entry.rank}>
                <span className="public-leaderboard-rank">#{entry.rank}</span>
                <span className="public-leaderboard-name">{entry.name}</span>
                <span className="public-leaderboard-meta">{entry.total_attempts} attempts</span>
                <span className="public-leaderboard-accuracy">{entry.accuracy_pct}%</span>
              </div>
            ))}
          </div>
        )}
      </section>

      <PublicFooter />
    </div>
  )
}
