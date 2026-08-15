import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Profile, QuestionOut, Topic } from '../types'
import { DmHeader } from './DmHeader'

export function QuizSetup({
  profile,
  initialTopic,
  onStart,
  onViewDashboard,
  onGoHome,
  onLogout,
}: {
  profile: Profile
  initialTopic?: string
  onStart: (questions: QuestionOut[]) => void
  onViewDashboard: () => void
  onGoHome: () => void
  onLogout: () => void
}) {
  const [topics, setTopics] = useState<Topic[]>([])
  const [topic, setTopic] = useState('')
  const [difficulty, setDifficulty] = useState('basic')
  const [count, setCount] = useState(5)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.listTopics().then((t) => {
      setTopics(t)
      const preferred = initialTopic || profile.preferred_topic
      const match = preferred && t.some((x) => x.name === preferred) ? preferred : t[0]?.name
      if (match) setTopic(match)
    })
    // Runs once on mount to pick the initial topic; initialTopic/preferred_topic
    // are read at that moment on purpose, not tracked for later changes.
    // oxlint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      const res = await api.startQuiz(topic, difficulty, count)
      if (res.available === 0) {
        setError(
          `No ${difficulty} questions for ${topic} yet. Generate some first with ` +
            `"python manage.py generate_questions --topic ${topic} --difficulty ${difficulty}".`,
        )
        return
      }
      onStart(res.questions)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="dm-app">
      <DmHeader
        onLogoClick={onGoHome}
        right={
          <div className="dm-nav">
            <button type="button" onClick={onViewDashboard}>
              Progress
            </button>
            <button type="button" onClick={onLogout}>
              Log out
            </button>
          </div>
        }
      />
      <div className="dm-body">
        <h2>Start a quiz</h2>
        <p className="dm-label">Practicing as {profile.name}</p>

        <form onSubmit={handleSubmit} className="dm-form">
          <div className="dm-field">
            <label>Topic</label>
            <select className="dm-input" value={topic} onChange={(e) => setTopic(e.target.value)}>
              {topics.map((t) => (
                <option key={t.id} value={t.name}>
                  {t.display_name}
                </option>
              ))}
            </select>
          </div>
          <div className="dm-field">
            <label>Difficulty</label>
            <select
              className="dm-input"
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
            >
              <option value="basic">Basic</option>
              <option value="mid">Mid</option>
            </select>
          </div>
          <div className="dm-field">
            <label>Question count</label>
            <input
              className="dm-input"
              type="number"
              min={1}
              max={50}
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
            />
          </div>
          <button type="submit" className="dm-btn" disabled={busy || !topic}>
            {busy ? 'Loading…' : 'Start quiz →'}
          </button>
        </form>

        {error && <p className="dm-error">{error}</p>}
      </div>
    </div>
  )
}
