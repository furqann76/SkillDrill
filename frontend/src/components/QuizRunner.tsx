import { useState } from 'react'
import { api } from '../api'
import type { GradeMCQResponse, GradeScenarioResponse, QuestionOut } from '../types'
import { DmHeader } from './DmHeader'
import { FormattedText } from './FormattedText'

export interface QuestionResult {
  question: QuestionOut
  mcqResult?: GradeMCQResponse
  scenarioResult?: GradeScenarioResponse
}

function pad(n: number): string {
  return String(n).padStart(2, '0')
}

export function QuizRunner({
  questions,
  onFinish,
  onGoHome,
}: {
  questions: QuestionOut[]
  onFinish: (results: QuestionResult[]) => void
  onGoHome: () => void
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
        const result = await api.gradeMcq(question.id, selectedOption)
        setPending({ question, mcqResult: result })
      } else {
        if (!scenarioAnswer.trim()) return
        const result = await api.gradeScenario(question.id, scenarioAnswer)
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
    <div className="dm-app">
      <DmHeader
        onLogoClick={onGoHome}
        right={
          <div className="dm-idx">
            Q {pad(index + 1)} / {pad(questions.length)}
          </div>
        }
      />
      <div className="dm-body">
        <div className="dm-ticks">
          {questions.map((_, i) => (
            <div key={i} className={i === index ? 'dm-tick on' : i < index ? 'dm-tick done' : 'dm-tick'} />
          ))}
        </div>

        <div className="dm-question">
          <div className="dm-qnum">{pad(index + 1)}</div>
          <p className="dm-prompt">
            <FormattedText text={question.question_text} />
          </p>
        </div>

        {!pending && question.type === 'mcq' && (
          <div className="dm-form">
            <div className="dm-options">
              {question.options?.map((opt, i) => (
                <label key={i} className={selectedOption === i ? 'dm-option selected' : 'dm-option'}>
                  <input
                    type="radio"
                    name="option"
                    checked={selectedOption === i}
                    onChange={() => setSelectedOption(i)}
                  />
                  {opt}
                </label>
              ))}
            </div>
            <button
              type="button"
              className="dm-btn"
              onClick={submitAnswer}
              disabled={busy || selectedOption === null}
            >
              Submit →
            </button>
          </div>
        )}

        {!pending && question.type === 'scenario' && (
          <div className="dm-form">
            <textarea
              className="dm-input"
              value={scenarioAnswer}
              onChange={(e) => setScenarioAnswer(e.target.value)}
              placeholder="Type your answer…"
            />
            <button
              type="button"
              className="dm-btn"
              onClick={submitAnswer}
              disabled={busy || !scenarioAnswer.trim()}
            >
              {busy ? 'Grading…' : 'Submit →'}
            </button>
          </div>
        )}

        {pending?.mcqResult && (
          <div className="dm-result">
            <p className={pending.mcqResult.is_correct ? 'dm-result-status good' : 'dm-result-status bad'}>
              {pending.mcqResult.is_correct ? 'Correct' : 'Incorrect'}
            </p>
            {!pending.mcqResult.is_correct && (
              <p className="dm-result-text">
                Correct answer: {question.options?.[pending.mcqResult.correct_index]}
              </p>
            )}
            <p className="dm-result-text">{pending.mcqResult.explanation}</p>
            <button type="button" className="dm-btn" onClick={next}>
              Next →
            </button>
          </div>
        )}

        {pending?.scenarioResult && (
          <div className="dm-result">
            <p className={pending.scenarioResult.is_correct ? 'dm-result-status good' : 'dm-result-status bad'}>
              Score: {pending.scenarioResult.score.toFixed(0)}/100 —{' '}
              {pending.scenarioResult.is_correct ? 'Pass' : 'Needs work'}
            </p>
            <div className="dm-ledger">
              {pending.scenarioResult.rubric_breakdown.map((r, i) => (
                <div key={i} className="dm-rubric-row">
                  <span className={r.covered ? 'dm-rubric-mark covered' : 'dm-rubric-mark missed'}>
                    {r.covered ? '✓' : '✗'}
                  </span>
                  <span className="dm-result-text">{r.point}</span>
                </div>
              ))}
            </div>
            <p className="dm-result-text">{pending.scenarioResult.feedback}</p>
            <p className="dm-result-text">
              <strong>Model answer:</strong> {pending.scenarioResult.model_answer}
            </p>
            <button type="button" className="dm-btn" onClick={next}>
              Next →
            </button>
          </div>
        )}

        {error && <p className="dm-error">{error}</p>}
      </div>
    </div>
  )
}
