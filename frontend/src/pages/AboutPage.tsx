import { PublicFooter } from '../components/PublicFooter'
import { PublicNav } from '../components/PublicNav'
import './publicPages.css'

export function AboutPage() {
  return (
    <div className="public-page">
      <PublicNav />

      <section className="public-section">
        <div className="public-prose">
          <span className="public-eyebrow">About</span>
          <h1>
            Practice that doesn't run out of <span className="accent">questions</span>
          </h1>
          <p>
            SkillDrill is a local-first interview practice engine. Instead of drawing from a
            fixed bank of stale questions, it generates fresh multiple-choice and open-ended
            scenario questions on demand using a locally-run language model -- so the question
            bank keeps growing the more it's used, without ever needing a cloud API key.
          </p>
          <p>
            Every generated question is checked against everything already in the bank using
            embedding-based similarity, so near-duplicates get filtered out before they're saved.
            Scenario answers are graded against a rubric by the same local model, with a
            breakdown of exactly which points were covered.
          </p>

          <h3>How it's built</h3>
          <p>
            The backend is Django + Django REST Framework over SQLite, with a background job that
            tops up the question bank for active topics automatically. The frontend is React and
            TypeScript. Generation and grading run against Qwen2.5 through a local Ollama
            instance -- nothing about a practice session leaves your machine.
          </p>

          <h3>Why it exists</h3>
          <p>
            Repeating the same twenty questions doesn't build real fluency. SkillDrill trades a
            hand-curated question set for one that regenerates itself, paired with per-topic
            accuracy tracking so it's obvious where another round is actually worth your time.
          </p>
        </div>
      </section>

      <PublicFooter />
    </div>
  )
}
