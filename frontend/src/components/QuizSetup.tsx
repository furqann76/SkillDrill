import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Profile, QuestionOut, Topic } from '../types'

export function QuizSetup({
  profile,
  onStart,
}: {
  profile: Profile
  onStart: (questions: QuestionOut[]) => void
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
            `"python -m app.generate_cli --topic ${topic} --difficulty ${difficulty}".`,
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
    <div className="screen">
      <h1>Start a quiz</h1>
      <p>Practicing as {profile.name}</p>
      <form onSubmit={handleSubmit} className="stack">
        <label>
          Topic
          <select value={topic} onChange={(e) => setTopic(e.target.value)}>
            {topics.map((t) => (
              <option key={t.id} value={t.name}>
                {t.display_name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Difficulty
          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            <option value="basic">Basic</option>
            <option value="mid">Mid</option>
          </select>
        </label>
        <label>
          Question count
          <input
            type="number"
            min={1}
            max={50}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
          />
        </label>
        <button type="submit" disabled={busy || !topic}>
          {busy ? 'Loading…' : 'Start quiz'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
    </div>
  )
}
