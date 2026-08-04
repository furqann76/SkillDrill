import { useState } from 'react'
import { api } from '../api'
import type { GradeMCQResponse, GradeScenarioResponse, Profile, QuestionOut } from '../types'

export interface QuestionResult {
  question: QuestionOut
  mcqResult?: GradeMCQResponse
  scenarioResult?: GradeScenarioResponse
}

export function QuizRunner({
  profile,
  questions,
  onFinish,
}: {
  profile: Profile
  questions: QuestionOut[]
  onFinish: (results: QuestionResult[]) => void
}) {
  const [index, setIndex] = useState(0)
  const [results, setResults] = useState<QuestionResult[]>([])
  const [selectedOption, setSelectedOption] = useState<number | null>(null)
  const [scenarioAnswer, setScenarioAnswer] = useState('')
  const [pending, setPending] = useState<QuestionResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const question = questions[index]

  async function submitAnswer() {
    setError('')
    setBusy(true)
    try {
      if (question.type === 'mcq') {
        if (selectedOption === null) return
        const result = await api.gradeMcq(profile.id, question.id, selectedOption)
        setPending({ question, mcqResult: result })
      } else {
        if (!scenarioAnswer.trim()) return
        const result = await api.gradeScenario(profile.id, question.id, scenarioAnswer)
        setPending({ question, scenarioResult: result })
      }
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  function next() {
    const updated = pending ? [...results, pending] : results
    setResults(updated)
    setPending(null)
    setSelectedOption(null)
    setScenarioAnswer('')
    if (index + 1 < questions.length) {
      setIndex(index + 1)
    } else {
      onFinish(updated)
    }
  }

  return (
    <div className="screen">
      <p className="progress">
        Question {index + 1} of {questions.length}
      </p>
      <h2>{question.question_text}</h2>

      {!pending && question.type === 'mcq' && (
        <div className="stack">
          {question.options?.map((opt, i) => (
            <label key={i} className="option">
              <input
                type="radio"
                name="option"
                checked={selectedOption === i}
                onChange={() => setSelectedOption(i)}
              />
              {opt}
            </label>
          ))}
          <button onClick={submitAnswer} disabled={busy || selectedOption === null}>
            Submit
          </button>
        </div>
      )}

      {!pending && question.type === 'scenario' && (
        <div className="stack">
          <textarea
            value={scenarioAnswer}
            onChange={(e) => setScenarioAnswer(e.target.value)}
            rows={6}
            placeholder="Type your answer…"
          />
          <button onClick={submitAnswer} disabled={busy || !scenarioAnswer.trim()}>
            {busy ? 'Grading…' : 'Submit'}
          </button>
        </div>
      )}

      {pending?.mcqResult && (
        <div className="result">
          <p className={pending.mcqResult.is_correct ? 'correct' : 'incorrect'}>
            {pending.mcqResult.is_correct ? 'Correct!' : 'Incorrect.'}
          </p>
          {!pending.mcqResult.is_correct && (
            <p>Correct answer: {question.options?.[pending.mcqResult.correct_index]}</p>
          )}
          <p>{pending.mcqResult.explanation}</p>
          <button onClick={next}>Next</button>
        </div>
      )}

      {pending?.scenarioResult && (
        <div className="result">
          <p className={pending.scenarioResult.is_correct ? 'correct' : 'incorrect'}>
            Score: {pending.scenarioResult.score.toFixed(0)}/100 —{' '}
            {pending.scenarioResult.is_correct ? 'Pass' : 'Needs work'}
          </p>
          <ul className="rubric">
            {pending.scenarioResult.rubric_breakdown.map((r, i) => (
              <li key={i} className={r.covered ? 'covered' : 'missed'}>
                {r.covered ? '✓' : '✗'} {r.point}
              </li>
            ))}
          </ul>
          <p>{pending.scenarioResult.feedback}</p>
          <p>
            <strong>Model answer:</strong> {pending.scenarioResult.model_answer}
          </p>
          <button onClick={next}>Next</button>
        </div>
      )}

      {error && <p className="error">{error}</p>}
    </div>
  )
}
