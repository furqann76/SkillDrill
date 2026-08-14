import type { ReactNode } from 'react'

/** Shared header for the dark-modernist screens: wordmark left, screen-specific content right. */
export function DmHeader({ right, onLogoClick }: { right?: ReactNode; onLogoClick?: () => void }) {
  const wordmark = (
    <div className="dm-word">
      Skill<span className="accent">Drill</span>
    </div>
  )

  return (
    <div className="dm-head">
      {onLogoClick ? (
        <button
          type="button"
          className="dm-word-btn"
          onClick={onLogoClick}
          aria-label="Go to profile picker"
        >
          {wordmark}
        </button>
      ) : (
        wordmark
      )}
      {right}
    </div>
  )
}
