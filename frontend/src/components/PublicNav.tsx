import { Link, useNavigate } from 'react-router-dom'

export function PublicNav() {
  const navigate = useNavigate()

  return (
    <header className="public-nav">
      <div className="public-nav-inner">
        <Link to="/" className="public-logo">
          <span className="public-logo-dot" />
          SKILL<span className="accent">DRILL</span>
        </Link>

        <nav className="public-nav-links">
          <Link to="/leaderboard">Leaderboard</Link>
          <Link to="/about">About</Link>
          <Link to="/#topics">Topics</Link>
          <Link to="/features">Features</Link>
          <Link to="/contact">Contact</Link>
        </nav>

        <button type="button" className="public-cta-ghost" onClick={() => navigate('/app')}>
          Login / Start Practicing
        </button>
      </div>
    </header>
  )
}
