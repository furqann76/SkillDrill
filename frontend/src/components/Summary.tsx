import type { QuestionResult } from './QuizRunner'

function celebrationMessage(pct: number): string {
  if (pct === 100) return "Perfect score — you're crushing it."
  if (pct >= 80) return 'Great run — almost there.'
  if (pct >= 50) return 'Solid effort — a bit more practice and you’ve got it.'
  return "Rough one — let's drill this topic again."
}

export function Summary({
  results,
  onRestart,
}: {
  results: QuestionResult[]
  onRestart: () => void
}) {
  const correct = results.filter(
    (r) => r.mcqResult?.is_correct || r.scenarioResult?.is_correct,
  ).length
  const pct = results.length > 0 ? Math.round((correct / results.length) * 100) : 0

  return (
    <div className="hero-screen">
      <h1>Summary</h1>
      <p className="score-hero">
        {correct}/{results.length}
      </p>
      <p className="score-hero-sub">{celebrationMessage(pct)}</p>
      <ul className="summary-list">
        {results.map((r, i) => (
          <li key={i} className={r.mcqResult?.is_correct || r.scenarioResult?.is_correct ? 'covered' : 'missed'}>
            {r.mcqResult?.is_correct || r.scenarioResult?.is_correct ? '✓' : '✗'}{' '}
            {r.question.question_text.slice(0, 80)}
            {r.scenarioResult && ` (${r.scenarioResult.score.toFixed(0)}/100)`}
          </li>
        ))}
      </ul>
      <button onClick={onRestart}>Take another quiz</button>
    </div>
  )
}
