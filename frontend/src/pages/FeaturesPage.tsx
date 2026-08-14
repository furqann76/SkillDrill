import { PublicFooter } from '../components/PublicFooter'
import { PublicNav } from '../components/PublicNav'
import './publicPages.css'

const FEATURES = [
  {
    title: 'AI-generated questions',
    text: 'Fresh MCQ and scenario questions generated on demand by a local LLM, per topic and difficulty.',
  },
  {
    title: 'Duplicate-free by design',
    text: 'Embedding-based similarity checks filter out near-duplicates before a new question is ever saved.',
  },
  {
    title: 'Rubric-graded scenarios',
    text: 'Open-ended answers are scored point-by-point against a rubric, with a plain-language explanation.',
  },
  {
    title: 'Per-topic analytics',
    text: 'Accuracy, attempt counts, and an MCQ/scenario breakdown for every topic you practice.',
  },
  {
    title: 'Weak-spot callouts',
    text: 'The dashboard flags topics trailing behind the rest, so the next session has a clear target.',
  },
  {
    title: 'Multiple profiles',
    text: 'Keep separate stats for separate people or separate study pushes, no accounts required.',
  },
  {
    title: 'Self-topping question bank',
    text: 'A background job keeps active topics stocked so a quiz is never blocked waiting on generation.',
  },
  {
    title: 'Admin panel',
    text: 'Manage topics, hand-author questions, or trigger AI generation in bulk from a themed admin UI.',
  },
]

export function FeaturesPage() {
  return (
    <div className="public-page">
      <PublicNav />

      <section className="public-section">
        <div className="public-section-head">
          <span className="public-eyebrow">Features</span>
          <h2>Everything the practice loop needs</h2>
          <p>No accounts, no cloud dependency, no stale question bank.</p>
        </div>

        <div className="public-feature-grid">
          {FEATURES.map((f) => (
            <div className="public-feature-card" key={f.title}>
              <h3>{f.title}</h3>
              <p>{f.text}</p>
            </div>
          ))}
        </div>
      </section>

      <PublicFooter />
    </div>
  )
}
