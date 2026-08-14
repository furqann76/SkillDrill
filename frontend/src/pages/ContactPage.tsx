import { PublicFooter } from '../components/PublicFooter'
import { PublicNav } from '../components/PublicNav'
import './publicPages.css'

export function ContactPage() {
  return (
    <div className="public-page">
      <PublicNav />

      <section className="public-section">
        <div className="public-prose">
          <span className="public-eyebrow">Contact</span>
          <h1>Get in touch</h1>
          <p>
            SkillDrill is a self-hosted practice tool -- there's no central company or support
            line behind it. Every instance is run by whoever set it up, so the right place to
            start depends on what you need.
          </p>

          <div className="public-contact-card">
            <h3 style={{ marginTop: 0 }}>Managing topics or questions?</h3>
            <p>
              That's handled from this instance's admin panel, where topics can be
              activated, deactivated, or generated in bulk.
            </p>
          </div>
        </div>
      </section>

      <PublicFooter />
    </div>
  )
}
