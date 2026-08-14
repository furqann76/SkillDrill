import { Link } from 'react-router-dom'

export function PublicFooter() {
  return (
    <footer className="public-footer">
      <div className="public-footer-inner">
        <div className="public-footer-brand">
          <span className="public-logo-dot" />
          SKILL<span className="accent">DRILL</span>
          <p>AI-graded interview practice, generated fresh and run entirely on your own machine.</p>
        </div>

        <div className="public-footer-col">
          <span className="public-footer-heading">Product</span>
          <Link to="/features">Features</Link>
          <Link to="/#topics">Topics</Link>
          <Link to="/leaderboard">Leaderboard</Link>
        </div>

        <div className="public-footer-col">
          <span className="public-footer-heading">Company</span>
          <Link to="/about">About</Link>
          <Link to="/contact">Contact</Link>
        </div>

        <div className="public-footer-col">
          <span className="public-footer-heading">Get started</span>
          <Link to="/app">Start practicing</Link>
        </div>
      </div>

      <div className="public-footer-bottom">© {new Date().getFullYear()} SkillDrill.</div>
    </footer>
  )
}
