import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { PublicFooter } from '../components/PublicFooter'
import { PublicNav } from '../components/PublicNav'
import type { LeaderboardEntry, PublicTopic } from '../types'
import './publicPages.css'

const STEPS = [
  {
    title: 'Pick a profile',
    text: 'Practice as yourself, or spin up a fresh profile to track a clean set of stats.',
  },
  {
    title: 'Choose a topic & difficulty',
    text: 'Python, Git, HTML5, databases, and more -- basic or mid-level, however many questions you want.',
  },
  {
    title: 'Answer AI-graded questions',
    text: 'Multiple-choice and open-ended scenario questions, graded instantly against a rubric.',
  },
  {
    title: 'Track your progress',
    text: 'Accuracy by topic, weak-spot callouts, and a leaderboard that rewards consistency.',
  },
]

export function LandingPage() {
  const navigate = useNavigate()
  const [topics, setTopics] = useState<PublicTopic[]>([])
  const [leaders, setLeaders] = useState<LeaderboardEntry[]>([])

  useEffect(() => {
    api.publicTopics().then(setTopics).catch(() => setTopics([]))
    api.publicLeaderboard(3).then(setLeaders).catch(() => setLeaders([]))
  }, [])

  return (
    <div className="public-page">
      <PublicNav />

      <section className="public-hero">
        <div>
          <div className="public-badges">
            {(topics.length > 0
              ? topics.map((t) => t.display_name)
              : ['Python', 'Git', 'HTML5', 'Database']
            ).map((name) => (
              <span key={name} className="public-badge">
                {name}
              </span>
            ))}
          </div>
          <h1>
            YOUR JOURNEY TO <span className="accent">MASTERY</span> STARTS HERE
          </h1>
          <p className="public-hero-sub">
            SkillDrill generates fresh, AI-graded interview questions on demand and tracks exactly
            where you're strong and where you're not -- all running locally, no two quizzes ever
            quite the same.
          </p>
          <div className="public-hero-actions">
            <button type="button" className="public-btn-primary" onClick={() => navigate('/app')}>
              Start Learning
            </button>
            <a href="#how-it-works" className="public-link-secondary">
              See how it works →
            </a>
          </div>
        </div>

        <div className="public-hero-visual">
          <div className="public-crystal">
            <div className="public-crystal-face" />
            <div className="public-crystal-face small" />
            <div className="public-crystal-face tiny" />
          </div>
        </div>
      </section>

      <section className="public-section" id="topics">
        <div className="public-section-head">
          <span className="public-eyebrow">Featured topics</span>
          <h2>Practice what's actually on the interview</h2>
          <p>Every topic is backed by a growing, deduplicated question bank.</p>
        </div>
        <div className="public-topics-grid">
          {(topics.length > 0
            ? topics
            : [
                { id: -1, name: 'python', display_name: 'Python' },
                { id: -2, name: 'git', display_name: 'Git' },
                { id: -3, name: 'html5', display_name: 'HTML5' },
                { id: -4, name: 'database', display_name: 'Database' },
              ]
          ).map((t) => (
            <div className="public-topic-card" key={t.id}>
              <h3>{t.display_name}</h3>
              <p>MCQ &amp; scenario questions, basic through mid-level.</p>
            </div>
          ))}
        </div>
      </section>

      <section className="public-section">
        <div className="public-section-head">
          <span className="public-eyebrow">Leaderboard</span>
          <h2>Top performers this season</h2>
          <p>Ranked by accuracy across at least 5 attempts.</p>
        </div>

        {leaders.length === 0 ? (
          <p className="public-empty">
            The leaderboard opens up once a few profiles have played some rounds -- be the first.
          </p>
        ) : (
          <div className="public-leaderboard-list">
            {leaders.map((entry) => (
              <div className="public-leaderboard-row" key={entry.rank}>
                <span className="public-leaderboard-rank">#{entry.rank}</span>
                <span className="public-leaderboard-name">{entry.name}</span>
                <span className="public-leaderboard-meta">{entry.total_attempts} attempts</span>
                <span className="public-leaderboard-accuracy">{entry.accuracy_pct}%</span>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="public-section" id="how-it-works">
        <div className="public-section-head">
          <span className="public-eyebrow">How it works</span>
          <h2>From zero to graded in four steps</h2>
        </div>
        <div className="public-steps">
          {STEPS.map((step, i) => (
            <div className="public-step" key={step.title}>
              <div className="public-step-num">{String(i + 1).padStart(2, '0')}</div>
              <h3>{step.title}</h3>
              <p>{step.text}</p>
            </div>
          ))}
        </div>
      </section>

      <PublicFooter />
    </div>
  )
}
