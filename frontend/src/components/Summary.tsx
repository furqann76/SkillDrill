import { DmHeader } from './DmHeader'
import { LedgerRow } from './LedgerRow'
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
  const missed = results.filter((r) => !(r.mcqResult?.is_correct || r.scenarioResult?.is_correct))

  return (
    <div className="dm-app">
      <DmHeader right={<div className="dm-idx">Summary</div>} />
      <div className="dm-body">
        <p className="dm-score">
          {pad(correct)}
          <span className="dm-score-suffix">
            {' / '}
            {pad(results.length)}
          </span>
        </p>
        <p className="dm-feedback">{celebrationMessage(pct)}</p>

        {missed.length > 0 && (
          <div className="dm-ledger">
            {missed.map((r, i) => (
              <LedgerRow
                key={i}
                index={i + 1}
                indexAccent
                main={<span className="dm-row-text">{r.question.question_text.slice(0, 80)}</span>}
                trailing={
                  <span className="dm-row-score">
                    {r.scenarioResult ? `${r.scenarioResult.score.toFixed(0)}/100` : 'Missed'}
                  </span>
                }
              />
            ))}
          </div>
        )}

        <button type="button" className="dm-btn" onClick={onRestart}>
          Take another quiz →
        </button>
      </div>
    </div>
  )
}

function pad(n: number): string {
  return String(n).padStart(2, '0')
}
