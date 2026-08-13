import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Profile, QuestionOut, Topic } from '../types'
import { DmHeader } from './DmHeader'

export function QuizSetup({
  profile,
  onStart,
  onViewDashboard,
  onManageTopics,
}: {
  profile: Profile
  onStart: (questions: QuestionOut[]) => void
  onViewDashboard: () => void
  onManageTopics: () => void
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
      if (t.length > 0) setTopic(t[0].name)
    })
  }, [])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      const res = await api.startQuiz(profile.id, topic, difficulty, count)
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
        right={
          <div className="dm-nav">
            <button type="button" onClick={onViewDashboard}>
              Progress
            </button>
            <button type="button" onClick={onManageTopics}>
              Topics
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
