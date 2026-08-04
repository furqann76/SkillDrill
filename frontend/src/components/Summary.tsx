import type { QuestionResult } from './QuizRunner'

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

  return (
    <div className="screen">
      <h1>Summary</h1>
      <p className="score-line">
        {correct} / {results.length} correct
      </p>
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
